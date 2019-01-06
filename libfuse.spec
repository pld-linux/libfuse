Summary:	Filesystem in Userspace
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika
Name:		libfuse
Version:	2.9.9
Release:	1
License:	LGPL v2 (library), GPL v2 (tools)
Group:		Applications/System
#Source0Download: https://github.com/libfuse/libfuse/releases
Source0:	https://github.com/libfuse/libfuse/releases/download/fuse-%{version}/fuse-%{version}.tar.gz
# Source0-md5:	8000410aadc9231fd48495f7642f3312
Patch0:		kernel-misc-fuse-Makefile.am.patch
URL:		https://github.com/libfuse/libfuse
BuildRequires:	autoconf >= 2.60
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	sed >= 4.0
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
Summary:	Filesystem in Userspace - development header files
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika - pliki nagłówkowe
License:	LGPL v2
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
FUSE libraries header files.

%description devel -l pl.UTF-8
Pliki nagłówkowe bibliotek FUSE.

%package static
Summary:	Filesystem in Userspace - static libraries
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika - biblioteki statyczne
License:	LGPL v2
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static FUSE libraries.

%description static -l pl.UTF-8
Statyczne biblioteki FUSE.

%package apidocs
Summary:	API documentation for FUSE library
Summary(pl.UTF-8):	Dokumentacja API bibliotek FUSE
Group:		Documentation

%description apidocs
API documentation for FUSE library.

%description apidocs -l pl.UTF-8
Dokumentacja API bibliotek FUSE.

%package tools
Summary:	Tools to mount FUSE based filesystems
Summary(pl.UTF-8):	Narzędzia do montowania systemów plików opartych na FUSE
License:	GPL v2
Group:		Applications/System
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires:	%{name} = %{version}-%{release}
Requires:	libfuse-common >= %{version}
Requires:	mount >= 2.18
Provides:	group(fuse)
Obsoletes:	fusermount

%description tools
Tools to mount FUSE based filesystems.

%description tools -l pl.UTF-8
Narzędzia do montowania systemów plików opartych na FUSE.

%prep
%setup -q -n fuse-%{version}
%patch0 -p1

sed -i '/FUSERMOUNT_PROG/s,fusermount,%{_bindir}/fusermount,' lib/mount.c

# gold is missing base versioning
install -d ld-dir
[ ! -x /usr/bin/ld.bfd ] || ln -sf /usr/bin/ld.bfd ld-dir/ld

%build
PATH=$(pwd)/ld-dir:$PATH
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%{__automake}
%configure \
	INIT_D_PATH=/etc/rc.d/init.d \
	--disable-silent-rules \
	--enable-lib \
	--enable-util

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/%{_lib},%{_pkgconfigdir},%{_sysconfdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%{__mv} $RPM_BUILD_ROOT%{_libdir}/libfuse.so.* $RPM_BUILD_ROOT/%{_lib}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libfuse.so
ln -sf /%{_lib}/$(basename $RPM_BUILD_ROOT/%{_lib}/libfuse.so.*.*) \
	$RPM_BUILD_ROOT%{_libdir}/libfuse.so

install fuse.pc $RPM_BUILD_ROOT%{_pkgconfigdir}

# part of default udev rules nowdays
%{__rm} $RPM_BUILD_ROOT/etc/udev/rules.d/99-fuse.rules

# not needed
%{__rm} $RPM_BUILD_ROOT/etc/rc.d/init.d/fuse

%clean
rm -rf $RPM_BUILD_ROOT

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%pre tools
%groupadd -g 84 fuse

%files
%defattr(644,root,root,755)
%doc README.md NEWS ChangeLog AUTHORS doc/{how-fuse-works,kernel.txt}
%attr(755,root,root) /%{_lib}/libfuse.so.*.*.*
%attr(755,root,root) %ghost /%{_lib}/libfuse.so.2
%attr(755,root,root) %{_libdir}/libulockmgr.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libulockmgr.so.1

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libfuse.so
%attr(755,root,root) %{_libdir}/libulockmgr.so
%{_libdir}/libfuse.la
%{_libdir}/libulockmgr.la
%{_includedir}/fuse
%{_includedir}/fuse.h
%{_includedir}/ulockmgr.h
%{_pkgconfigdir}/fuse.pc

%files static
%defattr(644,root,root,755)
%{_libdir}/libfuse.a
%{_libdir}/libulockmgr.a

%files apidocs
%defattr(644,root,root,755)
%doc doc/html/*

%files tools
%defattr(644,root,root,755)
%attr(4755,root,root) %{_bindir}/fusermount
%attr(755,root,root) %{_bindir}/ulockmgr_server
%attr(755,root,root) /sbin/mount.fuse
%{_mandir}/man1/fusermount.1*
%{_mandir}/man1/ulockmgr_server.1*
%{_mandir}/man8/mount.fuse.8*
