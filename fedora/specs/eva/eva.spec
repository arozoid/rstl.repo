Name:           eva
Version:        0.3.1
Release:        1%{?dist}
Summary:        Simple calculator REPL, similar to bc(1)
License:        MIT
URL:            https://github.com/NerdyPepper/eva
Source0:        v0.3.1.tar.gz

BuildArch:      x86_64

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       glibc gcc-libs rustup

%description
Simple calculator REPL, similar to bc(1)

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
