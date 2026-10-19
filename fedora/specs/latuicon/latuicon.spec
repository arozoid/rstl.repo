Name:           latuicon
Version:        0.1.6
Release:        1%{?dist}
Summary:        TUI icon picker (emojis / kaomojis / unicode / nerd fonts)
License:        MIT
URL:            https://github.com/coko7/latuicon
Source0:        v0.1.6.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       gcc-libs glibc cargo rust

%description
TUI icon picker (emojis / kaomojis / unicode / nerd fonts)

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
