Name:           effectcraft
Version:        0.9.2
Release:        1%{?dist}
Summary:        Motion graphics and visual effects; an open-source, clean-room reimplementation of Adobe After Effects, rebuilt in pure Rust
License:        Apache-2.0 and MIT
URL:            https://github.com/storytold/effectcraft
Source0:        effectcraft-0.9.2-linux-x86_64.AppImage
Source1:        LICENSE-APACHE
Source2:        LICENSE-MIT

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       dbus glibc libgcc libglvnd libX11 libxcb libXcursor libXi libxkbcommon libxkbcommon-x11 vulkan-loader wayland

%description
Motion graphics and visual effects; an open-source, clean-room reimplementation of Adobe After Effects, rebuilt in pure Rust

%prep
%setup -q -c -n %{name}-%{version}

%build
# Prebuilt AppImage binary, nothing to compile

%install
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/applications
mkdir -p %{buildroot}/usr/share/icons/hicolor
mkdir -p %{buildroot}/usr/share/metainfo
mkdir -p %{buildroot}/usr/share/mime/packages
mkdir -p %{buildroot}/usr/share/licenses/%{name}

chmod +x %{SOURCE0}
./%{SOURCE0} --appimage-extract >/dev/null

install -m 0755 squashfs-root/usr/bin/%{name} %{buildroot}/usr/bin/%{name}

# Install CLI if present
if [ -f squashfs-root/usr/bin/%{name}-cli ]; then
    install -m 0755 squashfs-root/usr/bin/%{name}-cli %{buildroot}/usr/bin/%{name}-cli
fi

# Install desktop file
if [ -f squashfs-root/usr/share/applications/*.desktop ]; then
    install -m 0644 squashfs-root/usr/share/applications/*.desktop %{buildroot}/usr/share/applications/
fi

# Install icons
if [ -d squashfs-root/usr/share/icons ]; then
    cp -a squashfs-root/usr/share/icons %{buildroot}/usr/share/
fi

# Install metainfo
if [ -d squashfs-root/usr/share/metainfo ]; then
    install -m 0644 squashfs-root/usr/share/metainfo/* %{buildroot}/usr/share/metainfo/
fi

# Install mime
if [ -d squashfs-root/usr/share/mime ]; then
    install -m 0644 squashfs-root/usr/share/mime/packages/* %{buildroot}/usr/share/mime/packages/
fi

# Install licenses
install -m 0644 %{SOURCE1} %{buildroot}/usr/share/licenses/%{name}/LICENSE-APACHE
install -m 0644 %{SOURCE2} %{buildroot}/usr/share/licenses/%{name}/LICENSE-MIT

%changelog
* Mon Oct 19 2026 rstl.repo <rstl@arozoid.dev> - %{version}-1
- Initial Fedora package
