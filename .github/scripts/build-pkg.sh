#!/usr/bin/env bash
# build-pkg.sh <pkg> — build one rstl.repo package.
#
# Used by CI (matrix jobs) and reusable from build.sh. Runs makepkg in a scratch
# dir so the source PKGBUILD is never mutated, installs the produced package
# (so in-repo dependencies are resolvable), and leaves the built artifacts in
# $REPO_DIR/out/<pkg>/ for upload/collection.
#
# CI sets BUILDER=builder and CARGO_HOME / CARGO_TARGET_DIR / RUSTUP_HOME to the
# cached locations; when BUILDER is unset the build runs as the invoking user.
set -euo pipefail

pkg="${1:?usage: build-pkg.sh <pkg>}"
root="$(cd "$(dirname "$0")/../.." && pwd)"

out="$root/out/$pkg"
builddir="/tmp/build-$pkg"
mkdir -p "$out"
rm -rf "$builddir"
mkdir -p "$builddir"
cp -a "$root/pkgbuilds/$pkg"/. "$builddir/"

if grep -q '^# auto:' "$builddir/PKGBUILD"; then
  echo "==> Resolving latest version for $pkg"
  bash "$root/inject.sh" "$root" "$builddir/PKGBUILD"
fi

# rust builds reuse a persistent cargo home/target across runs
export CARGO_HOME="${CARGO_HOME:-$HOME/.cargo}"
export CARGO_TARGET_DIR="${CARGO_TARGET_DIR:-$CARGO_HOME/target}"
mkdir -p "$CARGO_HOME" "$CARGO_TARGET_DIR"

makepkg_cmd='makepkg --syncdeps --noconfirm --nocheck --skipchecksums --skipinteg --skippgpcheck'
if [ -n "${BUILDER:-}" ]; then
  chown -R "$BUILDER" "$builddir" "$CARGO_HOME" "${RUSTUP_HOME:-/dev/null}" 2>/dev/null || true
  sudo -E -u "$BUILDER" bash -c "
    export CARGO_HOME='$CARGO_HOME' CARGO_TARGET_DIR='$CARGO_TARGET_DIR' RUSTUP_HOME='${RUSTUP_HOME:-}'
    cd '$builddir'
    $makepkg_cmd 2>&1
  "
else
  ( cd "$builddir" && $makepkg_cmd )
fi

mv "$builddir"/*.pkg.tar.* "$out/"
rm -rf "$builddir"

if [ "$(id -u)" -eq 0 ]; then
  pacman -U --noconfirm --needed "$out"/*.pkg.tar.* >/dev/null
else
  sudo pacman -U --noconfirm --needed "$out"/*.pkg.tar.* >/dev/null 2>&1 \
    || echo "==> WARNING: could not install $pkg (continuing)"
fi

echo "==> built $pkg -> $out"
ls -1 "$out"