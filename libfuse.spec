Summary:	Filesystem in Userspace
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika
Name:		libfuse
Version:	2.9.3
Release:	1
Epoch:		0
License:	GPL v2
Group:		Applications/System
Source0:	http://downloads.sourceforge.net/fuse/fuse-%{version}.tar.gz
# Source0-md5:	33cae22ca50311446400daf8a6255c6a
Source1:	fuse.conf
Patch0:		kernel-misc-fuse-Makefile.am.patch
URL:		http://fuse.sourceforge.net/
BuildRequires:	autoconf >= 2.60
BuildRequires:	automake
BuildRequires:	libtool
BuildRequires:	sed >= 4.0
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Provides:	group(fuse)
Suggests:	mount >= 2.18
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
Summary:	Filesytem in Userspace - Development header files
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika - pliki nagłówkowe
Group:		Development/Libraries
Requires:	%{name} = %{epoch}:%{version}-%{release}

%description devel
Libfuse library header files.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki libfuse.

%package static
Summary:	Filesytem in Userspace - static library
Summary(pl.UTF-8):	System plików w przestrzeni użytkownika - biblioteka statyczna
Group:		Development/Libraries
Requires:	%{name}-devel = %{epoch}:%{version}-%{release}

%description static
Static libfuse libraries.

%description static -l pl.UTF-8
Statyczna biblioteka libfuse.

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

mv -f $RPM_BUILD_ROOT%{_libdir}/libfuse.so.* $RPM_BUILD_ROOT/%{_lib}
%{__rm} $RPM_BUILD_ROOT%{_libdir}/libfuse.so
ln -sf /%{_lib}/$(cd $RPM_BUILD_ROOT/%{_lib}; echo libfuse.so.*.*) \
	$RPM_BUILD_ROOT%{_libdir}/libfuse.so

install fuse.pc $RPM_BUILD_ROOT%{_pkgconfigdir}
install %{SOURCE1} $RPM_BUILD_ROOT%{_sysconfdir}

# part of default udev rules nowdays
rm $RPM_BUILD_ROOT/etc/udev/rules.d/99-fuse.rules

# not needed
rm $RPM_BUILD_ROOT/etc/rc.d/init.d/fuse

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 84 fuse

%post	-p /sbin/ldconfig
%postun	-p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README NEWS ChangeLog AUTHORS doc/*
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/fuse.conf
%attr(4755,root,root) %{_bindir}/fusermount
%attr(755,root,root) %{_bindir}/ulockmgr_server
%attr(755,root,root) /sbin/mount.fuse
%attr(755,root,root) /%{_lib}/libfuse.so.*.*.*
%attr(755,root,root) %ghost /%{_lib}/libfuse.so.2
%attr(755,root,root) %{_libdir}/libulockmgr.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libulockmgr.so.1
%{_mandir}/man1/fusermount.1*
%{_mandir}/man1/ulockmgr_server.1*
%{_mandir}/man8/mount.fuse.8*

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
