Name:           python-clickgen
Version:        2.2.5
Release:        1%{?dist}
Summary:        X11 & Windows cursor building API
License:        MIT
URL:            https://github.com/ful1e5/clickgen
Source0:        v2.2.5.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       python-attrs python-numpy python-pillow python-toml python-yaml python-build python-installer python-setuptools python-wheel

%description
X11 & Windows cursor building API

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
