# Build ocaml bits unless rpmbuild was run with --without ocaml
# or ocamlopt is missing (the xen makefile doesn't build ocaml bits if it isn't there)
%define with_ocaml 0
%define build_ocaml 0
# Build with docs unless rpmbuild was run with --without docs
%define build_docs %{?_without_docs: 0} %{?!_without_docs: 1}
# Build without stubdom unless rpmbuild was run with --with stubdom
%define build_stubdom %{?_with_stubdom: 1} %{?!_with_stubdom: 0}
# Build without qemu-traditional unless rpmbuild was run with --with qemutrad
%define build_qemutrad %{?_with_qemutrad: 1} %{?!_with_qemutrad: 0}
# build with ovmf from edk2-ovmf unless rpmbuild was run with --without ovmf
%define build_ovmf %{?_without_ovmf: 0} %{?!_without_ovmf: 1}
# set to 0 for archs that don't use qemu or ovmf (reduces build dependencies)
%ifnarch x86_64 %{ix86}
%define build_qemutrad 0
%define build_ovmf 0
%endif
%if ! %build_qemutrad
%define build_stubdom 0
%endif
# Build with xen hypervisor unless rpmbuild was run with --without hyp
%define build_hyp %{?_without_hyp: 0} %{?!_without_hyp: 1}
# build xsm support unless rpmbuild was run with --without xsm
# or required packages are missing
%define with_xsm 0
%define build_xsm 0
# cross compile 64-bit hypervisor on ix86 unless rpmbuild was run
# with --without crosshyp
%define build_crosshyp %{?_without_crosshyp: 0} %{?!_without_crosshyp: 1}
%ifnarch %{ix86}
%define build_crosshyp 0
%else
%if ! %build_crosshyp
%define build_hyp 0
%endif
%endif
# no point in trying to build xsm on ix86 without a hypervisor
%if ! %build_hyp
%define build_xsm 0
%endif
# build an efi boot image (where supported) unless rpmbuild was run with
# --without efi
%define build_efi %{?_without_efi: 0} %{?!_without_efi: 1}
# xen only supports efi boot images on x86_64 or aarch64
# i686 builds a x86_64 hypervisor so add that as well
%ifnarch x86_64 aarch64 %{ix86}
%define build_efi 0
%endif
%if "%dist" >= ".fc20"
%define with_systemd_presets 1
%else
%define with_systemd_presets 0
%endif

%if 0%{?centos} >= 8
%define with_systemd_presets 1
%define build_docs 0
%define build_hyp 0
%define build_ovmf 0
%endif

# workaround for https://bugzilla.redhat.com/1671883 (dwz leaving temp files of
# hardlinked sources)
%define _unpackaged_files_terminate_build 0

# Hypervisor ABI
%define hv_abi 4.14

%define upstream_version 4.14.0
%define rctag %(echo 4.14.0 | sed -n -e 's/.*-\\(rc[0-9]*\\).*/0.\\1./;/rc/p')

Summary: Xen is a virtual machine monitor
Name:    xen
Version: %(echo 4.14.0 | sed 's/-rc.*//')
Release: %{?rctag}4%{?dist}
Epoch:   2001
License: GPLv2+ and LGPLv2+ and BSD
URL:     http://xen.org/
Source0: https://downloads.xenproject.org/release/xen/%{upstream_version}/xen-%{upstream_version}.tar.gz
Source2: %{name}.logrotate
# .config file for xen hypervisor
Source3: config
Source32: xen.modules-load.conf

# Out-of-tree patches.
#
# Use the following patch numbers:
# 100+:  Fedora
# 200+:  EFI workarounds
# 300+:  Backports
# 500+:  Security fixes
# 600+:  Upstreamable patches
# 700+:  GCC7+ fixes
# 800+:  vchan for stubdom
# 900+:  Support for Linux based stubdom
# 1000+: Qubes specific patches
# 1100+: Others

# EFI workarounds
Patch201: patch-0001-EFI-early-Add-noexit-to-inhibit-calling-ExitBootServices.patch
Patch202: patch-0002-efi-Ensure-incorrectly-typed-runtime-services-get-ma.patch
Patch203: patch-0001-Add-xen.cfg-options-for-mapbs-and-noexitboot.patch

# Backports

# Security fixes
Patch500: patch-xsa337-1.patch
Patch501: patch-xsa337-2.patch
Patch502: patch-xsa338.patch
Patch503: patch-xsa340.patch
Patch504: patch-xsa342.patch
Patch505: patch-xsa343-1.patch
Patch506: patch-xsa343-2.patch
Patch507: patch-xsa343-3.patch

# Upstreamable patches
Patch601: patch-xen-libxl-error-write-perm.patch
#TODO: simplified script instead:
# Patch604: patch-libxl-Revert-libxl-Remove-redundant-setting-of-phyical-dev.patch
# Patch605: patch-libxl-allow-PHY-backend-for-files-allocate-loop-devi.patch
# Patch606: patch-libxl-do-not-call-default-block-script.patch
Patch607: patch-libxl-do-not-for-backend-on-PCI-remove-when-backend-.patch
Patch614: patch-0001-libxl-do-not-fail-device-removal-if-backend-domain-i.patch
Patch621: patch-libxc-fix-xc_gntshr_munmap-semantic.patch
Patch622: patch-xen-disable-efi-gettime.patch
Patch627: patch-libxl-automatically-enable-gfx_passthru-if-IGD-is-as.patch
Patch628: patch-libxl-workaround-gcc-10.2-maybe-uninitialized-warnin.patch
Patch629: patch-libxl-fix-Werror-stringop-truncation-in-libxl__prepa.patch

