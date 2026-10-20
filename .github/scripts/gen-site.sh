#!/usr/bin/env bash
# gen-site.sh <repo-dir>
#
# Build the universal website for the rstl.repo umbrella repository. The repo
# tree is expected to look like this:
#
#   <repo-dir>/arch/    Arch Linux packages + pacman database (canonical)
#   <repo-dir>/fedora/  Fedora RPMs + createrepo_c metadata
#   <repo-dir>/void/    Void XBPS packages + signed repository index
#
# Everything is written to the top level of <repo-dir>:
#
#   index.html   landing page, one section per distribution
#   style.css    the only stylesheet
#   <name>.html  one page per package, covering every format that exists
#
# The Arch repo is also served from the top level for backwards compatibility
# (assemble creates symlinks into arch/); the site itself only ever links to
# the per-distribution directories.
set -euo pipefail

dir=${1:?usage: gen-site.sh <repo-dir>}
base=${BASE_URL:-https://arozoid.github.io/rstl.repo}
cd "$dir"

# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------
escape() { sed -e 's/&/\&amp;/g' -e 's/</\&lt;/g' -e 's/>/\&gt;/g'; }
human()  { du -h "$1" | cut -f1; }

# name, version and architecture from an RPM filename
# (name-version-release.arch.rpm)
rpm_meta() {
  local b=${1##*/} arch rest
  b=${b%.rpm}
  arch=${b##*.}; rest=${b%.*}
  rest=${rest%-*}
  printf '%s\t%s\t%s\n' "${rest%-*}" "${rest##*-}" "$arch"
}

# name, version and architecture from an XBPS filename
# (name-version_revision.arch.xbps)
xbps_meta() {
  local b=${1##*/} arch rest
  b=${b%.xbps}
  arch=${b##*.}; rest=${b%.*}
  rest=${rest%_*}
  printf '%s\t%s\t%s\n' "${rest%-*}" "${rest##*-}" "$arch"
}

# ---------------------------------------------------------------------------
# collect the package index — one entry per name, per format
# ---------------------------------------------------------------------------
declare -A arch_of=() rpm_of=() xbps_of=() all=()
for f in arch/*.pkg.tar.*; do
  case $f in *.sig) continue ;; esac
  [ -e "$f" ] || continue
  n=$(pacman -Qip "$f" | sed -n 's/^Name *: //p')
  arch_of[$n]=$f
  all[$n]=1
done
for f in fedora/*.rpm; do
  [ -e "$f" ] || continue
  IFS=$'\t' read -r n _ _ < <(rpm_meta "$f")
  rpm_of[$n]=$f
  all[$n]=1
done
for f in void/*.xbps; do
  [ -e "$f" ] || continue
  IFS=$'\t' read -r n _ _ < <(xbps_meta "$f")
  xbps_of[$n]=$f
  all[$n]=1
done

# ---------------------------------------------------------------------------
# stylesheet
# ---------------------------------------------------------------------------
cat > style.css <<'CSS'
body{max-width:60rem;margin:2rem auto;padding:0 1rem;font:16px/1.6 system-ui,sans-serif}
h2{margin-top:3rem;border-bottom:1px solid #8884}
.scroll{overflow-x:auto}
table{border-collapse:collapse;width:100%}
th,td{padding:.3rem .5rem;text-align:left;border-bottom:1px solid #8884}
th{white-space:nowrap}
code,pre{background:#8881;border-radius:4px}
code{padding:.1rem .3rem}
pre{padding:.6rem .8rem;overflow-x:auto}
.muted{opacity:.65}
CSS

# ---------------------------------------------------------------------------
# index.html
# ---------------------------------------------------------------------------
{
  cat <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>rstl.repo</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<h1>rstl.repo</h1>
<p>Package repositories for the <a href="https://github.com/arozoid/rstl.sway/">rstl.sway</a> rice — the same packages rebuilt natively for Arch, Fedora and Void.</p>
<p><a href="#arch">Arch</a> · <a href="#fedora">Fedora</a> · <a href="#void">Void</a></p>

<h2 id="arch">Arch Linux <span class="muted">pacman</span></h2>
<p>Add this to <code>/etc/pacman.conf</code>:</p>
<pre>[rstl-repo]
SigLevel = Optional TrustAll
Server = $base/arch/</pre>
<p>Or pick a single package — the name links to its install command, download grabs the file:</p>
<div class="scroll">
<table>
<thead><tr><th>package</th><th>version</th><th>arch</th><th>size</th><th>download</th></tr></thead>
<tbody>
EOF
  for f in arch/*.pkg.tar.*; do
    case $f in *.sig) continue ;; esac
    [ -e "$f" ] || continue
    info=$(pacman -Qip "$f")
    n=$(printf '%s\n' "$info" | sed -n 's/^Name *: //p')
    v=$(printf '%s\n' "$info" | sed -n 's/^Version *: //p')
    a=$(printf '%s\n' "$info" | sed -n 's/^Architecture *: //p')
    b=$(basename "$f")
    printf '<tr><td><a href="%s.html">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td><a href="arch/%s" title="%s">download</a></td></tr>\n' \
      "$n" "$n" "$v" "${a:-?}" "$(human "$f")" "$b" "$b"
  done
  cat <<'EOF'
</tbody>
</table>
</div>

EOF
  cat <<EOF
<h2 id="fedora">Fedora <span class="muted">dnf</span></h2>
<p>Save this as <code>/etc/yum.repos.d/rstl.repo</code>:</p>
<pre>[rstl-repo]
baseurl=$base/fedora
enabled=1
gpgcheck=0</pre>
<p>Or pick a single package — the name links to its install command, download grabs the file:</p>
<div class="scroll">
<table>
<thead><tr><th>package</th><th>version</th><th>arch</th><th>size</th><th>download</th></tr></thead>
<tbody>
EOF
  for f in fedora/*.rpm; do
    [ -e "$f" ] || continue
    IFS=$'\t' read -r n v a < <(rpm_meta "$f")
    b=$(basename "$f")
    printf '<tr><td><a href="%s.html">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td><a href="fedora/%s" title="%s">download</a></td></tr>\n' \
      "$n" "$n" "$v" "${a:-?}" "$(human "$f")" "$b" "$b"
  done
  cat <<'EOF'
</tbody>
</table>
</div>

EOF
  cat <<EOF
<h2 id="void">Void Linux <span class="muted">xbps</span></h2>
<p>Add this to <code>/etc/xbps.d/0-rstl.conf</code> and accept the signing key on first sync:</p>
<pre>repository=$base/void</pre>
<p>Or pick a single package — the name links to its install command, download grabs the file:</p>
<div class="scroll">
<table>
<thead><tr><th>package</th><th>version</th><th>arch</th><th>size</th><th>download</th></tr></thead>
<tbody>
EOF
  for f in void/*.xbps; do
    [ -e "$f" ] || continue
    IFS=$'\t' read -r n v a < <(xbps_meta "$f")
    b=$(basename "$f")
    printf '<tr><td><a href="%s.html">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td><a href="void/%s" title="%s">download</a></td></tr>\n' \
      "$n" "$n" "$v" "${a:-?}" "$(human "$f")" "$b" "$b"
  done
  cat <<'EOF'
</tbody>
</table>
</div>

<p class="muted">Built by <a href="https://github.com/arozoid/rstl.repo">rstl.repo</a>.</p>
</body>
</html>
EOF
} > index.html

# ---------------------------------------------------------------------------
# one page per package, covering every format that exists
# ---------------------------------------------------------------------------
for n in "${!all[@]}"; do
  af=${arch_of[$n]:-}
  rf=${rpm_of[$n]:-}
  xf=${xbps_of[$n]:-}
  {
    cat <<EOF
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>$n — rstl.repo</title>
<link rel="stylesheet" href="style.css">
</head>
<body>
<p><a href="index.html">← rstl.repo</a></p>
<h1>$n</h1>
EOF
    if [ -n "$af" ]; then
      d=$(pacman -Qip "$af" | sed -n 's/^Description *: //p')
      [ -n "$d" ] && printf '<p class="muted">%s</p>\n' "$(printf '%s' "$d" | escape)"
    fi
    echo '<h2>install</h2>'
    if [ -n "$af" ]; then
      b=$(basename "$af")
      printf '<h3>Arch Linux</h3>\n<pre>sudo pacman -U %s/arch/%s</pre>\n<p><a href="arch/%s">download</a></p>\n' "$base" "$b" "$b"
    fi
    if [ -n "$rf" ]; then
      b=$(basename "$rf")
      printf '<h3>Fedora</h3>\n<pre>sudo dnf install %s/fedora/%s</pre>\n<p><a href="fedora/%s">download</a></p>\n' "$base" "$b" "$b"
    fi
    if [ -n "$xf" ]; then
      b=$(basename "$xf")
      printf '<h3>Void Linux</h3>\n<pre>sudo xbps-install -y -R %s/void %s</pre>\n<p><a href="void/%s">download</a></p>\n<p class="muted">Accept the repository signing key when prompted.</p>\n' "$base" "$n" "$b"
    fi
    if [ -n "$af" ]; then
      echo '<h2>files</h2>'
      echo '<ul>'
      tar -tf "$af" | grep -v -E '^\.(PKGINFO|BUILDINFO|MTREE|INSTALL)$|/$' | while IFS= read -r p; do
        printf '<li><code>%s</code></li>\n' "$(printf '%s' "$p" | escape)"
      done
      echo '</ul>'
    fi
    echo '</body>'
    echo '</html>'
  } > "$n.html"
done

echo "generated $(ls -1 *.html | wc -l) page(s)"
