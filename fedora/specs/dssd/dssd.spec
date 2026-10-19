Name:           dssd
Version:        0.3.3
Release:        1%{?dist}
Summary:        Dead simple freedesktop SecretService implementation
License:        MIT
URL:            https://github.com/ylxdzsw/dssd
Source0:        v0.3.3.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       dbus rustup

%description
Dead simple freedesktop SecretService implementation

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
