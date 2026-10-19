Name:           ttf-jetbrains-mono-nerd-min
Version:        3.5.0
Release:        1%{?dist}
Summary:        JetBrains Mono Nerd Font — minimal (regular weight only)
License:        OFL-1.1-no-RFN
URL:            https://github.com/ryanoasis/nerd-fonts
Source0:        JetBrainsMono.tar.xz

BuildArch:      noarch

BuildRequires:  coreutils
BuildRequires:  findutils


%description
JetBrains Mono Nerd Font — minimal (regular weight only)

%prep
%setup -q

%build
# Nothing to build

%install
mkdir -p %{buildroot}/usr/share/fonts/TTF
mkdir -p %{buildroot}/usr/share/licenses/%{name}

install -m 0644 *.ttf %{buildroot}/usr/share/fonts/TTF/ 2>/dev/null || true
install -m 0644 *.otf %{buildroot}/usr/share/fonts/TTF/ 2>/dev/null || true

fc-cache -f %{buildroot}/usr/share/fonts/TTF/ 2>/dev/null || true

install -m 0644 LICENSE* %{buildroot}/usr/share/licenses/%{name}/ 2>/dev/null || true

%changelog
* Mon Oct 19 2026 rstl.repo <rstl@arozoid.dev> - %{version}-1
- Initial Fedora package
