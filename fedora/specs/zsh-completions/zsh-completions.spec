Name:           zsh-completions
Version:        0.36.0
Release:        1%{?dist}
Summary:        Additional completion definitions for Zsh
License:        MIT
URL:            https://github.com/zsh-users/zsh-completions
Source0:        0.36.0.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       zsh

%description
Additional completion definitions for Zsh

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
