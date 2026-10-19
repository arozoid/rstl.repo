#!/usr/bin/env bash
# build.sh — Build Fedora RPMs and generate repository metadata for rstl.repo.
#
# This script is designed to run on a Fedora system with rpmbuild and
# createrepo_c installed. It builds .spec files in fedora/specs/<pkg>/
# into binary RPMs, then generates repodata (repomd.xml, primary.xml,
# filelists.xml, other.xml) so the result is a usable DNF/YUM repository.
#
# Usage:
#   ./build.sh              # build all packages
#   ./build.sh vectorcraft  # build one package
#   ./build.sh --repo-only  # just regenerate repodata from existing RPMs
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SPECS_DIR="$REPO_DIR/specs"
RPMS_DIR="$REPO_DIR/Packages"
REPODATA_DIR="$REPO_DIR/repodata"
SRPMS_DIR="$REPO_DIR/SRPMS"

mkdir -p "$RPMS_DIR" "$REPODATA_DIR" "$SRPMS_DIR"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

have_rpmbuild() { command -v rpmbuild >/dev/null 2>&1; }
have_createrepo() { command -v createrepo_c >/dev/null 2>&1 || command -v createrepo >/dev/null 2>&1; }

# Build one RPM package from its spec file.
build_one() {
  local pkg="$1"
  local spec_file="$SPECS_DIR/$pkg/$pkg.spec"

  if [ ! -f "$spec_file" ]; then
    echo "WARNING: no spec file for $pkg at $spec_file" >&2
    return 1
  fi

  echo "==> Building $pkg"
  rpmbuild -ba \
    --define "_topdir $REPO_DIR/rpmbuild" \
    --define "_rpmdir $RPMS_DIR" \
    --define "_srcrpmdir $SRPMS_DIR" \
    --define "_builddir $REPO_DIR/rpmbuild/BUILD" \
    "$spec_file"

  echo "==> Built $pkg"
}

# Regenerate repodata from existing RPMs.
repo_only() {
  echo "==> Generating repodata from existing RPMs"
  if command -v python3 >/dev/null 2>&1; then
    python3 "$REPO_DIR/generate_repo.py" "$REPO_DIR/x86_64"
  else
    echo "ERROR: python3 not found, cannot generate repodata" >&2
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if [ "${1:-}" = "--repo-only" ]; then
  repo_only
  exit 0
fi

if ! have_rpmbuild; then
  echo "ERROR: rpmbuild not found. Install rpm-build to build RPMs:" >&2
  echo "  sudo dnf install rpm-build" >&2
  echo "" >&2
  echo "You can still regenerate repodata from existing RPMs with:" >&2
  echo "  ./build.sh --repo-only" >&2
  exit 1
fi

# Build all or specific packages
if [ $# -gt 0 ]; then
  for pkg in "$@"; do
    build_one "$pkg"
  done
else
  for d in "$SPECS_DIR"/*/; do
    pkg=$(basename "$d")
    build_one "$pkg"
  done
fi

# Regenerate repodata after building
repo_only

echo "==> Done. RPMs in $RPMS_DIR, repodata in $REPODATA_DIR"