# GCC8 fixes
Patch714: patch-tools-kdd-mute-spurious-gcc-warning.patch

# Support for Linux based stubdom
Patch900: patch-disable-dom0-qemu.patch

# MSI fixes
Patch950: patch-stubdom-allow-msi-enable.patch

# Qubes specific patches
Patch1001: patch-stubdom-vbd-non-dom0-backend.patch
Patch1002: patch-xen-no-downloads.patch
Patch1003: patch-xen-hotplug-external-store.patch
Patch1006: patch-xen-libxl-qubes-minimal-stubdom.patch
Patch1007: patch-xen-disable-dom0-qemu.patch
Patch1009: patch-xenconsoled-enable-logging.patch
Patch1010: patch-stubdom-linux-libxl-suspend.patch
Patch1011: patch-xen-hotplug-qubesdb-update.patch
Patch1013: patch-stubdom-linux-libxl-use-EHCI-for-providing-tablet-USB-device.patch
Patch1014: patch-allow-kernelopts-stubdom.patch
Patch1015: patch-libxl-readonly-disk-scsi.patch
Patch1016: patch-tools-xenconsole-replace-ESC-char-on-xenconsole-outp.patch
Patch1017: patch-libxl-disable-vkb-by-default.patch

Patch1020: patch-stubdom-linux-config-qubes-gui.patch
Patch1021: patch-stubdom-linux-libxl-do-not-force-qdisk-backend-for-cdrom.patch
Patch1022: patch-xen-acpi-slic-support.patch

Patch1030: patch-fix-igd-passthrough-with-linux-stubdomain.patch

%if %build_qemutrad
BuildRequires: libidn-devel zlib-devel SDL-devel curl-devel
BuildRequires: libX11-devel gtk2-devel libaio-devel
# build using Fedora seabios and ipxe packages for roms
BuildRequires: seabios-bin ipxe-roms-qemu
%ifarch %{ix86} x86_64
# for the VMX "bios"
BuildRequires: dev86
%endif
%endif
# qemu-xen
BuildRequires: glib2-devel pixman-devel
BuildRequires: python%{python3_pkgversion}-devel ncurses-devel
BuildRequires: perl-interpreter perl-generators
%ifarch %{ix86} x86_64
# so that x86_64 builds pick up glibc32 correctly
BuildRequires: /usr/include/gnu/stubs-32.h
%endif
# BEGIN QUBES SPECIFIC PART
BuildRequires: autoconf
BuildRequires: automake
BuildRequires: flex
BuildRequires: bison
# END QUBES SPECIFIC PART
BuildRequires: gettext
BuildRequires: gnutls-devel
BuildRequires: openssl-devel
# For ioemu PCI passthrough
BuildRequires: pciutils-devel
# Several tools now use uuid
BuildRequires: libuuid-devel
# iasl needed to build hvmloader
BuildRequires: acpica-tools
# modern compressed kernels
BuildRequires: bzip2-devel xz-devel
# libfsimage
BuildRequires: e2fsprogs-devel
# tools now require yajl
BuildRequires: yajl-devel
# remus support now needs libnl3
BuildRequires: libnl3-devel
%if %with_xsm
# xsm policy file needs needs checkpolicy and m4
BuildRequires: checkpolicy m4
%endif
%if %build_crosshyp
# cross compiler for building 64-bit hypervisor on ix86
BuildRequires: gcc-x86_64-linux-gnu
%endif
BuildRequires: gcc
Requires: iproute
Requires: python%{python3_pkgversion}-lxml
Requires: xen-runtime = %{epoch}:%{version}-%{release}
# Not strictly a dependency, but kpartx is by far the most useful tool right
# now for accessing domU data from within a dom0 so bring it in when the user
# installs xen.
Requires: kpartx
ExclusiveArch: %{ix86} x86_64 armv7hl aarch64
#ExclusiveArch: %#{ix86} x86_64 ia64 noarch
%if %with_ocaml
BuildRequires: ocaml, ocaml-findlib
%endif
%if %with_systemd_presets
Requires(post): systemd
Requires(preun): systemd
BuildRequires: systemd
%endif
BuildRequires: systemd-devel
%ifarch armv7hl aarch64
BuildRequires: libfdt-devel
%endif
%if %build_ovmf
BuildRequires: edk2-ovmf
%endif
Requires: seabios-bin

%description
This package contains the XenD daemon and xm command line
tools, needed to manage virtual machines running under the
Xen hypervisor

# BEGIN QUBES SPECIFIC PART
%package -n python%{python3_pkgversion}-%{name}
Summary: python%{python3_pkgversion} bindings for Xen tools
Group: Development/Libraries
Requires: xen-libs = %{epoch}:%{version}-%{release}
Requires: python%{python3_pkgversion}
%{?python_provide:%python_provide python%{python3_pkgversion}-%{name}}

%description -n python%{python3_pkgversion}-%{name}
This package contains python%{python3_pkgversion} bindings to Xen tools. Especially xen.lowlevel.xs
and xen.lowlevel.xc modules.
# END QUBES SPECIFIC PART

%package libs
Summary: Libraries for Xen tools
Requires: xen-licenses
# toolstack <-> stubdomain API change
Conflicts: xen-hvm-stubdom-linux < 1.1.0

%description libs
This package contains the libraries needed to run applications
which manage Xen virtual machines.


%package runtime
Summary: Core Xen runtime environment
Requires: xen-libs = %{epoch}:%{version}-%{release}
#Requires: /usr/bin/qemu-img /usr/bin/qemu-nbd
Requires: /usr/bin/qemu-img
# Ensure we at least have a suitable kernel installed, though we can't
# force user to actually boot it.
Requires: xen-hypervisor-abi = %{hv_abi}
%if %with_systemd_presets
Requires(post): systemd
Requires(preun): systemd
%endif

