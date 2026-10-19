#!/usr/bin/env bash
# build.sh — convert finished Arch packages into XBPS packages and generate a
# Void Linux repository for rstl.repo.
#
# This mirrors the Fedora pipeline: packages are converted from the .pkg.tar.*
# files built by CI (or by ../build.sh) rather than rebuilt from templates, so
# versions and file lists always match the Arch endpoint.
#
# Run on Void Linux (or inside the void-glibc-full container) with the `xbps`
# package installed. The same conversion is used by the CI `void` job.
#
# Usage:
#   ./build.sh                       # convert everything in ../repo and ../arch/repo
#   ./build.sh /path/to/*.pkg.tar.*  # convert specific packages
#   OUT=/path ./build.sh             # choose output directory (default ./repo)
#
set -euo pipefail

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$REPO_DIR/.." && pwd)"
OUT_DIR="${OUT:-$REPO_DIR/repo}"
KEY="$REPO_DIR/keys/rstl-repo.pem"
SIGNED_BY="rstl.repo <rstl@arozoid.github.io>"

command -v xbps-create >/dev/null 2>&1 || {
  cat >&2 <<'EOF'
ERROR: xbps-create not found.

Install the xbps tools on Void Linux:

    sudo xbps-install -Sy xbps

On any other distribution run this script inside the official Void container:

    podman run --rm -v "$PWD:/work" -w /work \
      ghcr.io/void-linux/void-glibc-full:latest \
      ./void/build.sh
EOF
  exit 1
}

mkdir -p "$OUT_DIR"
OUT_DIR="$(cd "$OUT_DIR" && pwd)"

if [ "$#" -gt 0 ]; then
  pkgs=("$@")
else
  mapfile -t pkgs < <(find "$ROOT_DIR/repo" "$ROOT_DIR/arch/repo" \
    -maxdepth 1 -type f -name '*.pkg.tar.*' 2>/dev/null | sort)
  if [ "${#pkgs[@]}" -eq 0 ]; then
    echo "ERROR: no .pkg.tar.* found in $ROOT_DIR/repo or $ROOT_DIR/arch/repo" >&2
    echo "       build the Arch packages first (./build.sh), or pass package paths." >&2
    exit 1
  fi
fi

names_file="$(mktemp)"
trap 'rm -f "$names_file"' EXIT

for p in "${pkgs[@]}"; do
  echo "==> Converting $(basename "$p")"
  bash "$ROOT_DIR/.github/scripts/pkg2xbps.sh" "$p" "$OUT_DIR" "$names_file"
done

echo "==> Registering packages in $OUT_DIR"
xbps-rindex -a "$OUT_DIR"/*.xbps

if [ -f "$KEY" ]; then
  echo "==> Signing repository index and packages"
  xbps-rindex -s --privkey "$KEY" --signedby "$SIGNED_BY" "$OUT_DIR"
  xbps-rindex -S --privkey "$KEY" "$OUT_DIR"/*.xbps
else
  echo "WARNING: $KEY not found; repository left unsigned." >&2
  echo "         Remote xbps clients refuse unsigned repositories." >&2
fi

echo "==> Done. Packages and repodata in $OUT_DIR"
ls -lh "$OUT_DIR"
