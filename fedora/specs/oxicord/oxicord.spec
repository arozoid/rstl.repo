Name:           oxicord
Version:        0.1.9
Release:        1%{?dist}
Summary:        Vim-native Discord TUI for terminal enthusiasts
License:        GPL-3.0-only
URL:            https://github.com/linuxmobile/oxicord
Source0:        v0.1.9.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       chafa dbus glibc libgcc rustup

%description
Vim-native Discord TUI for terminal enthusiasts

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