%description runtime
This package contains the runtime programs and daemons which
form the core Xen userspace environment.


%package hypervisor
Summary: Libraries for Xen tools
Provides: xen-hypervisor-abi = %{hv_abi}
Requires: xen-licenses

%description hypervisor
This package contains the Xen hypervisor


%if %build_docs
%package doc
Summary: Xen documentation
BuildArch: noarch
Requires: xen-licenses
# for the docs
%if "%dist" >= ".fc18"
BuildRequires: texlive-times texlive-courier texlive-helvetic texlive-ntgclass
%endif
BuildRequires: transfig texi2html ghostscript texlive-latex
BuildRequires: perl(Pod::Man) perl(Pod::Text) texinfo graphviz
# optional requires for more documentation
BuildRequires: pandoc discount
BuildRequires: discount

%description doc
This package contains the Xen documentation.
%endif


%package devel
Summary: Development libraries for Xen tools
Requires: xen-libs = %{epoch}:%{version}-%{release}
Requires: libuuid-devel

%description devel
This package contains what's needed to develop applications
which manage Xen virtual machines.


%package licenses
Summary: License files from Xen source

%description licenses
This package contains the license files from the source used
to build the xen packages.


%if %build_ocaml
%package ocaml
Summary: Ocaml libraries for Xen tools
Requires: ocaml-runtime, xen-libs = %{epoch}:%{version}-%{release}

%description ocaml
This package contains libraries for ocaml tools to manage Xen
virtual machines.


%package ocaml-devel
Summary: Ocaml development libraries for Xen tools
Requires: xen-ocaml = %{epoch}:%{version}-%{release}

%description ocaml-devel
This package contains libraries for developing ocaml tools to
manage Xen virtual machines.
%endif

# BEGIN QUBES SPECIFIC PART
%package qemu-tools
Summary: Qemu disk tools bundled with Xen
Provides: qemu-img
Conflicts: qemu-img

%description qemu-tools
This package contains symlinks to qemu tools (qemu-img, qemu-nbd)
budled with Xen, making them available for general use.

%package qubes-vm
Summary: Xen files required in Qubes VM
Requires: xen-libs = %{epoch}:%{version}-%{release}
Conflicts: xen
Provides: xen-qubes-vm-essentials = %{epoch}:%{version}-%{release}

%description qubes-vm
Just a few xenstore-* tools and Xen hotplug scripts needed by Qubes VMs
# END QUBES SPECIFIC PART

%prep
%autosetup -p1 -n %{name}-%{upstream_version}

# copy xen hypervisor .config file to change settings
cp -v %{SOURCE3} xen/.config


%build
%if !%build_ocaml
%define ocaml_flags OCAML_TOOLS=n
%endif
%if %build_efi
%define efi_flags EFI_VENDOR=qubes
mkdir -p dist/install/boot/efi/efi/qubes
%endif
%if %build_ocaml
mkdir -p dist/install%{_libdir}/ocaml/stublibs
%endif
%define seabiosloc /usr/share/seabios/bios-256k.bin
#export XEN_VENDORVERSION="-%{release}"
export EXTRA_CFLAGS_XEN_TOOLS="$RPM_OPT_FLAGS -Wno-error=declaration-after-statement"
export EXTRA_CFLAGS_QEMU_TRADITIONAL="$RPM_OPT_FLAGS"
export EXTRA_CFLAGS_QEMU_XEN="$RPM_OPT_FLAGS"
export PYTHON="%{__python3}"
export KCONFIG_CONFIG=%{SOURCE3}
export XEN_CONFIG_EXPERT=y
%if %build_hyp
%if %build_crosshyp
%define efi_flags LD_EFI=false
XEN_TARGET_ARCH=x86_64 make %{?_smp_mflags} %{?efi_flags} prefix=/usr xen CC="/usr/bin/x86_64-linux-gnu-gcc `echo $RPM_OPT_FLAGS | sed -e 's/-m32//g' -e 's/-march=i686//g' -e 's/-mtune=atom//g' -e 's/-specs=\/usr\/lib\/rpm\/redhat\/redhat-annobin-cc1//g' -e 's/-fstack-clash-protection//g' -e 's/-mcet//g' -e 's/-fcf-protection//g'`"
%else
%ifarch armv7hl
make %{?_smp_mflags} %{?efi_flags} prefix=/usr xen CC="gcc `echo $RPM_OPT_FLAGS | sed -e 's/-mfloat-abi=hard//g' -e 's/-march=armv7-a//g'`"
%else
%ifarch aarch64
make %{?_smp_mflags} %{?efi_flags} prefix=/usr xen CC="gcc $RPM_OPT_FLAGS"
%else
make %{?_smp_mflags} %{?efi_flags} prefix=/usr xen CC="gcc `echo $RPM_OPT_FLAGS | sed -e 's/-specs=\/usr\/lib\/rpm\/redhat\/redhat-annobin-cc1//g' -e 's/-fcf-protection//g'`"
%endif
%endif
%endif
%endif
%if ! %build_qemutrad
CONFIG_EXTRA="--disable-qemu-traditional"
%else
CONFIG_EXTRA=""
%endif
%if ! %build_stubdom
CONFIG_EXTRA="$CONFIG_EXTRA --disable-stubdom"
%endif
%if %build_ovmf
CONFIG_EXTRA="$CONFIG_EXTRA --with-system-ovmf=%{_libexecdir}/%{name}/boot/ovmf.bin"
%endif
# BEGIN QUBES SPECIFIC PART
%ifnarch armv7hl aarch64
#CONFIG_EXTRA="$CONFIG_EXTRA --with-system-ipxe=/usr/share/ipxe"
CONFIG_EXTRA="$CONFIG_EXTRA --disable-ipxe --disable-rombios"
%endif
CONFIG_EXTRA="$CONFIG_EXTRA --with-extra-qemuu-configure-args='--disable-spice'"
export PATH="/usr/bin:$PATH"
autoreconf
# END QUBES SPECIFIC PART
./configure --prefix=%{_prefix} --libdir=%{_libdir} --libexecdir=%{_libexecdir} --with-system-seabios=%{seabiosloc} --with-linux-backend-modules="xen-evtchn xen-gntdev xen-gntalloc xen-blkback xen-netback xen-pciback xen-scsiback xen-acpi-processor" $CONFIG_EXTRA
make %{?_smp_mflags} %{?ocaml_flags} prefix=/usr tools
%if %build_docs
make                 prefix=/usr docs
%endif
export RPM_OPT_FLAGS_RED=`echo $RPM_OPT_FLAGS | sed -e 's/-m64//g' -e 's/--param=ssp-buffer-size=4//g' -e's/-fstack-protector-strong//'`
%ifarch %{ix86}
export EXTRA_CFLAGS_XEN_TOOLS="$RPM_OPT_FLAGS_RED"
%endif
%if %build_stubdom
%ifnarch armv7hl aarch64
make mini-os-dir
make -C stubdom build
%endif
%ifarch x86_64
export EXTRA_CFLAGS_XEN_TOOLS="$RPM_OPT_FLAGS_RED"
XEN_TARGET_ARCH=x86_32 make -C stubdom pv-grub
%endif
%endif


