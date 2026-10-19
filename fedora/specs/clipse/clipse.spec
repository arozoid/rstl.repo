Name:           clipse
Version:        1.2.1
Release:        1%{?dist}
Summary:        Configurable TUI clipboard manager for Unix
License:        MIT
URL:            https://github.com/savedra1/clipse
Source0:        v1.2.1.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       glibc wl-clipboard go

%description
Configurable TUI clipboard manager for Unix

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
