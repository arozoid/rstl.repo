#!/usr/bin/env bash
# pkg2rpm.sh <pkg.tar.*> [outdir]
#
# Convert one finished rstl.repo pacman package into an RPM. Name, version,
# license, file list and dependencies are read from the package itself, so
# the RPM always matches the Arch package CI just built (auto-versioning and
# pkgrel bumping come for free).
#
# Arch dependency names are mapped to their Fedora equivalents; packages built
# by this repo keep their name unchanged so in-repo deps resolve inside the
# dnf repo too.
#
# RPMBUILD=<path> can override the rpmbuild binary (used for local testing).
set -euo pipefail

src=${1:?usage: pkg2rpm.sh <pkg.tar.zst> [outdir]}
outdir=${2:-.}
root="$(cd "$(dirname "$0")/../.." && pwd)"
rpmbuild_bin=${RPMBUILD:-rpmbuild}
mkdir -p "$outdir"

# names built by this repo — never remapped
declare -A inrepo=()
for d in "$root"/pkgbuilds/*/; do
  n=$(bash -c '. "$1"; printf "%s" "${pkgname:-}"' bash "$d/PKGBUILD" 2>/dev/null || true)
  [ -n "${n:-}" ] && inrepo["$n"]=1
done

# arch -> fedora package names (space separated for 1:many mappings)
declare -A map=(
  [awk]=gawk
  [sh]=bash
  [gcc-libs]='libstdc++'
  [libinih]=inih
  [libpipewire]=pipewire-libs
  [libpipewire-0.3.so]=pipewire-libs
  [libpulse]=pulseaudio-libs
  [librsvg]=librsvg2
  [libudev.so]=systemd-libs
  [libx11]=libX11
  [libxcursor]=libXcursor
  [libxi]=libXi
  [openssl]=openssl-libs
  [python-attrs]=python3-attrs
  [python-httpx]=python3-httpx
  [python-numpy]=python3-numpy
  [python-pillow]=python3-pillow
  [python-pip]=python3-pip
  [python-pylast]=python3-pylast
  [python-pyperclip]=python3-pyperclip
  [python-requests]=python3-requests
  [python-toml]=python-toml
  [python-yaml]=python3-pyyaml
  [vulkan-icd-loader]=vulkan-loader
  [wayland]='libwayland-client libwayland-cursor libwayland-egl'
  [wayland-protocols]=wayland-protocols-devel
  [zlib]=zlib-ng-compat
)

# name [+version constraint] -> fedora name(s) [+same constraint], one per line
map_dep() {
  local spec=$1 name rest t
  name=${spec%%[<>=]*}
  rest=${spec#"$name"}
  local targets=${map[$name]:-$name}
  if [ -n "${inrepo[$name]:-}" ]; then targets=$name; fi
  for t in $targets; do printf '%s%s\n' "$t" "$rest"; done
}

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/root" "$work/top"
if command -v bsdtar >/dev/null 2>&1; then
  bsdtar -xf "$src" -C "$work/root"
else
  tar -xf "$src" -C "$work/root"
fi

gi="$work/root/.PKGINFO"
[ -f "$gi" ] || { echo "pkg2rpm: no .PKGINFO in $src" >&2; exit 1; }

get() { sed -n "s/^$1 = //p" "$gi" | head -n1; }

pkgname=$(get pkgname)
pkgverfull=$(get pkgver)
pkgdesc=$(get pkgdesc)
urlv=$(get url)
archv=$(get arch)

epoch=''
rel=${pkgverfull##*-}
ver=${pkgverfull%-*}
if [[ $ver == *:* ]]; then epoch=${ver%%:*}; ver=${ver#*:}; fi

mapfile -t depends < <(sed -n 's/^depend = //p' "$gi")
mapfile -t optdeps < <(sed -n 's/^optdepend = //p' "$gi")
mapfile -t licenses < <(sed -n 's/^license = //p' "$gi")
mapfile -t provides < <(sed -n 's/^provides = //p' "$gi")
mapfile -t conflicts < <(sed -n 's/^conflict = //p' "$gi")
mapfile -t replaces < <(sed -n 's/^replaces = //p' "$gi")

# description / license join
summary=$pkgdesc
license=Unknown
if [ "${#licenses[@]}" -gt 0 ]; then
  license=$(printf '%s AND ' "${licenses[@]}")
  license=${license% AND }
fi

requires=()
for d in "${depends[@]:-}"; do
  [ -n "$d" ] || continue
  while IFS= read -r m; do requires+=("$m"); done < <(map_dep "$d")
done
mapfile -t requires < <(printf '%s\n' "${requires[@]:-}" | sed '/^$/d' | sort -u)

suggests=()
for o in "${optdeps[@]:-}"; do
  [ -n "$o" ] || continue
  on=${o%%:*}
  while IFS= read -r m; do suggests+=("$m"); done < <(map_dep "$on")
done
mapfile -t suggests < <(printf '%s\n' "${suggests[@]:-}" | sed '/^$/d' | sort -u)

provides_m=()
for p in "${provides[@]:-}"; do
  [ -n "$p" ] || continue
  while IFS= read -r m; do provides_m+=("$m"); done < <(map_dep "$p")
done

conflicts_m=()
for c in "${conflicts[@]:-}"; do
  [ -n "$c" ] || continue
  while IFS= read -r m; do conflicts_m+=("$m"); done < <(map_dep "$c")
done

obsoletes_m=()
for r in "${replaces[@]:-}"; do
  [ -n "$r" ] || continue
  while IFS= read -r m; do obsoletes_m+=("$m"); done < <(map_dep "$r")
done

# file list: every entry except root-level pacman metadata (.PKGINFO, .MTREE, …)
files_list=$work/files
: > "$files_list"
while IFS= read -r f; do
  f=${f%/}
  [ -n "$f" ] || continue
  case $f in .*) continue ;; esac
  # Only include actual files, not directories
  if [ -f "$work/root/$f" ]; then
    esc=${f//\\/\\\\}
    esc=${esc//\[/\\[}
    esc=${esc//\?/\\?}
    esc=${esc//\*/\\*}
    printf '/%s\n' "$esc" >> "$files_list"
  fi
