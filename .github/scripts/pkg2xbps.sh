#!/usr/bin/env bash
# pkg2xbps.sh <pkg.tar.*> [outdir] [names-file]
#
# Convert one finished rstl.repo pacman package into an XBPS package. Name,
# version, license, file list and dependencies are read from the package itself,
# so the .xbps always matches the Arch package CI just built (auto-versioning
# and pkgrel bumping come for free).
#
# Arch dependency names are mapped to their Void equivalents; packages built by
# this repo keep their name unchanged so in-repo deps resolve inside the xbps
# repository too.
#
# Requires xbps-create (package `xbps` on Void Linux).
set -euo pipefail

src=${1:?usage: pkg2xbps.sh <pkg.tar.zst> [outdir] [names-file]}
outdir=${2:-.}
names_file=${3:-}
root="$(cd "$(dirname "$0")/../.." && pwd)"

command -v xbps-create >/dev/null 2>&1 || {
  echo "pkg2xbps: xbps-create not found (install the 'xbps' package)" >&2
  exit 1
}
mkdir -p "$outdir"

# names built by this repo — never remapped
declare -A inrepo=()
for d in "$root"/pkgbuilds/*/; do
  n=$(bash -c '. "$1"; printf "%s" "${pkgname:-}"' bash "$d/PKGBUILD" 2>/dev/null || true)
  [ -n "${n:-}" ] && inrepo["$n"]=1
done

# arch -> void package names (space separated for 1:many mappings)
declare -A map=(
  [awk]=gawk
  [sh]=bash
  [freetype2]=freetype
  [gcc-libs]='libgcc libstdc++'
  [libegl]=libglvnd
  [libgl]=libglvnd
  [libinih]=inih
  [libpipewire]=libpipewire
  [libpipewire-0.3.so]=libpipewire
  [libpulse]=libpulseaudio
  [libudev.so]=eudev-libudev
  [libx11]=libX11
  [libxcursor]=libXcursor
  [libxi]=libXi
  [bluez-libs]=libbluetooth
  [bluez-utils]=bluez
  [networkmanager]=NetworkManager
  [openssl]=openssl
  [pipewire-alsa]=alsa-pipewire
  [pipewire-pulse]=pipewire
  [greetd-tuigreet]=tuigreet
  [xorg-xwayland]=xorg-server-xwayland
  [python-attrs]=python3-attrs
  [python-httpx]=python3-httpx
  [python-numpy]=python3-numpy
  [python-pillow]=python3-Pillow
  [python-pip]=python3-pip
  [python-pylast]=python3-pylast
  [python-pyperclip]=python3-pyperclip
  [python-requests]=python3-requests
  [python-toml]=python3-toml
  [python-yaml]=python3-yaml
  [vulkan-icd-loader]=vulkan-loader
  [wayland]=wayland
  [zlib]=zlib
)

# Arch pkgver ("1.2.3-4", optionally "2:1.2.3-4") -> XBPS pkgver ("1.2.3_4").
# XBPS has no epochs; the epoch is dropped. Anything outside the XBPS version
# character set is replaced with an underscore instead of failing xbps-create.
void_version() {
  local v=$1 base rel
  case $v in *:*) v=${v#*:} ;; esac
  if [[ $v == *-* ]]; then
    base=${v%-*}
    rel=${v##*-}
    v="${base}_${rel}"
  else
    v="${v}_1"
  fi
  printf '%s' "$v" | tr -c 'A-Za-z0-9._+' '_'
}

# Arch version constraint suffix (">=1.2.3-4") -> XBPS (">=1.2.3_4")
# XBPS has no `=` comparator, so an exact Arch pin becomes a lower bound.
void_constraint() {
  local rest=$1
  case $rest in
    =*) rest=">=${rest#=}" ;;
  esac
  printf '%s' "$rest" | sed -E 's/-([0-9][0-9A-Za-z._+]*)$/_\1/'
}

# name [+version constraint] -> void name(s) [+constraint], one per line
map_dep() {
  local spec=$1 name rest t
  name=${spec%%[<>=]*}
  rest=${spec#"$name"}
  local targets=${map[$name]:-$name}
  if [ -n "${inrepo[$name]:-}" ]; then
    targets=$name
    # Keep the constraint for in-repo packages (same versioning scheme).
    rest=$(void_constraint "$rest")
  else
    # External packages do not share Arch's versioning (and Void package
    # versions carry an _revision), so drop the constraint entirely.
    rest=""
  fi
  # xbps-install cannot parse a bare dependency name: every run_depends entry
  # must be a full pkgver or a pattern. Unversioned dependencies become ">=0",
  # which is the lower bound form Void's own packages use.
  [ -n "$rest" ] || rest=">=0"
  for t in $targets; do printf '%s%s\n' "$t" "$rest"; done
}

# Arch "provides" entry ("name" or "name=version") -> XBPS virtual package
# ("name-version_rev"). XBPS requires every virtual provide to carry a version.
map_provide() {
  local spec=$1 name rest ver
  name=${spec%%[<>=]*}
  rest=${spec#"$name"}
  case $rest in
    =*) ver=${rest#=} ;;
    '') ver=0 ;;
    *) return 0 ;;   # range-style provides cannot be expressed; skip
  esac
  printf '%s-%s\n' "$name" "$(void_version "$ver")"
}

work=$(mktemp -d)
trap 'rm -rf "$work"' EXIT
mkdir -p "$work/root"
if command -v bsdtar >/dev/null 2>&1; then
  bsdtar -xf "$src" -C "$work/root"
else
  tar -xf "$src" -C "$work/root"
fi

gi="$work/root/.PKGINFO"
[ -f "$gi" ] || { echo "pkg2xbps: no .PKGINFO in $src" >&2; exit 1; }

get() { sed -n "s/^$1 = //p" "$gi" | head -n1; }

pkgname=$(get pkgname)
pkgverfull=$(get pkgver)
pkgdesc=$(get pkgdesc)
urlv=$(get url)
archv=$(get arch)

voidver=$(void_version "$pkgverfull")

mapfile -t depends   < <(sed -n 's/^depend = //p' "$gi")
mapfile -t licenses  < <(sed -n 's/^license = //p' "$gi")
mapfile -t provides  < <(sed -n 's/^provides = //p' "$gi")
mapfile -t conflicts < <(sed -n 's/^conflict = //p' "$gi")
mapfile -t replaces  < <(sed -n 's/^replaces = //p' "$gi")

# description: xbps-create wants a single line shorter than 80 characters
summary=${pkgdesc:-$pkgname}
summary=${summary:0:79}

license=Unknown
if [ "${#licenses[@]}" -gt 0 ]; then
  license=""
  for l in "${licenses[@]}"; do
    [ -n "$l" ] || continue
    license="${license:+$license AND }$l"
  done
  [ -n "$license" ] || license=Unknown
fi

requires=()
for d in "${depends[@]:-}"; do
  [ -n "$d" ] || continue
  while IFS= read -r m; do
    [ -n "$m" ] && requires+=("$m")
  done < <(map_dep "$d")
done
mapfile -t requires < <(printf '%s\n' "${requires[@]:-}" | sed '/^$/d' | sort -u)

provides_m=()
for p in "${provides[@]:-}"; do
  [ -n "$p" ] || continue
  while IFS= read -r m; do
    [ -n "$m" ] && provides_m+=("$m")
  done < <(map_provide "$p")
done

conflicts_m=()
for c in "${conflicts[@]:-}"; do
  [ -n "$c" ] || continue
  while IFS= read -r m; do
    [ -n "$m" ] && conflicts_m+=("$m")
  done < <(map_dep "$c")
done

replaces_m=()
for r in "${replaces[@]:-}"; do
  [ -n "$r" ] || continue
  while IFS= read -r m; do
    [ -n "$m" ] && replaces_m+=("$m")
  done < <(map_dep "$r")
done

# Strip pacman metadata and any pacman install script: an Arch .INSTALL is
# sourced by pacman and is not a valid XBPS INSTALL script.
rm -f "$work/root/.PKGINFO" "$work/root/.MTREE" "$work/root/.BUILDINFO" \
      "$work/root/.INSTALL" "$work/root/INSTALL" "$work/root/INSTALL.msg"
find "$work/root" -maxdepth 1 -name '.*' -exec rm -rf {} +

# Detect ELF binaries: Arch packages marked "any" may still ship compiled code.
has_elf() {
  local f
  while IFS= read -r -d '' f; do
    if [ "$(od -An -tx1 -N4 "$f" 2>/dev/null | tr -d ' \n')" = "7f454c46" ]; then
      return 0
    fi
  done < <(find "$work/root" -type f -print0)
  return 1
}

xbpsarch=noarch
if has_elf; then
  xbpsarch=x86_64
elif [ -n "${archv:-}" ] && [ "$archv" != "any" ]; then
  xbpsarch=$archv
fi

deps_str="${requires[*]:-}"
provides_str="${provides_m[*]:-}"
conflicts_str="${conflicts_m[*]:-}"
replaces_str="${replaces_m[*]:-}"

args=(
  -A "$xbpsarch"
  -n "$pkgname-$voidver"
  -s "$summary"
  -m "rstl.repo <rstl@arozoid.github.io>"
  -l "$license"
  --compression zstd
)
[ -n "${urlv:-}" ]        && args+=(-H "$urlv")
[ -n "$deps_str" ]        && args+=(-D "$deps_str")
[ -n "$provides_str" ]    && args+=(-P "$provides_str")
[ -n "$conflicts_str" ]   && args+=(-C "$conflicts_str")
[ -n "$replaces_str" ]    && args+=(-R "$replaces_str")

( cd "$outdir" && xbps-create "${args[@]}" "$work/root" )

if [ -n "$names_file" ]; then
  printf '%s\n' "$pkgname" >> "$names_file"
fi
echo "pkg2xbps: $pkgname-$voidver ($xbpsarch) -> $outdir"
