#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
PKGDIR="$REPO_DIR/repo"
PKGBUILDS="$REPO_DIR/pkgbuilds"

mkdir -p "$PKGDIR"

for dir in "$PKGBUILDS"/*/; do
  pkg=$(basename "$dir")
  echo "==> Building $pkg"
  ( cd "$dir" && makepkg --noconfirm --nocheck --skipchecksums --skipinteg --skippgpcheck )
  mv "$dir"*.pkg.tar.* "$PKGDIR/" 2>/dev/null || true
done

echo "==> Creating repo database"
( cd "$PKGDIR" && repo-add rstl-repo.db.tar.gz *.pkg.tar.* )

echo "==> Done. Packages in $PKGDIR"
ls -lh "$PKGDIR"
