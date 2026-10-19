Name:           rstlpk
Version:        0.1.0
Release:        1%{?dist}
Summary:        Minimal polkit authentication agent for the rstl.sway rice (no gtk)
License:        MIT
URL:            https://github.com/arozoid/rstlpk
Source0:        v0.1.0.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       polkit rustup

%description
Minimal polkit authentication agent for the rstl.sway rice (no gtk)

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
