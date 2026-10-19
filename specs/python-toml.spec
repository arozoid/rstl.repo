# python-toml — Fedora no longer packages the `toml` module, but
# python-clickgen does `import toml` at runtime. Built natively by the rpm
# job in CI (pure python, no arch counterpart needed — Arch ships python-toml).
Name:           python-toml
Version:        0.10.2
Release:        1%{?dist}
Summary:        Python library for the TOML file format
License:        MIT
URL:            https://github.com/uiri/toml
Source0:        https://github.com/uiri/toml/archive/refs/tags/%{version}.tar.gz
BuildArch:      noarch
BuildRequires:  python3-devel
BuildRequires:  python3-build
BuildRequires:  python3-installer
BuildRequires:  python3-wheel
BuildRequires:  python3-setuptools

%description
Toml (Tomas's Obvious Minimal Language) is a format for storing configuration
data. It aims to be an easy to read, very minimal format which maps unambiguously
to a hash and is universally usable as a serialization format.

%prep
%autosetup -n toml-%{version}

%build
%{__python3} -m build --wheel --no-isolation

%install
%{__python3} -m installer -d %{buildroot} dist/*.whl

%files
%{python3_sitelib}/toml/
%{python3_sitelib}/toml-*.dist-info/
