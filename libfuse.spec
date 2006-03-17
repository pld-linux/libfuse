#
# Condtional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# without smp packages
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)
#
%ifarch sparc
%undefine	with_smp
%endif
#
Summary:	Filesystem in Userspace
Summary(pl):	System plików w przestrzeni u¿ytkownika
Name:		libfuse
Version:	2.5.2
%define		_rel	3
Release:	%{_rel}
Epoch:		0
License:	GPL v2
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/fuse/fuse-%{version}.tar.gz
# Source0-md5:	ea565debe6c7486963bef05c45c50361
Source1:	fuse.conf
Patch0:		kernel-misc-fuse-Makefile.am.patch
URL:		http://fuse.sourceforge.net/
BuildRequires:	autoconf
BuildRequires:	automake
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.217
%endif
BuildRequires:	libtool
BuildRequires:	sed >= 4.0
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the Linux kernel. FUSE also
aims to provide a secure method for non privileged users to create and
mount their own filesystem implementations.

This package contains a shared library.

%description -l pl
FUSE stanowi prosty interfejs dla programów dzia³aj±cych w przestrzeni
u¿ytkownika eksportuj±cy wirtualny system plików do j±dra Linuksa.
FUSE ma równie¿ na celu udostêpnienie bezpiecznej metody tworzenia i
montowania w³asnych implementacji systemów plików przez zwyk³ych
(nieuprzywilejowanych) u¿ytkowników.

Ten pakiet zawiera bibliotekê wspó³dzielon±.

%package devel
Summary:	Filesytem in Userspace - Development header files
Summary(pl):	System plików w przestrzeni u¿ytkownika - pliki nag³ówkowe
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{_rel}

%description devel
Libfuse library header files.

%description devel -l pl
Pliki nag³ówkowe biblioteki libfuse.

%package static
Summary:	Filesytem in Userspace - static library
Summary(pl):	System plików w przestrzeni u¿ytkownika - biblioteka statyczna
Group:		Development/Libraries
Release:	%{_rel}
Requires:	libfuse-devel = %{epoch}:%{version}-%{_rel}

%description static
Static libfuse libraries.

%description static -l pl
Statyczna biblioteka libfuse.

%package -n kernel-misc-fuse
Summary:	Filesystem in Userspace
Summary(pl):	System plików w przestrzeni u¿ytkownika
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_up
Requires(postun):	%releq_kernel_up
%endif

%description -n kernel-misc-fuse
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the Linux kernel. FUSE also
aims to provide a secure method for non privileged users to create and
mount their own filesystem implementations.

%description -n kernel-misc-fuse -l pl
FUSE stanowi prosty interfejs dla programów dzia³aj±cych w przestrzeni
u¿ytkownika eksportuj±cy wirtualny system plików do j±dra Linuksa.
FUSE ma równie¿ na celu udostêpnienie bezpiecznej metody tworzenia i
montowania w³asnych implementacji systemów plików przez zwyk³ych
(nieuprzywilejowanych) u¿ytkowników.

%package -n kernel-smp-misc-fuse
Summary:	Filesystem in Userspace
Summary(pl):	System plików w przestrzeni u¿ytkownika
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Provides:	kernel-misc-fuse
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif

%description -n kernel-smp-misc-fuse
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the Linux kernel. FUSE also
aims to provide a secure method for non privileged users to create and
mount their own filesystem implementations.

%description -n kernel-smp-misc-fuse -l pl
FUSE stanowi prosty interfejs dla programów dzia³aj±cych w przestrzeni
u¿ytkownika eksportuj±cy wirtualny system plików do j±dra Linuksa.
FUSE ma równie¿ na celu udostêpnienie bezpiecznej metody tworzenia i
montowania w³asnych implementacji systemów plików przez zwyk³ych
(nieuprzywilejowanych) u¿ytkowników.

%prep
%setup -q -n fuse-%{version}
%patch0 -p1

sed -i '/FUSERMOUNT_PROG/s,fusermount,%{_bindir}/fusermount,' lib/mount.c

%build
%{__libtoolize}
%{__aclocal}
%{__autoheader}
%{__autoconf}
%{__automake}
%configure \
	--enable-kernel-module \
	--enable-lib \
	--enable-util \
	--with-kernel=%{_kernelsrcdir}

%if %{with userspace}
cp kernel/fuse_kernel.h include/
for DIR in include lib util; do
%{__make} -C $DIR
done
%endif

%if %{with kernel}
cd kernel
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	install -d o/include/linux
	ln -sf %{_kernelsrcdir}/config-$cfg o/.config
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg o/Module.symvers
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h o/include/linux/autoconf.h
%if %{with dist_kernel}
	%{__make} -C %{_kernelsrcdir} O=$PWD/o prepare scripts
%else
	install -d o/include/config
	touch o/include/config/MARKER
	ln -sf %{_kernelsrcdir}/scripts o/scripts
%endif
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		SYSSRC=%{_kernelsrcdir} \
		SYSOUT=$PWD/o \
		M=$PWD O=$PWD/o \
		%{?with_verbose:V=1}

	mv fuse.ko fuse-$cfg.ko
done
cd -
%endif

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_pkgconfigdir},%{_sysconfdir}}

%if %{with userspace}
for DIR in include lib util; do
%{__make} -C $DIR install \
	DESTDIR=$RPM_BUILD_ROOT
done

install fuse.pc $RPM_BUILD_ROOT%{_pkgconfigdir}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}
mv $RPM_BUILD_ROOT%{_sysconfdir}/udev/rules.d/{40-,}fuse.rules
%endif

%if %{with kernel}
cd kernel
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/fs
install fuse-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/fs/fuse.ko
%if %{with smp} && %{with dist_kernel}
install fuse-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/fs/fuse.ko
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%post -n kernel-misc-fuse
%depmod %{_kernel_ver}

%postun -n kernel-misc-fuse
%depmod %{_kernel_ver}

%post -n kernel-smp-misc-fuse
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-misc-fuse
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README NEWS ChangeLog AUTHORS doc/*
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fuse.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/udev/rules.d/fuse.rules
%attr(755,root,root) %{_bindir}/fusermount
%attr(755,root,root) /sbin/mount.fuse
%attr(755,root,root) %{_libdir}/libfuse.so.*.*.*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libfuse.so
%{_libdir}/libfuse.la
%{_includedir}/fuse*
%{_pkgconfigdir}/fuse.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libfuse.a
%endif

%if %{with kernel}
%files -n kernel-misc-fuse
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/fs/fuse.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-misc-fuse
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/fs/fuse.ko*
%endif
%endif
