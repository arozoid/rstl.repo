Name:           superfile
Version:        1.6.0
Release:        1%{?dist}
Summary:        Pretty fancy and modern terminal file manager
License:        MIT
URL:            https://github.com/yorukot/superfile
Source0:        v1.6.0.tar.gz

BuildArch:      x86_64

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       glibc go

%description
Pretty fancy and modern terminal file manager

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
