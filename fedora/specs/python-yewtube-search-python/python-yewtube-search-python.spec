Name:           python-yewtube-search-python
Version:        1.6.7
Release:        1%{?dist}
Summary:        Search for YouTube videos, channels and playlists without the Data API (yewtube's fork)
License:        MIT
URL:            https://github.com/iamtalhaasghar/youtube-search-python
Source0:        yewtube_search_python-1.6.7.tar.gz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       python-httpx python-build python-installer python-setuptools python-wheel

%description
Search for YouTube videos, channels and playlists without the Data API (yewtube's fork)

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
