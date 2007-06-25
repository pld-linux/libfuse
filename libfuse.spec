#
# Condtional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_with	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)
%bcond_with	grsec_kernel	# build for kernel-grsecurity
%bcond_without	selinux		# build without SELinux support
#
%if %{with kernel} && %{with dist_kernel} && %{with grsec_kernel}
%define	alt_kernel	grsecurity
%endif
#
%define		_rel	3
Summary:	Filesystem in Userspace
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika
Name:		libfuse
Version:	2.6.5
Release:	%{_rel}
Epoch:		0
License:	GPL v2
Group:		Applications/System
Source0:	http://dl.sourceforge.net/fuse/fuse-%{version}.tar.gz
# Source0-md5:	66bd30503df55a87b9868835ca5a45bc
Source1:	fuse.conf
Patch0:		kernel-misc-fuse-Makefile.am.patch
Patch1:		%{name}-link.patch
URL:		http://fuse.sourceforge.net/
BuildRequires:	autoconf
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	cpp
BuildRequires:	sed >= 4.0
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.20.2}
BuildRequires:	rpmbuild(macros) >= 1.379
%endif
%if %{with userspace}
%{?with_selinux:BuildRequires:	libselinux-devel}
%endif
Requires(postun):	/sbin/ldconfig
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%if !%{with kernel}
%undefine with_dist_kernel
%endif

%description
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the Linux kernel. FUSE also
aims to provide a secure method for non privileged users to create and
mount their own filesystem implementations.

This package contains a shared library.

%description -l pl.UTF-8
FUSE stanowi prosty interfejs dla programów działających w przestrzeni
użytkownika eksportujący wirtualny system plików do jądra Linuksa.
FUSE ma również na celu udostępnienie bezpiecznej metody tworzenia i
montowania własnych implementacji systemów plików przez zwykłych
(nieuprzywilejowanych) użytkowników.

Ten pakiet zawiera bibliotekę współdzieloną.

%package devel
Summary:	Filesytem in Userspace - Development header files
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika - pliki nagłówkowe
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{_rel}

%description devel
Libfuse library header files.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki libfuse.

%package static
Summary:	Filesytem in Userspace - static library
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika - biblioteka statyczna
Group:		Development/Libraries
Requires:	libfuse-devel = %{epoch}:%{version}-%{_rel}

%description static
Static libfuse libraries.

%description static -l pl.UTF-8
Statyczna biblioteka libfuse.

%package -n kernel%{_alt_kernel}-misc-fuse
Summary:	Filesystem in Userspace
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Base/Kernel
Requires(post,postun):	/sbin/depmod
%if %{with dist_kernel}
%requires_releq_kernel
Requires(postun):	%releq_kernel
%endif
%if "%{_alt_kernel}" != "%{nil}"
Provides:	kernel-misc-fuse
%endif

%description -n kernel%{_alt_kernel}-misc-fuse
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the Linux kernel. FUSE also
aims to provide a secure method for non privileged users to create and
mount their own filesystem implementations.

%description -n kernel%{_alt_kernel}-misc-fuse -l pl.UTF-8
FUSE stanowi prosty interfejs dla programów działających w przestrzeni
użytkownika eksportujący wirtualny system plików do jądra Linuksa.
FUSE ma również na celu udostępnienie bezpiecznej metody tworzenia i
montowania własnych implementacji systemów plików przez zwykłych
(nieuprzywilejowanych) użytkowników.

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
	%{!?with_selinux:ac_cv_header_selinux_selinux_h=no} \
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
%files -n kernel%{_alt_kernel}-misc-fuse
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/fs/fuse.ko*
%endif
