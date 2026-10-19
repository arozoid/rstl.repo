Name:           rovr
Version:        0.10.3
Release:        1%{?dist}
Summary:        A post-modern terminal file explorer
License:        MIT
URL:            https://github.com/NSPC911/rovr
Source0:        rovr-linux-x64-nuitka.zip

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils

Requires:       bash glibc libgcc libstdc++ zlib unzip

%description
A post-modern terminal file explorer

%prep
%setup -q

%build
# Prebuilt binary, nothing to compile

%install
mkdir -p %{buildroot}/opt/%{name}
mkdir -p %{buildroot}/usr/bin
mkdir -p %{buildroot}/usr/share/licenses/%{name}

unzip -q %{SOURCE0} -d %{buildroot}/opt/%{name}

install -m 0755 /dev/stdin %{buildroot}/usr/bin/%{name} <<'EOF'
#!/usr/bin/env sh
exec /opt/%{name}/%{name} "$@"
EOF

install -m 0644 %{SOURCE1} %{buildroot}/usr/share/licenses/%{name}/LICENSE

%changelog
* Mon Oct 19 2026 rstl.repo <rstl@arozoid.dev> - %{version}-1
- Initial Fedora package
