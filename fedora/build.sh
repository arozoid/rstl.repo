#!/usr/bin/env bash
# build.sh — build Fedora RPMs for rstl.repo.
#
# Builds .spec files in fedora/specs/<pkg>/<pkg>.spec using rpmbuild.
# Sources are fetched from the URLs defined in each spec file.
#
# Usage: ./build.sh [pkg1 pkg2 ...]
#   With no arguments, builds all packages.
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
RPMDIR="$REPO_DIR/rpms"
SPECS_DIR="$REPO_DIR/fedora/specs"

mkdir -p "$RPMDIR"

# Use rpmbuild if available, otherwise document what to do
if ! command -v rpmbuild &>/dev/null; then
  echo "ERROR: rpmbuild not found. Install rpm-build package to build Fedora RPMs." >&2
  echo "  sudo dnf install rpm-build" >&2
  exit 1
fi

# Set up rpmbuild directory structure
RPMTOP="${RPMTOP:-$HOME/rpmbuild}"
mkdir -p "$RPMTOP"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# Copy spec files and sources into rpmbuild tree
build_pkg() {
  local pkg="$1"
  local spec_dir="$SPECS_DIR/$pkg"
  local spec_file="$spec_dir/$pkg.spec"

  if [ ! -f "$spec_file" ]; then
    echo "==> Skipping $pkg: no spec file at $spec_file" >&2
    return 1
  fi

  echo "==> Building $pkg"
  cp "$spec_file" "$RPMTOP/SPECS/"

  # Download sources if they aren't already present
  # (In a real build, sources come from the Fedora lookaside cache)
  cd "$RPMTOP/SOURCES"
  while IFS= read -r line; do
    # Skip comments and non-Source lines
    [[ "$line" =~ ^Source[0-9]+: ]] || continue
    local src_url="${line#*: }"
    local src_name="${src_url##*/}"
    if [ ! -f "$src_name" ]; then
      echo "    Downloading $src_name"
      curl -fsSL -O "$src_url" || echo "    WARNING: failed to download $src_name" >&2
    fi
  done < "$spec_file"
  cd "$REPO_DIR"

  rpmbuild -ba --define "_topdir $RPMTOP" "$RPMTOP/SPECS/$pkg.spec"

  # Copy built RPMs to repo dir
  find "$RPMROOT/RPMS" -name "*.rpm" -exec cp {} "$RPMDIR/" \; 2>/dev/null || true

  echo "==> Built $pkg"
}

if [ $# -gt 0 ]; then
  for pkg in "$@"; do
    build_pkg "$pkg"
  done
else
  for d in "$SPECS_DIR"/*/; do
    pkg=$(basename "$d")
    build_pkg "$pkg"
  done
fi

echo "==> Done. RPMs in $RPMDIR"
ls -lh "$RPMDIR" 2>/dev/null || true
