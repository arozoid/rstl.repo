Name:           concord
Version:        2.5.22
Release:        1%{?dist}
Summary:        A feature-rich TUI client for Discord
License:        GPL-3.0-only
URL:            https://github.com/chojs23/concord
Source0:        v2.5.22.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       glibc libgcc libstdc++ alsa-lib libpipewire libva rustup clang cmake nasm

%description
A feature-rich TUI client for Discord

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
