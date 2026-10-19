Name:           yewtube
Version:        2.13.1
Release:        1%{?dist}
Summary:        Terminal-based YouTube player and downloader
License:        GPL3
URL:            https://github.com/mps-youtube/yewtube
Source0:        v2.13.1.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       python-pip python-httpx python-pylast python-pyperclip python-requests python-yewtube-search-python yt-dlp python-build python-installer python-setuptools python-wheel

%description
Terminal-based YouTube player and downloader

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
