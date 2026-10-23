Name:           linux-cachyos-frugal
Version:        0.2.0
Release:        1%{?dist}
Summary:        Build FRUGAL boot artifacts from the latest prebuilt CachyOS kernel
License:        GPL-3.0-or-later
URL:            https://github.com/arozoid/rstl.repo

Source0:        https://raw.githubusercontent.com/arozoid/rstl.repo/main/pkgbuilds/linux-cachyos-frugal/linux-cachyos-frugal
Source1:        https://raw.githubusercontent.com/arozoid/rstl.repo/main/pkgbuilds/linux-cachyos-frugal/mkFRkernel
Source2:        https://raw.githubusercontent.com/arozoid/rstl.repo/main/pkgbuilds/linux-cachyos-frugal/w_init.frugal
Source3:        https://raw.githubusercontent.com/arozoid/rstl.repo/main/pkgbuilds/linux-cachyos-frugal/linux-cachyos-frugal.hook
Source4:        https://raw.githubusercontent.com/arozoid/rstl.repo/main/pkgbuilds/linux-cachyos-frugal/README.md
Source5:        https://gitlab.com/firstrib/firstrib/-/raw/master/latest/build_system/initrd-latest.gz

BuildArch:      noarch

Requires:       bash
Requires:       coreutils
Requires:       findutils
Requires:       util-linux
Requires:       gzip
Requires:       cpio
Requires:       kmod
Requires:       squashfs-tools
Requires:       zstd
Requires:       curl
Requires:       bsdtar

%description
Builds vmlinuz, initrd.gz and 00modules.sfs from the latest prebuilt CachyOS
kernel package and installs them into an existing FRUGAL profile.  The
generated initrd can use 02modules.new/03firmware.new replacement layers, so
updating the kernel does not require switching profile links or boot entries.
The profile is discovered from the running overlay, w_bootfrom, and mounted
FRUGALS directories rather than a hard-coded mount path.

%prep
mkdir -p %{_builddir}/%{name}-%{version}
cp %{SOURCE0} %{_builddir}/%{name}-%{version}/linux-cachyos-frugal
cp %{SOURCE1} %{_builddir}/%{name}-%{version}/mkFRkernel
cp %{SOURCE2} %{_builddir}/%{name}-%{version}/w_init.frugal
cp %{SOURCE3} %{_builddir}/%{name}-%{version}/linux-cachyos-frugal.hook
cp %{SOURCE4} %{_builddir}/%{name}-%{version}/README.md

%build

%install
install -Dm755 %{_builddir}/%{name}-%{version}/linux-cachyos-frugal \
    %{buildroot}%{_bindir}/linux-cachyos-frugal
install -Dm755 %{_builddir}/%{name}-%{version}/mkFRkernel \
    %{buildroot}%{_prefix}/lib/linux-cachyos-frugal/mkFRkernel
install -Dm644 %{_builddir}/%{name}-%{version}/w_init.frugal \
    %{buildroot}%{_prefix}/lib/linux-cachyos-frugal/w_init
install -Dm644 %{SOURCE5} \
    %{buildroot}%{_prefix}/lib/linux-cachyos-frugal/initrd-latest.gz
install -Dm644 %{_builddir}/%{name}-%{version}/linux-cachyos-frugal.hook \
    %{buildroot}%{_datadir}/libalpm/hooks/90-linux-cachyos-frugal.hook
install -Dm644 %{_builddir}/%{name}-%{version}/README.md \
    %{buildroot}%{_docdir}/%{name}/README.md

%post
if [ -x %{_bindir}/linux-cachyos-frugal ]; then
    %{_bindir}/linux-cachyos-frugal --auto --source latest || :
fi

%files
%{_bindir}/linux-cachyos-frugal
%{_prefix}/lib/linux-cachyos-frugal/mkFRkernel
%{_prefix}/lib/linux-cachyos-frugal/w_init
%{_prefix}/lib/linux-cachyos-frugal/initrd-latest.gz
%{_datadir}/libalpm/hooks/90-linux-cachyos-frugal.hook
%{_docdir}/%{name}/README.md

%changelog
* Fri Oct 23 2026 rstl.repo <rstl@arozoid.dev> - 0.2.0-1
- Add 02modules.new/03firmware.new replacement-layer support
- Keep original FRUGAL layer links when deploying updates

* Fri Oct 23 2026 rstl.repo <rstl@arozoid.dev> - 0.1.0-1
- Initial Fedora package
