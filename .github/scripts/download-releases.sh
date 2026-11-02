#!/usr/bin/env bash
# download-releases.sh <dest-dir> [count] [patterns...]
#
# Download package assets from the newest <count> rstl.repo snapshots on GitHub
# Releases (default 3) into <dest-dir>/<tag>/. Optional glob patterns limit the
# download to one format (e.g. '*.rpm'); by default all three formats are
# fetched.
#
# Requires the GitHub CLI (`gh`) plus GH_TOKEN (or an already-authenticated gh).
# GH_REPO may be set to owner/name when not running inside the checked-out repo.
set -euo pipefail

dest=${1:?usage: download-releases.sh <dest-dir> [count] [patterns...]}
shift
count=3
if [[ ${1:-} =~ ^[0-9]+$ ]]; then
  count=$1
  shift
fi

if [ "$#" -gt 0 ]; then
  patterns=("$@")
else
  patterns=('*.pkg.tar.*' '*.rpm' '*.xbps')
fi
pattern_args=()
for p in "${patterns[@]}"; do
  pattern_args+=(--pattern "$p")
done

mkdir -p "$dest"

# Newest first. Only our own snapshot tags are considered, so unrelated
# releases in the repository are never downloaded or pruned.
mapfile -t tags < <(
  gh release list --limit 100 --exclude-drafts --exclude-pre-releases \
    --json tagName --jq '.[].tagName' \
    | grep -E '^repo-' \
    | head -n "$count" || true
)

if [ "${#tags[@]}" -eq 0 ]; then
  echo "download-releases: no repo-* releases found" >&2
  exit 1
fi

for tag in "${tags[@]}"; do
  [ -n "$tag" ] || continue
  out="$dest/$tag"
  mkdir -p "$out"
  echo "==> downloading $tag (${patterns[*]})"
  gh release download "$tag" --dir "$out" --clobber "${pattern_args[@]}"
done

echo "downloaded ${#tags[@]} release(s) into $dest"
