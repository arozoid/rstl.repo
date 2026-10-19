Name:           papirus-icon-theme-dark-only
Version:        20260801
Release:        1%{?dist}
Summary:        Papirus icon theme — Papirus-Dark only
License:        GPL-3.0
URL:            https://github.com/PapirusDevelopmentTeam/papirus-icon-theme
Source0:        papirus-icon-theme-20260801.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       gtk-update-icon-cache

%description
Papirus icon theme — Papirus-Dark only

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
