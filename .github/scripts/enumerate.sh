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

# shard assignment — spread packages out instead of bunching related ones:
#   + at most MAX_PER_SLOT packages per slot (best effort)
#   + packages with related in-repo dependencies (share a dep, or one needs the
#     other) are pushed to different slots whenever a low-cost slot exists
#   + round-robin start from the topo index keeps the load balanced
max_per_slot=${MAX_PER_SLOT:-3}

# related[pkg] = everyone "similar" to pkg: its in-repo deps, everyone that
# depends on it, and everyone sharing any of its deps.
declare -A related
for p in "${order[@]}"; do
  list=" ${deps_of[$p]:-} "
  for q in "${order[@]}"; do
    [ "$q" = "$p" ] && continue
    case " ${deps_of[$q]:-} " in
      *" $p "*) list+=" $q " ;;
    esac
  done
  for d in ${deps_of[$p]:-}; do
    for q in "${order[@]}"; do
      [ "$q" = "$p" ] && continue
      case " ${deps_of[$q]:-} " in
        *" $d "*) list+=" $q " ;;
      esac
    done
  done
  related[$p]=$list
done

declare -A shard_of slot_pkgs slot_count
for i in "${!order[@]}"; do
  p="${order[$i]}"
  start=$(( i % slots ))
  pick=""
  pickcost=999
  for (( k=0; k<slots; k++ )); do
    n=$(( (start + k) % slots ))
    [ "${slot_count[$n]:-0}" -lt "$max_per_slot" ] || continue
    cost=0
    for q in ${related[$p]:-}; do
      case " ${slot_pkgs[$n]:-} " in
        *" $q "*) cost=$((cost + 1)) ;;
      esac
    done
    if [ "$cost" -lt "$pickcost" ]; then
      pickcost=$cost
      pick=$n
      [ "$cost" -eq 0 ] && break
    fi
  done
  [ -n "$pick" ] || { echo "enumerate.sh: no slot with capacity for $p" >&2; exit 1; }
  shard_of[$p]=$pick
  slot_pkgs[$pick]="${slot_pkgs[$pick]:-} $p "
  slot_count[$pick]=$(( ${slot_count[$pick]:-0} + 1 ))
done

packages_json='['
shard_map_json='{'
first_pkg=1
for p in "${order[@]}"; do
  [ "$first_pkg" -eq 1 ] || { packages_json+=','; shard_map_json+=','; }
  packages_json+="{\"pkg\":\"$(json_str "$p")\",\"deps\":["
  first=1
  for d in ${deps_of[$p]:-}; do
    [ "$first" -eq 1 ] || packages_json+=','
    packages_json+="\"$(json_str "$d")\""
    first=0
  done
  packages_json+=']}'
  shard_map_json+="\"$(json_str "$p")\":\"${shard_of[$p]}\""
  first_pkg=0
done
if [ "${#order[@]}" -eq 0 ]; then
  packages_json='[]'
  shard_map_json='{}'
fi
packages_json+=']'
shard_map_json+='}'

echo "packages_json=$packages_json"
echo "shard_map_json=$shard_map_json"
echo "slots=$slots"