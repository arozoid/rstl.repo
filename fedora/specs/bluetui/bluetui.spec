Name:           bluetui
Version:        0.8.2
Release:        1%{?dist}
Summary:        TUI for managing bluetooth devices
License:        GPL-3.0-only
URL:            https://github.com/pythops/bluetui
Source0:        v0.8.2.tar.gz

BuildArch:      x86_64

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       gcc-libs dbus bluez rustup

%description
TUI for managing bluetooth devices

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
* Tue Oct 20 2026 rstl.repo <rstl@arozoid.dev> - %{version}-1
- Initial Fedora package