%install
#export XEN_VENDORVERSION="-%{release}"
export EXTRA_CFLAGS_XEN_TOOLS="$RPM_OPT_FLAGS"
export EXTRA_CFLAGS_QEMU_TRADITIONAL="$RPM_OPT_FLAGS"
export EXTRA_CFLAGS_QEMU_XEN="$RPM_OPT_FLAGS"
export PATH="/usr/bin:$PATH"
export KCONFIG_CONFIG=%{SOURCE3}
export XEN_CONFIG_EXPERT=y
rm -rf %{buildroot}
mkdir -p %{buildroot}
cp -prlP dist/install/* %{buildroot}
%if %build_stubdom
%ifnarch armv7hl aarch64
make DESTDIR=%{buildroot} %{?ocaml_flags} prefix=/usr install-stubdom
%endif
%endif
%if %build_efi
mkdir -p %{buildroot}/boot/efi/efi/qubes
mv %{buildroot}/boot/efi/efi %{buildroot}/boot/efi/EFI
%endif
%if %build_xsm
# policy file should be in /boot/flask
mkdir %{buildroot}/boot/flask
mv %{buildroot}/boot/xenpolicy* %{buildroot}/boot/flask
%else
rm -f %{buildroot}/boot/xenpolicy*
rm -f %{buildroot}/usr/sbin/flask-*
%endif

############ debug packaging: list files ############

find %{buildroot} -print | xargs ls -ld | sed -e 's|.*%{buildroot}||' > f1.list

############ kill unwanted stuff ############

# stubdom: newlib
rm -rf %{buildroot}/usr/*-xen-elf

# hypervisor symlinks
rm -rf %{buildroot}/boot/xen-%{hv_abi}.gz
rm -rf %{buildroot}/boot/xen-4.gz
rm -rf %{buildroot}/boot/xen.gz
%if !%build_hyp
rm -rf %{buildroot}/boot
%endif

# silly doc dir fun
rm -fr %{buildroot}%{_datadir}/doc/xen
rm -rf %{buildroot}%{_datadir}/doc/qemu

# Pointless helper
rm -f %{buildroot}%{_sbindir}/xen-python-path

# qemu stuff (unused or available from upstream)
rm -rf %{buildroot}/usr/share/xen/man
rm -rf %{buildroot}/usr/share/qemu-xen/icons
rm -rf %{buildroot}/usr/share/qemu-xen/applications
# BEGIN QUBES SPECIFIC PART
ln -s ../libexec/%{name}/bin/qemu-img %{buildroot}/%{_bindir}/qemu-img
ln -s ../libexec/%{name}/bin/qemu-nbd %{buildroot}/%{_bindir}/qemu-nbd
# END QUBES SPECIFIC PART
for file in bios.bin openbios-sparc32 openbios-sparc64 ppc_rom.bin \
         pxe-e1000.bin pxe-ne2k_pci.bin pxe-pcnet.bin pxe-rtl8139.bin \
         vgabios.bin vgabios-cirrus.bin video.x openbios-ppc bamboo.dtb
do
	rm -f %{buildroot}/%{_datadir}/xen/qemu/$file
done

# BEGIN QUBES SPECIFIC PART
rm -f %{buildroot}/usr/libexec/qemu-bridge-helper
# END QUBES SPECIFIC PART

# README's not intended for end users
rm -f %{buildroot}/%{_sysconfdir}/xen/README*

# standard gnu info files
rm -rf %{buildroot}/usr/info

# adhere to Static Library Packaging Guidelines
rm -rf %{buildroot}/%{_libdir}/*.a

%if %build_efi
# clean up extra efi files
rm -rf %{buildroot}/%{_libdir}/efi
%ifarch %{ix86}
rm -rf %{buildroot}/usr/lib64/efi
%endif
%endif

%if ! %build_ocaml
rm -rf %{buildroot}/%{_unitdir}/oxenstored.service
%endif

%if %build_ovmf
cat /usr/share/OVMF/OVMF_{VARS,CODE}.fd >%{buildroot}%{_libexecdir}/%{name}/boot/ovmf.bin
%endif

############ fixup files in /etc ############

# logrotate
mkdir -p %{buildroot}%{_sysconfdir}/logrotate.d/
install -m 644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# init scripts
rm %{buildroot}%{_sysconfdir}/rc.d/init.d/xen-watchdog
rm %{buildroot}%{_sysconfdir}/rc.d/init.d/xencommons
rm %{buildroot}%{_sysconfdir}/rc.d/init.d/xendomains
rm %{buildroot}%{_sysconfdir}/rc.d/init.d/xendriverdomain
# BEGIN QUBES SPECIFIC PART
rm %{buildroot}%{_sysconfdir}/sysconfig/xendomains
cp %{SOURCE32} %{buildroot}/usr/lib/modules-load.d/xen.conf

# get rid of standard domain starting scripts
rm %{buildroot}%{_unitdir}/xen-qemu-dom0-disk-backend.service
rm %{buildroot}%{_unitdir}/xendomains.service

# unused and dangerous
rm -f %{buildroot}/%{_bindir}/pygrub
rm -rf %{buildroot}/%{python3_sitearch}/pygrub*
# END QUBES SPECIFIC PART

############ create dirs in /var ############

mkdir -p %{buildroot}%{_localstatedir}/lib/xen/images
mkdir -p %{buildroot}%{_localstatedir}/log/xen/console

############ create symlink for x86_64 for compatibility with 4.4 ############

%if "%{_libdir}" != "/usr/lib"
ln -s %{_libexecdir}/%{name} %{buildroot}/%{_libdir}/%{name}
%endif

# BEGIN QUBES SPECIFIC PART
# don't create symlink to qemu-system-i386
ln -s ../sbin/xl %{buildroot}/%{_bindir}/xl
# END QUBES SPECIFIC PART

############ debug packaging: list files ############

find %{buildroot} -print | xargs ls -ld | sed -e 's|.*%{buildroot}||' > f2.list
diff -u f1.list f2.list || true

############ assemble license files ############

mkdir licensedir
# avoid licensedir to avoid recursion, also stubdom/ioemu and dist
# which are copies of files elsewhere
find . -path licensedir -prune -o -path stubdom/ioemu -prune -o \
  -path dist -prune -o -name COPYING -o -name LICENSE | while read file; do
  mkdir -p licensedir/`dirname $file`
  install -m 644 $file licensedir/$file
done

############ all done now ############

# BEGIN QUBES SPECIFIC PART
# %post
# %if %with_systemd_presets
# %systemd_post xendomains.service
# %else
# if [ $1 == 1 ]; then
#   /bin/systemctl enable xendomains.service
# fi
# %endif

# %preun
# %if %with_systemd_presets
# %systemd_preun xendomains.service
# %else
# if [ $1 == 0 ]; then
# /bin/systemctl disable xendomains.service
# fi
# %endif
# END QUBES SPECIFIC PART

%post runtime
%if %with_systemd_presets
%systemd_post xenstored.service xenconsoled.service xen-init-dom0.service
%else
if [ $1 == 1 ]; then
  /bin/systemctl enable xenstored.service
  /bin/systemctl enable xenconsoled.service
  /bin/systemctl enable xen-init-dom0.service
fi
%endif

%preun runtime
%if %with_systemd_presets
%systemd_preun xenstored.service xenconsoled.service xen-init-dom0.service
%else
if [ $1 == 0 ]; then
  /bin/systemctl disable xenstored.service
  /bin/systemctl disable xenconsoled.service
  /bin/systemctl disable xen-init-dom0.service
fi
%endif

%post qubes-vm
# Unconditionally enable this service in Qubes VM
systemctl enable xendriverdomain.service >/dev/null 2>&1 || :

%preun qubes-vm
%systemd_preun xendriverdomain.service

%post libs

/sbin/ldconfig

%ldconfig_scriptlets libs

%if %build_hyp
%post hypervisor
%if %build_efi
XEN_EFI_VERSION=$(echo %{upstream_version} | sed -e 's/rc./rc/')
EFI_DIR=$(efibootmgr -v 2>/dev/null | awk '
      /^BootCurrent:/ { current=$2; }
      /^Boot....\* / {
          if ("Boot" current "*" == $1) {
              sub(".*File\\(", "");
              sub("\\\\xen.efi\\).*", "");
              gsub("\\\\", "/");
              print;
          }
      }')
# FAT (on ESP) does not support symlinks
# override the file on purpose
if [ -n "${EFI_DIR}" -a -d "/boot/efi${EFI_DIR}" ]; then
  cp -pf /boot/efi/EFI/qubes/xen-$XEN_EFI_VERSION.efi /boot/efi${EFI_DIR}/xen.efi
else
  cp -pf /boot/efi/EFI/qubes/xen-$XEN_EFI_VERSION.efi /boot/efi/EFI/qubes/xen.efi
fi
%endif

if [ -f /boot/efi/EFI/qubes/xen.cfg ]; then
    if ! grep -q smt=off /boot/efi/EFI/qubes/xen.cfg; then
        sed -i -e 's:^options=.*:\0 smt=off:' /boot/efi/EFI/qubes/xen.cfg
    fi
    if ! grep -q gnttab_max_frames /boot/efi/EFI/qubes/xen.cfg; then
        sed -i -e 's:^options=.*:\0 gnttab_max_frames=2048 gnttab_max_maptrack_frames=4096:' /boot/efi/EFI/qubes/xen.cfg
    fi
fi

if [ -f /etc/default/grub ]; then
    if ! grep -q smt=off /etc/default/grub; then
        echo 'GRUB_CMDLINE_XEN_DEFAULT="$GRUB_CMDLINE_XEN_DEFAULT smt=off"' >> /etc/default/grub
        grub2-mkconfig -o /boot/grub2/grub.cfg
    fi
    if ! grep -q gnttab_max_frames /etc/default/grub; then
        echo 'GRUB_CMDLINE_XEN_DEFAULT="$GRUB_CMDLINE_XEN_DEFAULT gnttab_max_frames=2048 gnttab_max_maptrack_frames=4096"' >> /etc/default/grub
        grub2-mkconfig -o /boot/grub2/grub.cfg
    fi
fi

if [ $1 == 1 -a -f /sbin/grub2-mkconfig ]; then
  if [ -f /boot/grub2/grub.cfg ]; then
    /sbin/grub2-mkconfig -o /boot/grub2/grub.cfg
  fi
  if [ -f /boot/efi/EFI/qubes/grub.cfg ]; then
    /sbin/grub2-mkconfig -o /boot/efi/EFI/qubes/grub.cfg
  fi
fi

%postun hypervisor
if [ -f /sbin/grub2-mkconfig ]; then
  if [ -f /boot/grub2/grub.cfg ]; then
    /sbin/grub2-mkconfig -o /boot/grub2/grub.cfg
  fi
  if [ -f /boot/efi/EFI/qubes/grub.cfg ]; then
    /sbin/grub2-mkconfig -o /boot/efi/EFI/qubes/grub.cfg
  fi
fi
%endif

%if %build_ocaml
%post ocaml
%if %with_systemd_presets
%systemd_post oxenstored.service
%else
if [ $1 == 1 ]; then
  /bin/systemctl enable oxenstored.service
fi
%endif

%preun ocaml
%if %with_systemd_presets
%systemd_preun oxenstored.service
%else
if [ $1 == 0 ]; then
  /bin/systemctl disable oxenstored.service
fi
%endif
%endif

# Base package only contains XenD/xm python stuff
#files -f xen-xm.lang
%files
%doc COPYING README
%{_bindir}/xencons

# BEGIN QUBES SPECIFIC PART
%files -n python%{python3_pkgversion}-%{name}
%{python3_sitearch}/%{name}
%{python3_sitearch}/xen-*.egg-info
# END QUBES SPECIFIC PART

%files libs
%{_libdir}/*.so.*
%{_libdir}/xenfsimage

# All runtime stuff except for XenD/xm python stuff
%files runtime
# Hotplug rules

%dir %attr(0700,root,root) %{_sysconfdir}/%{name}
%dir %attr(0700,root,root) %{_sysconfdir}/%{name}/scripts/
%config %attr(0700,root,root) %{_sysconfdir}/%{name}/scripts/*

%{_sysconfdir}/bash_completion.d/xl.sh

%{_unitdir}/proc-xen.mount
%{_unitdir}/var-lib-xenstored.mount
%{_unitdir}/xenstored.service
%{_unitdir}/xenconsoled.service
%{_unitdir}/xen-watchdog.service
# BEGIN QUBES SPECIFIC PART
%{_unitdir}/xen-init-dom0.service
%exclude %{_unitdir}/xendriverdomain.service
# END QUBES SPECIFIC PART
/usr/lib/modules-load.d/xen.conf

%config(noreplace) %{_sysconfdir}/sysconfig/xencommons
%config(noreplace) %{_sysconfdir}/xen/xl.conf
%config(noreplace) %{_sysconfdir}/xen/cpupool
%config(noreplace) %{_sysconfdir}/xen/xlexample*

# Rotate console log files
%config(noreplace) %{_sysconfdir}/logrotate.d/xen

# Programs run by other programs
%dir %{_libexecdir}/%{name}
%dir %{_libexecdir}/%{name}/bin
%attr(0700,root,root) %{_libexecdir}/%{name}/bin/*
# QEMU runtime files
%if %build_qemutrad
%ifnarch armv7hl aarch64
%dir %{_datadir}/%{name}/qemu
%dir %{_datadir}/%{name}/qemu/keymaps
%{_datadir}/%{name}/qemu/keymaps/*
%endif
%endif
# BEGIN QUBES SPECIFIC PART
%dir %{_datadir}/qemu-xen
%dir %{_datadir}/qemu-xen/qemu
%{_datadir}/qemu-xen/qemu/*
# END QUBES SPECIFIC PART

# man pages
%if %build_docs
%{_mandir}/man1/xentop.1*
%{_mandir}/man1/xentrace_format.1*
%{_mandir}/man8/xentrace.8*
%{_mandir}/man1/xl.1*
%{_mandir}/man5/xl.cfg.5*
%{_mandir}/man5/xl.conf.5*
%{_mandir}/man5/xlcpupool.cfg.5*
%{_mandir}/man1/xenstore*
%{_mandir}/man1/xenhypfs.1*
%{_mandir}/man5/xl-disk-configuration.5.gz
%{_mandir}/man7/xen-pci-device-reservations.7.gz
%{_mandir}/man7/xen-tscmode.7.gz
%{_mandir}/man7/xen-vtpm.7.gz
%{_mandir}/man7/xen-vtpmmgr.7.gz
%{_mandir}/man5/xl-network-configuration.5.gz
%{_mandir}/man7/xen-pv-channel.7.gz
%{_mandir}/man7/xl-numa-placement.7.gz
%{_mandir}/man7/xen-vbd-interface.7.gz
%endif

%{python3_sitearch}/xenfsimage*.so
%{python3_sitearch}/grub

# The firmware
%ifarch %{ix86} x86_64
%dir %{_libexecdir}/%{name}/boot
%{_libexecdir}/xen/boot/hvmloader
%ifnarch %{ix86}
%{_libexecdir}/%{name}/boot/xen-shim
/usr/lib/debug%{_libexecdir}/xen/boot/xen-shim-syms
%endif
%if %build_ovmf
%{_libexecdir}/xen/boot/ovmf.bin
%endif
%if %build_stubdom
%{_libexecdir}/xen/boot/ioemu-stubdom.gz
%{_libexecdir}/xen/boot/xenstore-stubdom.gz
%{_libexecdir}/xen/boot/pv-grub*.gz
%endif
%endif
%if "%{_libdir}" != "/usr/lib"
%{_libdir}/%{name}
%endif
%ghost /usr/lib/%{name}
# General Xen state
%dir %{_localstatedir}/lib/%{name}
%dir %{_localstatedir}/lib/%{name}/dump
%dir %{_localstatedir}/lib/%{name}/images
# Xenstore persistent state
%dir %{_localstatedir}/lib/xenstored
# Xenstore runtime state
%ghost %{_localstatedir}/run/xenstored

# All xenstore CLI tools
%{_bindir}/xenstore
%{_bindir}/xenstore-*
%{_bindir}/xentrace*
#%%{_bindir}/remus
# XSM
%if %build_xsm
%{_sbindir}/flask-*
%endif
# Misc stuff
%ifnarch armv7hl aarch64
%{_bindir}/xen-detect
%endif
%{_bindir}/vchan-socket-proxy
%{_bindir}/xencov_split
%ifnarch armv7hl aarch64
%{_sbindir}/gdbsx
%{_sbindir}/xen-kdd
%endif
%ifnarch armv7hl aarch64
%{_sbindir}/xen-hptool
%{_sbindir}/xen-hvmcrash
%{_sbindir}/xen-hvmctx
%endif
%{_sbindir}/xenconsoled
%{_sbindir}/xenlockprof
%{_sbindir}/xenmon
%{_sbindir}/xentop
%{_sbindir}/xentrace_setmask
%{_sbindir}/xenbaked
%{_sbindir}/xenstored
%{_sbindir}/xenpm
%{_sbindir}/xenpmd
%{_sbindir}/xenperf
%{_sbindir}/xenwatchdogd
%{_sbindir}/xl
%{_sbindir}/xen-ucode
%{_sbindir}/xenhypfs
%ifnarch armv7hl aarch64
%{_sbindir}/xen-lowmemd
%endif
%{_sbindir}/xencov
%ifnarch armv7hl aarch64
%{_sbindir}/xen-mfndump
%endif
%{_bindir}/xenalyze
%{_sbindir}/xentrace
%{_sbindir}/xentrace_setsize
%ifnarch armv7hl aarch64
%{_bindir}/xen-cpuid
%endif
%{_sbindir}/xen-livepatch
%{_sbindir}/xen-diag
# BEGIN QUBES SPECIFIC PART
%{_bindir}/xl
# END QUBES SPECIFIC PART

# Xen logfiles
%dir %attr(0700,root,root) %{_localstatedir}/log/xen
# Guest/HV console logs
%dir %attr(0700,root,root) %{_localstatedir}/log/xen/console

%files hypervisor
%if %build_hyp
%defattr(-,root,root)
%ifnarch armv7hl aarch64
/boot/xen-*.gz
# BEGIN QUBES SPECIFIC PART
# /boot/xen.gz
# END QUBES SPECIFIC PART
/boot/xen*.config
%else
/boot/xen*
%endif
%if %build_xsm
%dir %attr(0755,root,root) /boot/flask
/boot/flask/xenpolicy*
%endif
%if %build_efi
/boot/efi/EFI/qubes/*.efi
%endif
/usr/lib/debug/xen*
%endif

%if %build_docs
%files doc
%doc docs/misc/
%doc dist/install/usr/share/doc/xen/html
%endif

%files devel
%{_includedir}/*.h
%dir %{_includedir}/xen
%{_includedir}/xen/*
%dir %{_includedir}/xenstore-compat
%{_includedir}/xenstore-compat/*
%{_libdir}/*.so
%{_libdir}/pkgconfig/*

%files licenses
%doc licensedir/*

%if %build_ocaml
%files ocaml
%{_libdir}/ocaml/xen*
%exclude %{_libdir}/ocaml/xen*/*.a
%exclude %{_libdir}/ocaml/xen*/*.cmxa
%exclude %{_libdir}/ocaml/xen*/*.cmx
%{_libdir}/ocaml/stublibs/*.so
%{_libdir}/ocaml/stublibs/*.so.owner
%{_sbindir}/oxenstored
%config(noreplace) %{_sysconfdir}/xen/oxenstored.conf
%{_unitdir}/oxenstored.service

%files ocaml-devel
%{_libdir}/ocaml/xen*/*.a
%{_libdir}/ocaml/xen*/*.cmxa
%{_libdir}/ocaml/xen*/*.cmx
%endif

