Name:           googledot-black
Version:        2.0.0
Release:        1%{?dist}
Summary:        Cursor theme inspired on Google — GoogleDot-Black only
License:        GPL-3.0-or-later
URL:            https://github.com/ful1e5/Google_Cursor
Source0:        v2.0.0.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       python-clickgen

%description
Cursor theme inspired on Google — GoogleDot-Black only

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
