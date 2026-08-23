#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PKGDIR="$REPO_DIR/repo"
PKGBUILDS="$REPO_DIR/pkgbuilds"

mkdir -p "$PKGDIR"

if [ "$(id -u)" -eq 0 ]; then
  pacman_install() { pacman -U --noconfirm --needed "$@"; }
else
  pacman_install() { sudo pacman -U --noconfirm --needed "$@" || echo "==> WARNING: could not install $* (continuing)"; }
fi

declare -A built=()

pending() {
  local dir pkg
  for dir in "$PKGBUILDS"/*/; do
    pkg=$(basename "$dir")
    [ -n "${built[$pkg]:-}" ] || return 1
  done
}

while ! pending; do
  progress=0
  for dir in "$PKGBUILDS"/*/; do
    pkg=$(basename "$dir")
    [ -n "${built[$pkg]:-}" ] && continue
    mapfile -t deps < <(bash -c '. "$1/PKGBUILD"; printf "%s\n" "${depends[@]:-}" "${makedepends[@]:-}"' bash "$dir" | sed '/^$/d')
    defer_pkg=0
    if ! pacman -T "${deps[@]}" >/dev/null 2>&1; then
      # only defer if a missing dep is provided by another package in this repo;
      # anything else comes from the official repos and makepkg --syncdeps will fetch it
      for dep in "${deps[@]}"; do
        name=${dep%%[<>=]*}
        if [ -d "$PKGBUILDS/$name" ] && [ -z "${built[$name]:-}" ]; then
          defer_pkg=1
          break
        fi
      done
    fi
    if [ "$defer_pkg" -eq 1 ]; then
      echo "==> Deferring $pkg (waiting on repo packages)"
      continue
    fi
    echo "==> Building $pkg"
    if ( cd "$dir" && makepkg --syncdeps --noconfirm --nocheck --skipchecksums --skipinteg --skippgpcheck ); then
      pacman_install "$dir"*.pkg.tar.*
      mv "$dir"*.pkg.tar.* "$PKGDIR/"
      built[$pkg]=1
      progress=1
    else
      echo "==> ERROR: $pkg failed to build" >&2
      exit 1
    fi
  done
  if [ "$progress" -eq 0 ]; then
    echo "==> ERROR: unresolved dependencies:" >&2
    for dir in "$PKGBUILDS"/*/; do
      pkg=$(basename "$dir")
      [ -n "${built[$pkg]:-}" ] || echo "     $pkg" >&2
    done
    exit 1
  fi
done

echo "==> Creating repo database"
( cd "$PKGDIR" && repo-add rstl-repo.db.tar.gz *.pkg.tar.* )

echo "==> Done. Packages in $PKGDIR"
ls -lh "$PKGDIR"
