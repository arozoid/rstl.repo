Name:           chroncal
Version:        0.10.0
Release:        1%{?dist}
Summary:        Terminal-first calendar, todo and journal manager
License:        MIT
URL:            https://github.com/DouglasdeMoura/chroncal
Source0:        v0.10.0.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       glibc go

%description
Terminal-first calendar, todo and journal manager

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
