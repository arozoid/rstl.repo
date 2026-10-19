Name:           adwaita-icon-theme-dark
Version:        50.0
Release:        1%{?dist}
Summary:        GNOME standard icons (dark-capable Adwaita), bundled without the adwaita-cursors dependency
License:        CC-BY-SA-3.0
URL:            https://gitlab.gnome.org/GNOME/adwaita-icon-theme
Source0:        adwaita-icon-theme-50.0.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       hicolor-icon-theme gtk-update-icon-cache librsvg meson

%description
GNOME standard icons (dark-capable Adwaita), bundled without the adwaita-cursors dependency

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
