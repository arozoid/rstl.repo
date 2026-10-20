Name:           awww
Version:        0.12.1
Release:        1%{?dist}
Summary:        Efficient animated wallpaper daemon for Wayland, controlled at runtime
License:        GPL-3.0-or-later
URL:            https://codeberg.org/LGFae/awww
Source0:        v0.12.1.tar.gz

BuildArch:      x86_64

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       glibc gcc-libs libxkbcommon lz4 rustup dav1d scdoc wayland wayland-protocols

%description
Efficient animated wallpaper daemon for Wayland, controlled at runtime

%prep
%setup -q -n awww

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
