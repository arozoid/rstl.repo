Name:           zsh-auto-notify
Version:        0.11.1
Release:        1%{?dist}
Summary:        zsh plugin that automatically posts a notification when a long-running command finishes
License:        GPL-3.0-only
URL:            https://github.com/MichaelAquilina/zsh-auto-notify
Source0:        0.11.1.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       zsh libnotify

%description
zsh plugin that automatically posts a notification when a long-running command finishes

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
