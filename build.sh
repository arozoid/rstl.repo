#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PKGDIR="$REPO_DIR/repo"
PKGBUILDS="$REPO_DIR/pkgbuilds"

mkdir -p "$PKGDIR"

# persistent cargo cache shared by every rust package build in this repo
RSTL_CARGO_CACHE="${RSTL_CARGO_CACHE:-$REPO_DIR/.cargo-cache}"
mkdir -p "$RSTL_CARGO_CACHE/home" "$RSTL_CARGO_CACHE/target"
export CARGO_HOME="$RSTL_CARGO_CACHE/home"
export CARGO_TARGET_DIR="$RSTL_CARGO_CACHE/target"

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

    # Build via the shared per-package helper (installs the result so in-repo
    # deps resolve, and leaves artifacts in $REPO_DIR/out/<pkg>/)
    echo "==> Building $pkg"
    if bash "$REPO_DIR/.github/scripts/build-pkg.sh" "$pkg"; then
      mv "$REPO_DIR"/out/$pkg/*.pkg.tar.* "$PKGDIR/"
      rm -rf "$REPO_DIR/out/$pkg"
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
