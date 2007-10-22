#
# Condtional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# without smp packages
%bcond_without	up		# without up packages
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)
%bcond_with	grsec_kernel	# build for kernel-grsecurity

%ifarch sparc
%undefine	with_smp
%endif

%if %{without kernel}
%undefine with_dist_kernel
%endif
%if %{with kernel} && %{with dist_kernel} && %{with grsec_kernel}
%define	alt_kernel	grsecurity
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif

%define		_rel	55
Summary:	Filesystem in Userspace
Summary(pl):	System plików w przestrzeni u¿ytkownika
Name:		libfuse
Version:	2.6.1
Release:	%{_rel}
Epoch:		0
License:	GPL v2
Group:		Applications/System
Source0:	http://dl.sourceforge.net/fuse/fuse-%{version}.tar.gz
# Source0-md5:	13e1873086a1d7a95f470bbc7428c528
Source1:	fuse.conf
Patch0:		kernel-misc-fuse-Makefile.am.patch
Patch1:		%{name}-link.patch
URL:		http://fuse.sourceforge.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	sed >= 4.0
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.9}
BuildRequires:	rpmbuild(macros) >= 1.330
BuildRequires:	cpp
%endif
%if %{with userspace}
BuildRequires:	libselinux-devel
%endif
Requires(postun):	/sbin/ldconfig
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Provides:	group(fuse)
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
Requires:	libfuse-devel = %{epoch}:%{version}-%{_rel}

%description static
Static libfuse libraries.

%description static -l pl
Statyczna biblioteka libfuse.

%package -n kernel%{_alt_kernel}-misc-fuse
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
%if "%{_alt_kernel}" != "%{nil}"
Provides:	kernel-misc-fuse
%endif

%description -n kernel%{_alt_kernel}-misc-fuse
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the Linux kernel. FUSE also
aims to provide a secure method for non privileged users to create and
mount their own filesystem implementations.

%description -n kernel%{_alt_kernel}-misc-fuse -l pl
FUSE stanowi prosty interfejs dla programów dzia³aj±cych w przestrzeni
u¿ytkownika eksportuj±cy wirtualny system plików do j±dra Linuksa.
FUSE ma równie¿ na celu udostêpnienie bezpiecznej metody tworzenia i
montowania w³asnych implementacji systemów plików przez zwyk³ych
(nieuprzywilejowanych) u¿ytkowników.

%package -n kernel%{_alt_kernel}-smp-misc-fuse
Summary:	Filesystem in Userspace
Summary(pl):	System plików w przestrzeni u¿ytkownika
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel_smp
Requires(postun):	%releq_kernel_smp
%endif
Provides:	kernel-misc-fuse

%description -n kernel%{_alt_kernel}-smp-misc-fuse
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the Linux kernel. FUSE also
aims to provide a secure method for non privileged users to create and
mount their own filesystem implementations.

%description -n kernel%{_alt_kernel}-smp-misc-fuse -l pl
FUSE stanowi prosty interfejs dla programów dzia³aj±cych w przestrzeni
u¿ytkownika eksportuj±cy wirtualny system plików do j±dra Linuksa.
FUSE ma równie¿ na celu udostêpnienie bezpiecznej metody tworzenia i
montowania w³asnych implementacji systemów plików przez zwyk³ych
(nieuprzywilejowanych) u¿ytkowników.

%prep
%setup -q -n fuse-%{version}
%patch0 -p1
%patch1 -p1

sed -i '/FUSERMOUNT_PROG/s,fusermount,%{_bindir}/fusermount,' lib/mount.c

%build
%{__libtoolize}
%{__aclocal}
%{__autoheader}
%{__autoconf}
%{__automake}
%configure \
	--%{?with_kernel:en}%{!?with_kernel:dis}able-kernel-module \
	--enable-lib \
	--enable-util \
	%{?with_kernel:--with-kernel=%{_kernelsrcdir}}

%if %{with userspace}
cp kernel/fuse_kernel.h include/
for DIR in include lib util; do
%{__make} -C $DIR
done
%endif

%if %{with kernel}
%build_kernel_modules -m fuse -C kernel
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
%endif

%if %{with kernel}
%install_kernel_modules -m kernel/fuse -d kernel/fs
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 84 fuse

%post	-p /sbin/ldconfig
%postun
/sbin/ldconfig
if [ "$1" = "0" ] ; then
	%groupremove fuse
fi

%post -n kernel%{_alt_kernel}-misc-fuse
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-misc-fuse
%depmod %{_kernel_ver}

%post -n kernel%{_alt_kernel}-smp-misc-fuse
%depmod %{_kernel_ver}smp

%postun -n kernel%{_alt_kernel}-smp-misc-fuse
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README NEWS ChangeLog AUTHORS doc/*
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fuse.conf
%attr(4754,root,fuse) %{_bindir}/fusermount
%attr(755,root,root) %{_bindir}/ulockmgr_server
%attr(755,root,root) /sbin/mount.fuse
%attr(755,root,root) %{_libdir}/lib*.so.*.*.*

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/lib*.so
%{_libdir}/lib*.la
%{_includedir}/fuse*
%{_includedir}/ulockmgr.h
%{_pkgconfigdir}/fuse.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/lib*.a
%endif

%if %{with kernel}
%if %{with up} || %{without dist_kernel}
%files -n kernel%{_alt_kernel}-misc-fuse
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/fs/fuse.ko*
%endif

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-misc-fuse
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/fs/fuse.ko*
%endif
%endif
