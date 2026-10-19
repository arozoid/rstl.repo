#!/usr/bin/env bash
# inject.sh — resolve a package's latest version and patch its PKGBUILD in place.
#
# Usage: inject.sh <REPO_DIR> <PKGBUILD>
# Patches `pkgver=` (and `_commit=` for date-mode) in the given PKGBUILD using
# resolve.sh, so makepkg picks up the current upstream version.
set -euo pipefail

repo=$1
pkgbuild=$2

while IFS='=' read -r key val; do
  case "$key" in
    pkgver)  sed -i "s|^pkgver=.*|pkgver=$val|" "$pkgbuild" ;;
    _commit) sed -i "s|^_commit=.*|_commit=$val|" "$pkgbuild" ;;
  esac
done < <("$repo/resolve.sh" "$pkgbuild")