done < <(if command -v bsdtar >/dev/null 2>&1; then bsdtar -tf "$src"; else tar -tf "$src"; fi | sed 's|^\./||')
sort -o "$files_list" "$files_list"

# Detect whether the package contains ELF binaries to set BuildArch correctly.
# Arch packages marked "any" may still ship compiled binaries.
rpmarch=noarch
if [ -n "$(find "$work/root" -type f -exec file {} + 2>/dev/null | grep -E 'ELF.*executable|ELF.*shared object' | head -1)" ]; then
  rpmarch=x86_64
elif [ "$archv" != "any" ]; then
  rpmarch=$archv
fi

spec=$work/$pkgname.spec
{
  echo "Name:           $pkgname"
  echo "Version:        $ver"
  [ -n "$epoch" ] && echo "Epoch:          $epoch"
  echo "Release:        $rel"
  echo "Summary:        $summary"
  echo "License:        $license"
  [ -n "$urlv" ] && echo "URL:            $urlv"
  echo "BuildArch:      $rpmarch"
  # metadata is mapped explicitly from the pacman package — no ELF/python
  # autodetection, and no brp post-processing of already-built Arch binaries
  echo "AutoReq:        no"
  echo "AutoProv:       no"
  for r in "${requires[@]:-}"; do [ -n "$r" ] && echo "Requires:       $r"; done
  for s in "${suggests[@]:-}"; do [ -n "$s" ] && echo "Suggests:       $s"; done
  for p in "${provides_m[@]:-}"; do [ -n "$p" ] && echo "Provides:       $p"; done
  for c in "${conflicts_m[@]:-}"; do [ -n "$c" ] && echo "Conflicts:      $c"; done
  for o in "${obsoletes_m[@]:-}"; do [ -n "$o" ] && echo "Obsoletes:      $o"; done
  echo
  echo '%global __os_install_post %{nil}'
  echo '%global debug_package %{nil}'
  echo
  echo '%description'
  echo "$summary"
  echo
  echo '%install'
  echo 'mkdir -p %{buildroot}'
  echo "cp -a $work/root/. %{buildroot}/"
  echo "find %{buildroot} -maxdepth 1 -name '.*' -exec rm -rf {} +"
  echo
  echo '%files'
  cat "$files_list"
} > "$spec"

"$rpmbuild_bin" -bb "$spec" \
  --define "_topdir $work/top" \
  --define 'debug_package %{nil}' \
  --define '__os_install_post %{nil}' >/dev/null || {
    echo "pkg2rpm: rpmbuild failed for $pkgname" >&2
    sed 's/^/  /' "$spec" >&2
    exit 1
  }

mv "$work"/top/RPMS/*/*.rpm "$outdir"/
echo "pkg2rpm: $pkgname-$ver-$rel -> $outdir/"
