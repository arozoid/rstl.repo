Name:           fzf-tab
Version:        1.3.0
Release:        1%{?dist}
Summary:        Replace zsh's default completion selection menu with fzf
License:        MIT
URL:            https://github.com/Aloxaf/fzf-tab
Source0:        v1.3.0.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       zsh fzf

%description
Replace zsh's default completion selection menu with fzf

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
