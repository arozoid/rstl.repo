#!/usr/bin/env bash
# resolve.sh — resolve the latest version for a package's upstream.
#
# Usage: resolve.sh <PKGBUILD>
#
# Reads the package's `url`, `pkgname`, and an `# auto:` marker:
#   # auto: release  -> pkgver = latest upstream release/tag (leading "v" stripped)
#   # auto: date     -> pkgver = YYYYMMDD, and _commit = latest commit sha
#
# Prints one or more `KEY=value` lines to stdout (pkgver and possibly _commit).
set -euo pipefail

pkgbuild=$1

url=$(bash -c '. "$1"; printf "%s" "$url"' bash "$pkgbuild")
pkgname=$(bash -c '. "$1"; printf "%s" "$pkgname"' bash "$pkgbuild")
mode=$(grep -oE '^# auto: (release|date)' "$pkgbuild" | awk '{print $3}')

case "$mode" in
  date)
    # No upstream releases: use today's date for the version, track latest commit.
    sha=$(curl -fsSL -H "User-Agent: rstl-repo" \
      "https://api.github.com/repos/${url#https://github.com/}/commits?per_page=1" \
      | grep -oE '"sha":"[0-9a-f]{40}"' | head -1 | grep -oE '[0-9a-f]{40}')
    printf 'pkgver=%s\n_commit=%s\n' "$(date +%Y%m%d)" "$sha"
    ;;
  release)
    # Use the latest upstream release tag. Pick the newest *version-like* tag to
    # ignore junk tags (e.g. "release", "final") that break version parsing.
    case "$url" in
      https://codeberg.org/*)
        json=$(curl -fsSL "https://codeberg.org/api/v1/repos/${url#https://codeberg.org/}/tags?limit=50")
        ;;
      https://github.com/*)
        json=$(curl -fsSL -H "User-Agent: rstl-repo" \
          "https://api.github.com/repos/${url#https://github.com/}/tags?per_page=50")
        ;;
      *)
        echo "resolve.sh: unsupported host in url: $url" >&2
        exit 1
        ;;
    esac
    # Gather version-like tags, then pick the highest by numeric version sort.
    # Tags may carry a Python-style ".postN" suffix (e.g. 0.10.1.post1).
    cands=()
    while IFS= read -r tag; do
      [ -z "$tag" ] && continue
      bare=${tag#v}
      [[ $bare =~ ^[0-9]+(\.[0-9]+){0,2}(\.post[0-9]+)?$ ]] || continue
      cands+=("$bare")
    done < <(printf '%s' "$json" | grep -oE '"name":"[^"]*"' | sed -E 's/^"name":"//;s/"$//')
    if [ "${#cands[@]}" -eq 0 ]; then
      echo "resolve.sh: no version-like tag found for $url" >&2
      exit 1
    fi
    best=$(printf '%s\n' "${cands[@]}" | {
      while IFS= read -r ver; do
        base=${ver%%.post*}
        post=0
        [[ $ver != "$base" ]] && post=${ver##*.post}
        IFS=. read -r a b c <<<"$base"
        printf '%03d.%03d.%03d.%03d %s\n' "${a:-0}" "${b:-0}" "${c:-0}" "$post" "$ver"
      done
    } | sort -r | head -1 | awk '{print $2}')
    printf 'pkgver=%s\n' "$best"
    ;;
  *)
    echo "resolve.sh: $pkgbuild has no '# auto:' marker" >&2
    exit 1
    ;;
esac
