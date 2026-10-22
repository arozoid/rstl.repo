Name:           ratl
Version:        0.1.0
Release:        1%{?dist}
Summary:        JSON-driven terminal dialogs rendered with ratatui
License:        MIT
URL:            https://github.com/arozoid/ratl
Source0:        v0.1.0.tar.gz

BuildArch:      x86_64

BuildRequires:  rustup

Requires:       glibc libstdc++

%description
ratl is a declarative terminal-dialog tool in the spirit of zenity, yad, and
gtkdialog. Dialogs are described in JSON and rendered with ratatui, making it
useful for shell scripts and installer frontends that should not depend on a
graphical toolkit.

%prep
%setup -q

%build
rustup toolchain install nightly --profile minimal --no-self-update
cargo +nightly build --release --locked

%install
install -Dm755 target/release/ratl %{buildroot}%{_bindir}/ratl
install -Dm644 LICENSE %{buildroot}/usr/share/licenses/%{name}/LICENSE
install -Dm644 README.md %{buildroot}/usr/share/doc/%{name}/README.md
install -Dm644 schema.json %{buildroot}/usr/share/doc/%{name}/schema.json
install -Dm644 ratl.json %{buildroot}/usr/share/doc/%{name}/ratl.json

%files
%{_bindir}/ratl
/usr/share/licenses/%{name}/LICENSE
/usr/share/doc/%{name}/README.md
/usr/share/doc/%{name}/schema.json
/usr/share/doc/%{name}/ratl.json

%changelog
* Thu Oct 22 2026 rstl.repo <rstl@arozoid.dev> - %{version}-1
- Initial Fedora package
