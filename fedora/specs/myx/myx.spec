Name:           myx
Version:        0.5.0
Release:        1%{?dist}
Summary:        A lean, beautiful terminal Spotify player
License:        MIT
URL:            https://github.com/HaseebKhalid1507/Myx
Source0:        v0.5.0.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       gcc-libs alsa-lib openssl cargo rust

%description
A lean, beautiful terminal Spotify player

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
