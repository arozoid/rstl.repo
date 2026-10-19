Name:           xcursor-pro-dark
Version:        2.0.2
Release:        1%{?dist}
Summary:        Modern X11 Cursor Theme — dark only (trimmed from xcursor-pro-cursor-theme)
License:        GPL-3.0-or-later
URL:            https://github.com/ful1e5/XCursor-pro
Source0:        v2.0.2.tar.gz
Source1:        bitmaps.zip

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       python-clickgen

%description
Modern X11 Cursor Theme — dark only (trimmed from xcursor-pro-cursor-theme)

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
