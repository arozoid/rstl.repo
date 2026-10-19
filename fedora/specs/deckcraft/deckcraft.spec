Name:           deckcraft
Version:        0.6.1
Release:        1%{?dist}
Summary:        Presentations and slide shows; an open-source, clean-room reimplementation of Microsoft PowerPoint, rebuilt in pure Rust
License:        Apache-2.0 and MIT
URL:            https://github.com/storytold/deckcraft
Source0:        deckcraft-0.6.1-linux-x86_64.AppImage
Source1:        LICENSE-APACHE
Source2:        LICENSE-MIT

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       dbus glibc libgcc libglvnd libX11 libxcb libXcursor libXi libxkbcommon libxkbcommon-x11 vulkan-loader wayland

%description
Presentations and slide shows; an open-source, clean-room reimplementation of Microsoft PowerPoint, rebuilt in pure Rust

%prep
%setup -q

%build
%configure
make %{?_smp_mflags}

%install
make install DESTDIR=%{buildroot}

mkdir -p %{buildroot}/usr/share/licenses/%{name}
install -m 0644 LICENSE %{buildroot}/usr/share/licenses/%{name}/LICENSE 2>/dev/null || true
install -m 0644 LICENSE* %{buildroot}/usr/share/licenses/%{name}/ 2>/dev/null || true

%changelog
* Mon Oct 19 2026 rstl.repo <rstl@arozoid.dev> - %{version}-1
- Initial Fedora package
