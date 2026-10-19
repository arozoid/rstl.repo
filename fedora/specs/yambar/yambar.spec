Name:           yambar
Version:        1.11.0
Release:        1%{?dist}
Summary:        Modular status panel for X11 and Wayland, inspired by polybar
License:        MIT
URL:            https://codeberg.org/dnkl/$pkgname
Source0:        1.11.0.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       fcft libpulse libudev.so libxcb libyaml libpipewire-0.3.so pipewire pixman wayland wayland-protocols xcb-util xcb-util-cursor xcb-util-wm meson scdoc tllist xorgproto

%description
Modular status panel for X11 and Wayland, inspired by polybar

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
