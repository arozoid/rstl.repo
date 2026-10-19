Name:           xdg-desktop-portal-termfilechooser
Version:        1.4.3
Release:        1%{?dist}
Summary:        xdg-desktop-portal backend for your favorite terminal file chooser
License:        MIT
URL:            https://github.com/hunkyburrito/xdg-desktop-portal-termfilechooser
Source0:        v${pkgver}.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       xdg-desktop-portal libinih meson scdoc

%description
xdg-desktop-portal backend for your favorite terminal file chooser

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
