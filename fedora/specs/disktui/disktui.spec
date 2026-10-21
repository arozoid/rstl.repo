Name:           disktui
Version:        1.3.0
Release:        1%{?dist}
Summary:        TUI for disk management and partitioning
License:        MIT
URL:            https://github.com/mkbula/disktui
Source0:        v1.3.0.tar.gz

BuildArch:      x86_64

BuildRequires:  cargo
BuildRequires:  rust

Requires:       libstdc++ parted e2fsprogs cryptsetup polkit which util-linux

%description
A terminal-based disk management and partitioning utility built with Rust and
Ratatui.

%prep
%setup -q

%build
cargo build --release --locked

%install
install -Dm755 target/release/disktui %{buildroot}%{_bindir}/disktui
install -Dm755 target/release/disktui-helper %{buildroot}%{_bindir}/disktui-helper
install -Dm644 LICENSE %{buildroot}/usr/share/licenses/%{name}/LICENSE
install -Dm644 README.md %{buildroot}/usr/share/doc/%{name}/README.md

%files
%{_bindir}/disktui
%{_bindir}/disktui-helper
/usr/share/licenses/%{name}/LICENSE
/usr/share/doc/%{name}/README.md

%changelog
* Wed Oct 21 2026 rstl.repo <rstl@arozoid.dev> - %{version}-1
- Initial Fedora package
