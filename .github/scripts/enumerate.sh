#!/usr/bin/env bash
# enumerate.sh — compute the topological build order of rstl.repo packages and
# shard them across a fixed number of parallel slots.
#
# Prints three lines to stdout:
#   packages_json=<array of {pkg,deps}>  (deps = in-repo deps, topo-ordered)
#   shard_map_json=<object pkg->shard>
#   slots=<num>
set -euo pipefail

root="$(cd "$(dirname "$0")/../.." && pwd)"
slots="${RSTL_SLOTS:-16}"

json_str() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

# name_of[dir] = pkgname ; dir_of[pkgname] = dir
declare -A name_of dir_of
for d in "$root"/pkgbuilds/*/; do
  pkg=$(basename "$d")
  name=$(bash -c '. "$1"; printf "%s" "${pkgname:-}"' bash "$d/PKGBUILD")
  [ -n "$name" ] || { echo "enumerate.sh: pkgname missing in $d" >&2; exit 1; }
  name_of[$pkg]=$name
  dir_of[$name]=$pkg
done

# deps_of[pkg] = space-separated *in-repo* dependency names (depends+makedepends)
declare -A deps_of
for pkg in "${!name_of[@]}"; do
  d="$root/pkgbuilds/$pkg/PKGBUILD"
  mapfile -t deps < <(bash -c '. "$1"; printf "%s\n" "${depends[@]:-}" "${makedepends[@]:-}"' bash "$d" | sed '/^$/d')
  rdeps=()
  for dep in "${deps[@]}"; do
    n=${dep%%[<>!=]*}
    [ -n "${dir_of[$n]:-}" ] || continue
    rdeps+=("$n")
  done
  deps_of[$pkg]="${rdeps[*]}"
done

# topological sort (Kahn): repeatedly emit packages whose in-repo deps are done
pkgs=( "${!name_of[@]}" )
order=()
declare -A done_pkg
while [ "${#order[@]}" -lt "${#pkgs[@]}" ]; do
  progress=0
  for pkg in "${pkgs[@]}"; do
    [ -n "${done_pkg[$pkg]:-}" ] && continue
    unmet=0
    for d in ${deps_of[$pkg]:-}; do
      [ -n "${done_pkg[$d]:-}" ] || { unmet=1; break; }
    done
    if [ "$unmet" -eq 0 ]; then
      order+=("$pkg")
      done_pkg[$pkg]=1
      progress=1
    fi
  done
  if [ "$progress" -eq 0 ]; then
    echo "enumerate.sh: circular in-repo dependency detected" >&2
    exit 1
  fi
done

# contiguous shards over the topo order; a dependency always precedes its users,
# so any cross-shard fetch targets an earlier shard
size=$(( (${#order[@]} + slots - 1) / slots ))   # packages per slot
[ "$size" -gt 0 ] || { echo 'packages_json=[]'; echo 'shard_map_json={}'; echo "slots=$slots"; exit 0; }

packages_json='['
shard_map_json='{'
sn=0
i=0
for (( n=0; n<slots; n++ )); do
  if [ "$i" -ge "${#order[@]}" ]; then break; fi
  [ "$n" -eq 0 ] || { packages_json+=','; shard_map_json+=','; }
  packages_json+='{'
  pkgn=$(json_str "${order[$i]}")
  packages_json+="\"pkg\":\"$pkgn\",\"deps\":["
  first=1
  for d in ${deps_of[${order[$i]}]:-}; do
    [ "$first" -eq 1 ] || packages_json+=','
    packages_json+="\"$(json_str "$d")\""
    first=0
  done
  packages_json+=']}'
  shard_map_json+="\"$pkgn\":\"$sn\""
  sn=$((sn+1))
  for (( c=1; c<size && i<${#order[@]}; c++ )); do
    i=$((i+1))
    [ "$i" -ge "${#order[@]}" ] && break
    pkgn=$(json_str "${order[$i]}")
    packages_json+=',{"pkg":"'$pkgn'","deps":['
    first=1
    for d in ${deps_of[${order[$i]}]:-}; do
      [ "$first" -eq 1 ] || packages_json+=','
      packages_json+="\"$(json_str "$d")\""
      first=0
    done
    packages_json+=']}'
    shard_map_json+=",\"$pkgn\":\"$sn\""
  done
  i=$((i+1))
done
packages_json+=']'
shard_map_json+='}'

echo "packages_json=$packages_json"
echo "shard_map_json=$shard_map_json"
echo "slots=$slots"