# BEGIN QUBES SPECIFIC PART
%files qemu-tools
/usr/bin/qemu-img
/usr/bin/qemu-nbd

%files qubes-vm
%{_bindir}/xenstore
%{_bindir}/xenstore-*
%{_sbindir}/xl
%{_unitdir}/xendriverdomain.service
%config(noreplace) %{_sysconfdir}/xen/xl.conf

%dir %attr(0700,root,root) %{_sysconfdir}/xen
%dir %attr(0700,root,root) %{_sysconfdir}/xen/scripts/
%config %attr(0700,root,root) %{_sysconfdir}/xen/scripts/*

# General Xen state
%dir %{_localstatedir}/lib/xen
%dir %{_localstatedir}/lib/xen/dump

# Xen logfiles
%dir %attr(0700,root,root) %{_localstatedir}/log/xen

# Python modules
%dir %{python3_sitearch}/xen
%{python3_sitearch}/xen/__init__.*
%{python3_sitearch}/xen/lowlevel
%{python3_sitearch}/xen-*.egg-info
# END QUBES SPECIFIC PART

%changelog
* Tue Sep 22 2020 Qubes OS Team <qubes-devel@googlegroups.com>
- For complete changelog see: /

* Tue Sep 22 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 85f4a51
- version 4.14.0-4

* Tue Sep 22 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 3633266
- Apply XSA-337, XSA-338, XSA-340, XSA-342, XSA-343

* Wed Sep 16 2020 Frédéric Pierret (fepitre) <frederic.pierret@qubes-os.org> - 28b1fb2
- travis: exclude conflicting packages at install phase

* Mon Sep 14 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 6c426f6
- version 4.14.0-3

* Mon Sep 14 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 3caeccc
- debian: fix in-vm assumed xen-utils package version

* Sat Sep 12 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 6e03e0d
- version 4.14.0-2

* Sat Sep 12 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - cefb118
- rpm: include xenhypfs tool

* Sat Sep 12 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 62c3b97
- rpm: fix qemu-xen packaging

* Sat Sep 12 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 56591c0
- rpm: remove remaining pygrub part

* Sat Sep 12 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 853d1dd
- rpm: skip stubdom build at configure stage too

* Sat Sep 12 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 13060f3
- Fix seabios path

* Mon Aug 31 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 1ad23b8
- Add gcc warnings fixes to Debian package too

* Mon Aug 31 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 343c2ae
- version 4.14.0-1

* Mon Aug 31 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 5f89d2d
- Adjust "Fix IGD passthrough with linux stubdomain" for Xen 4.14

* Mon Aug 31 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 6370714
- rpm: adjust dependencies for stubdomain API change

* Thu Aug 20 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - f7f9a69
- Update Debian and Arch packaging and patches for Xen 4.14

* Thu Aug 20 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 7dfa12b
- Update to Xen 4.14.0

* Mon Aug 10 2020 Frédéric Pierret (fepitre) <frederic.pierret@qubes-os.org> - 4cabc08
- spec: user python3_pkgversion macro

* Fri Aug 07 2020 Frédéric Pierret (fepitre) <frederic.pierret@qubes-os.org> - f7f2427
- Update travis

* Wed Jun 17 2020 Artur Puzio <contact@puzio.waw.pl> - 08af9e0
- IGD passthrough fix

* Sat Jun 13 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 9783e07
- version 4.13.1-4

* Sat Jun 13 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 7a8e063
- Backport fix for domain shutdown cleanup

* Sun Jun 07 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - bcb6336
- Automatically enable gfx_passthru option when needed

* Wed May 27 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 19c9fcb
- Update to 4.13.1

* Sat May 16 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 9178ad6
- version 4.13.0-3

* Sun Apr 05 2020 Frédéric Pierret (fepitre) <frederic.pierret@qubes-os.org> - 191e701
- Add gcc10, ocaml4.10 and pygrub fixes from Fedora

* Wed Mar 11 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - d7fed68
- version 4.13.0-2

* Wed Mar 11 2020 Paweł Marczewski <pawel@invisiblethingslab.com> - 2949390
- libxl: fix cleanup bug in initiate_domain_create()

* Mon Mar 09 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - cecee08
- version 4.13.0-1

* Thu Mar 05 2020 Paweł Marczewski <pawel@invisiblethingslab.com> - 29a855b
- libxl: wait for console path before firing console_available

* Fri Feb 28 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 0482e33
- Increase default gnttab_max_frames and gnttab_max_maptrack_frames

* Tue Feb 11 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 06c4b6d
- Apply fix for HYPERVISOR bit in calculated CPUID - fix resume on AMD

* Sun Jan 19 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - d7d60e8
- Disable commonly broken EFI GetTime() call

* Sun Jan 19 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 7f94ed6
- version 4.13.0-0.3

* Sat Jan 18 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 703e47f
- Disable vkb device by default

* Sat Jan 18 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 9809eb6
- Update patch for suspending stubdomain without QMP

* Fri Jan 17 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 7a6b551
- version 4.13.0-0.2

* Sat Jan 11 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 2cdb27e
- Add a patch for crash after resume

* Sat Jan 04 2020 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 066f02a
- version 4.13.0-0.1

* Wed Dec 25 2019 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 9774d93
- Allow stubdomain to control interupts of PCI device

* Wed Dec 25 2019 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 13f288c
- rpm: Fix file list

* Wed Dec 25 2019 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - d4e1336
- Fix stubdom-linux patch series

* Sat Dec 21 2019 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - dbd354d
- rpm: add R(post,preun) to xen-runtime package too

* Sat Dec 21 2019 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - a1fd430
- Revert "Abort the major upgrade if any VM is running"

* Sat Dec 21 2019 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - be47c3e
- rpm: re-enable BR: pandoc

* Sat Dec 21 2019 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 2f63c88
- travis: switch dom0 to fc31

* Sat Dec 21 2019 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - a1fc0b0
- Don't use distfiles mirror anymore

* Sat Dec 21 2019 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - db72c67
- Update Debian packaging for 4.13

* Sat Dec 21 2019 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 2adac38
- Update to 4.13.0

* Sat Dec 21 2019 Marek Marczykowski-Górecki <marmarek@invisiblethingslab.com> - 30d45a6
- Improve -rc handling once again

