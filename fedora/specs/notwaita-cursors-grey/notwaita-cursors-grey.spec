Name:           notwaita-cursors-grey
Version:        ${_release//-/.}
Release:        2%{?dist}
Summary:        Grey Notwaita cursor theme - Adwaita-inspired, HiDPI (grey only, trimmed to 24/32/48px)
License:        custom
URL:            https://github.com/ful1e5/notwaita-cursor
Source0:        Notwaita-Gray.tar.xz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       hicolor-icon-theme python

%description
Grey Notwaita cursor theme - Adwaita-inspired, HiDPI (grey only, trimmed to 24/32/48px)

%prep
%setup -q

%build
# Nothing to build

%install
mkdir -p %{buildroot}/usr/share/icons
mkdir -p %{buildroot}/usr/share/licenses/%{name}

cp -a * %{buildroot}/usr/share/icons/ 2>/dev/null || true

install -m 0644 LICENSE* %{buildroot}/usr/share/licenses/%{name}/ 2>/dev/null || true

%changelog
* Mon Oct 19 2026 rstl.repo <rstl@arozoid.dev> - %{version}-1
- Initial Fedora package
