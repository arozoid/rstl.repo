#!/usr/bin/env python3
"""Generate Fedora .spec files for all rstl.repo packages."""

import os
import re
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
PKGBUILDS_DIR = os.path.join(REPO_DIR, "pkgbuilds")
SPECS_DIR = os.path.join(REPO_DIR, "fedora", "specs")

# Package type categories for spec generation
APPIMAGE_PKGS = {
    "vectorcraft", "filmcraft", "photocraft", "pdfcraft", "lightcraft",
    "designcraft", "effectcraft", "figcraft", "soundcraft", "cadcraft",
}

BINARY_ZIP_PKGS = {
    "rovr",
}

FONT_PKGS = {
    "ttf-jetbrains-mono-nerd-min",
}

ICON_THEME_PKGS = {
    "adwaita-icon-theme-dark", "papirus-icon-theme-dark-only",
    "xcursor-pro-dark", "notwaita-cursors-grey", "googledot-black",
}


def parse_pkgbuild(pkgdir):
    """Parse a PKGBUILD file and return a dict of key values."""
    with open(os.path.join(pkgdir, "PKGBUILD")) as f:
        content = f.read()

    info = {}

    # Simple key=value assignments (single line, possibly quoted)
    for key in ["pkgname", "pkgver", "pkgrel", "pkgdesc", "url"]:
        m = re.search(r'^' + key + r"\s*=\s*(.+)$", content, re.MULTILINE)
        if m:
            val = m.group(1).strip()
            # Strip surrounding quotes
            if (val.startswith('"') and val.endswith('"')) or \
               (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            info[key] = val

    # License: handle both array and simple assignment
    m = re.search(r'^license\s*=\s*\((.*?)\)', content, re.MULTILINE | re.DOTALL)
    if m:
        lic_str = m.group(1)
        # Extract unquoted or quoted words
        licenses = re.findall(r"'([^']+)'|\"([^\"]+)\"|(\S+)", lic_str)
        licenses = [l[0] or l[1] or l[2] for l in licenses if l[0] or l[1] or l[2]]
        info["license"] = " and ".join(licenses)
    else:
        m = re.search(r'^license\s*=\s*(.+)$', content, re.MULTILINE)
        if m:
            val = m.group(1).strip().strip('"').strip("'")
            info["license"] = val

    # Depends: handle array
    m = re.search(r'^depends\s*=\s*\((.*?)\)', content, re.MULTILINE | re.DOTALL)
    if m:
        dep_str = m.group(1)
        deps = re.findall(r"'([^']+)'|\"([^\"]+)\"|(\S+)", dep_str)
        info["depends"] = [d[0] or d[1] or d[2] for d in deps if d[0] or d[1] or d[2]]
    else:
        info["depends"] = []

    # Makepends
    m = re.search(r'^makedepends\s*=\s*\((.*?)\)', content, re.MULTILINE | re.DOTALL)
    if m:
        mkdep_str = m.group(1)
        mkdeps = re.findall(r"'([^']+)'|\"([^\"]+)\"|(\S+)", mkdep_str)
        info["makedepends"] = [d[0] or d[1] or d[2] for d in mkdeps if d[0] or d[1] or d[2]]
    else:
        info["makedepends"] = []

    # Source: parse the source array to get URLs
    # Source lines look like: "$pkgname-$pkgver.AppImage::$url/releases/download/..."
    # or: "LICENSE-APACHE::https://raw.githubusercontent.com/..."
    m = re.search(r'^source\s*=\s*\((.*?)\)', content, re.MULTILINE | re.DOTALL)
    if m:
        src_str = m.group(1)
        # Find all source entries: name::url or just url
        entries = re.findall(r'(\w+)::([^\s"\']+)', src_str)
        # Also find plain URLs (no ::)
        plain_urls = re.findall(r'(https?://[^\s"\']+)', src_str)
        
        info["sources"] = []
        for name, url in entries:
            info["sources"].append((name, url))
        for url in plain_urls:
            # Skip if already captured as part of ::
            if not any(url == u for _, u in info["sources"]):
                info["sources"].append((None, url))
    else:
        info["sources"] = []

    # Expand shell variables in URLs: $pkgname, $pkgver, $url, $pkgrel
    def expand_vars(s):
        s = s.replace("$pkgname", info.get("pkgname", ""))
        s = s.replace("$pkgver", info.get("pkgver", ""))
        s = s.replace("$pkgrel", info.get("pkgrel", "1"))
        s = s.replace("$url", info.get("url", ""))
        return s

    # Build the source list with expanded variables
    expanded_sources = []
    for name, url in info["sources"]:
        expanded_sources.append((name, expand_vars(url)))
    info["expanded_sources"] = expanded_sources

    return info


def spec_header(info):
    """Generate the header section of a .spec file."""
    name = info["pkgname"]
    ver = info["pkgver"]
    rel = info.get("pkgrel", "1")
    summary = info.get("pkgdesc", "")
    license_str = info.get("license", "MIT")
    url = info.get("url", "")

    lines = []
    lines.append(f"Name:           {name}")
    lines.append(f"Version:        {ver}")
    lines.append(f"Release:        {rel}%{{?dist}}")
    lines.append(f"Summary:        {summary}")
    lines.append(f"License:        {license_str}")
    lines.append(f"URL:            {url}")

    # Source0 is the first source
    sources = info.get("expanded_sources", [])
    if sources:
        source0_name, source0_url = sources[0]
        # Extract filename from URL
        filename = source0_url.split("/")[-1]
        lines.append(f"Source0:        {filename}")
        # Additional sources
        for i, (src_name, src_url) in enumerate(sources[1:], start=1):
            filename = src_url.split("/")[-1]
            lines.append(f"Source{i}:        {filename}")
    lines.append("")
    lines.append("BuildArch:      noarch")
    lines.append("")
    lines.append("BuildRequires:  coreutils")
    lines.append("BuildRequires:  findutils")
    lines.append("")

    # Fedora package name mappings for dependencies
    dep_map = {
        "dbus": "dbus",
        "glibc": "glibc",
        "libgcc": "libgcc",
        "libglvnd": "libglvnd",
        "libx11": "libX11",
        "libxcb": "libxcb",
        "libxcursor": "libXcursor",
        "libxi": "libXi",
        "libxkbcommon": "libxkbcommon",
        "libxkbcommon-x11": "libxkbcommon-x11",
        "vulkan-icd-loader": "vulkan-loader",
        "wayland": "wayland",
        "bash": "bash",
        "libstdc++": "libstdc++",
        "zlib": "zlib",
        "unzip": "unzip",
        "rust": "rust",
        "cargo": "cargo",
        "meson": "meson",
        "scdoc": "scdoc",
        "gtk-update-icon-cache": "gtk-update-icon-cache",
        "clang": "clang",
        "cmake": "cmake",
        "libva": "libva",
        "nasm": "nasm",
        "pulseaudio-libs": "pulseaudio-libs",
        "pipewire": "pipewire",
        "alsa-lib": "alsa-lib",
        "polkit": "polkit",
        "xdg-desktop-portal": "xdg-desktop-portal",
        "python3": "python3",
        "python3-pip": "python3-pip",
        "fcft": "fcft",
        "tllist": "tllist",
        "xorgproto": "xorgproto",
        "libxcb": "libxcb",
        "libxcb-util": "libxcb-util",
        "libxcb-cursor": "libxcb-cursor",
        "libxcb-wm": "libxcb-util-wm",
    }

    deps = info.get("depends", [])
    makedeps = info.get("makedepends", [])
    all_deps = list(dict.fromkeys(deps + makedeps))  # unique, preserve order

    fedora_deps = []
    for dep in all_deps:
        dep_name = re.sub(r'[<>=].*$', '', dep)
        fedora_name = dep_map.get(dep_name, dep_name)
        if fedora_name not in fedora_deps:
            fedora_deps.append(fedora_name)

    if fedora_deps:
        lines.append("Requires:       " + " ".join(fedora_deps))

    lines.append("")
    lines.append("%description")
    lines.append(summary)
    lines.append("")
    return "\n".join(lines)


def spec_prep_build_install(info):
    """Generate %prep, %build, %install sections."""
    name = info["pkgname"]
    ver = info["pkgver"]
    sources = info.get("expanded_sources", [])

    if name in APPIMAGE_PKGS:
        # Source0 is the AppImage, Source1/Source2 are licenses
        appimage_file = sources[0][1].split("/")[-1] if sources else f"{name}-{ver}-linux-x86_64.AppImage"
        prep = f"""%prep
%setup -q -c -n %{{name}}-%{{version}}

%build
# Prebuilt AppImage binary, nothing to compile

%install
mkdir -p %{{buildroot}}/usr/bin
mkdir -p %{{buildroot}}/usr/share/applications
mkdir -p %{{buildroot}}/usr/share/icons/hicolor
mkdir -p %{{buildroot}}/usr/share/metainfo
mkdir -p %{{buildroot}}/usr/share/mime/packages
mkdir -p %{{buildroot}}/usr/share/licenses/%{{name}}

chmod +x %{{SOURCE0}}
./%{{SOURCE0}} --appimage-extract >/dev/null

install -m 0755 squashfs-root/usr/bin/%{{name}} %{{buildroot}}/usr/bin/%{{name}}

# Install CLI if present
if [ -f squashfs-root/usr/bin/%{{name}}-cli ]; then
    install -m 0755 squashfs-root/usr/bin/%{{name}}-cli %{{buildroot}}/usr/bin/%{{name}}-cli
fi

# Install desktop file
if [ -f squashfs-root/usr/share/applications/*.desktop ]; then
    install -m 0644 squashfs-root/usr/share/applications/*.desktop %{{buildroot}}/usr/share/applications/
fi

# Install icons
if [ -d squashfs-root/usr/share/icons ]; then
    cp -a squashfs-root/usr/share/icons %{{buildroot}}/usr/share/
fi

# Install metainfo
if [ -d squashfs-root/usr/share/metainfo ]; then
    install -m 0644 squashfs-root/usr/share/metainfo/* %{{buildroot}}/usr/share/metainfo/
fi

# Install mime
if [ -d squashfs-root/usr/share/mime ]; then
    install -m 0644 squashfs-root/usr/share/mime/packages/* %{{buildroot}}/usr/share/mime/packages/
fi

# Install licenses
install -m 0644 %{{SOURCE1}} %{{buildroot}}/usr/share/licenses/%{{name}}/LICENSE-APACHE
install -m 0644 %{{SOURCE2}} %{{buildroot}}/usr/share/licenses/%{{name}}/LICENSE-MIT
"""
        files = """%files
/usr/bin/%{name}
/usr/bin/%{name}-cli
/usr/share/applications/*
/usr/share/icons/*
/usr/share/metainfo/*
/usr/share/mime/packages/*
/usr/share/licenses/%{name}/
"""
    elif name in BINARY_ZIP_PKGS:
        zip_file = sources[0][1].split("/")[-1] if sources else f"{name}-{ver}.zip"
        prep = f"""%prep
%setup -q

%build
# Prebuilt binary, nothing to compile

%install
mkdir -p %{{buildroot}}/opt/%{{name}}
mkdir -p %{{buildroot}}/usr/bin
mkdir -p %{{buildroot}}/usr/share/licenses/%{{name}}

unzip -q %{{SOURCE0}} -d %{{buildroot}}/opt/%{{name}}

install -m 0755 /dev/stdin %{{buildroot}}/usr/bin/%{{name}} <<'EOF'
#!/usr/bin/env sh
exec /opt/%{{name}}/%{{name}} "$@"
EOF

install -m 0644 %{{SOURCE1}} %{{buildroot}}/usr/share/licenses/%{{name}}/LICENSE
"""
        files = """%files
/opt/%{name}
/usr/bin/%{name}
/usr/share/licenses/%{name}/
"""
    elif name in FONT_PKGS:
        prep = """%prep
%setup -q

%build
# Nothing to build

%install
mkdir -p %{buildroot}/usr/share/fonts/TTF
mkdir -p %{buildroot}/usr/share/licenses/%{name}

install -m 0644 *.ttf %{buildroot}/usr/share/fonts/TTF/ 2>/dev/null || true
install -m 0644 *.otf %{buildroot}/usr/share/fonts/TTF/ 2>/dev/null || true

fc-cache -f %{buildroot}/usr/share/fonts/TTF/ 2>/dev/null || true

install -m 0644 LICENSE* %{buildroot}/usr/share/licenses/%{name}/ 2>/dev/null || true
"""
        files = """%files
/usr/share/fonts/TTF/*
/usr/share/licenses/%{name}/
"""
    elif name in ICON_THEME_PKGS:
        prep = """%prep
%setup -q

%build
# Nothing to build

%install
mkdir -p %{buildroot}/usr/share/icons
mkdir -p %{buildroot}/usr/share/licenses/%{name}

cp -a * %{buildroot}/usr/share/icons/ 2>/dev/null || true

install -m 0644 LICENSE* %{buildroot}/usr/share/licenses/%{name}/ 2>/dev/null || true
"""
        files = """%files
/usr/share/icons/*
/usr/share/licenses/%{name}/
"""
    else:
        # Source-built package
        prep = """%prep
%setup -q

%build
%configure
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}

mkdir -p %{buildroot}/usr/share/licenses/%{name}
install -m 0644 LICENSE %{buildroot}/usr/share/licenses/%{name}/LICENSE 2>/dev/null || true
install -m 0644 LICENSE* %{buildroot}/usr/share/licenses/%{name}/ 2>/dev/null || true
"""
        files = """%files
%{_bindir}/*
%{_datadir}/*
/usr/share/licenses/%{name}/
"""

    return prep


def spec_footer():
    """Generate %changelog section."""
    return """%changelog
* Mon Oct 19 2026 rstl.repo <rstl@arozoid.dev> - %{version}-1
- Initial Fedora package
"""


def generate_spec(info):
    """Generate a complete .spec file."""
    lines = []
    lines.append(spec_header(info))
    lines.append(spec_prep_build_install(info))
    lines.append(spec_footer())
    return "\n".join(lines)


def main():
    os.makedirs(SPECS_DIR, exist_ok=True)

    packages = sorted(os.listdir(PKGBUILDS_DIR))

    generated = []
    for pkg in packages:
        pkgdir = os.path.join(PKGBUILDS_DIR, pkg)
        if not os.path.isdir(pkgdir):
            continue

        info = parse_pkgbuild(pkgdir)
        if not info.get("pkgname"):
            print(f"WARNING: no pkgname in {pkg}", file=sys.stderr)
            continue

        spec_name = info["pkgname"]
        spec_dir = os.path.join(SPECS_DIR, spec_name)
        os.makedirs(spec_dir, exist_ok=True)

        spec_path = os.path.join(spec_dir, f"{spec_name}.spec")
        spec_content = generate_spec(info)

        with open(spec_path, "w") as f:
            f.write(spec_content)

        generated.append(spec_name)
        print(f"Generated: {spec_path}")

    print(f"\nGenerated {len(generated)} spec files in {SPECS_DIR}")


if __name__ == "__main__":
    main()
