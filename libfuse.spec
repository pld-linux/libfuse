#
# Condtional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# without smp packages
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)
#
Name:		kernel-misc-fuse
Summary:	Filesystem in Userspace
Summary(pl):	System plików w przestrzeni u¿ytkownika
Version:	1.1
%define		_rel	3
Release:	%{_rel}@%{_kernel_ver_str}
License:	GPL v2
Group:		Applications/System
Source0:	http://dl.sourceforge.net/avf/fuse-%{version}.tar.gz
# Source0-md5:	adfbf15cf196ca597e1ff7fb7839938e
Patch0:		%{name}-configure.in.patch
URL:		http://sourceforge.net/projects/avf
BuildRequires:	autoconf
BuildRequires:	automake
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel-module-build
%endif
%{?with_dist_kernel:%requires_releq_kernel_up}
BuildRequires:	rpmbuild(macros) >= 1.153
Requires(post,postun):	/sbin/depmod
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the Linux kernel. FUSE also
aims to provide a secure method for non privileged users to create and
mount their own filesystem implementations.

%description -l pl
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
Group:		Applications/System
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod

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

%package -n libfuse
Summary:	Shared library for Filesytem in Userspace
Summary(pl):	Biblioteki dzielone Systemu plików w przestrzeni u¿ytkownika
Group:		Applications/System
Release:	%{_rel}

%description -n libfuse
Shared library for Filesytem in Userspace

%description -n libfuse -l pl
Biblioteki dzielone Systemu plików w przestrzeni u¿ytkownika

%package -n libfuse-devel
Summary:	Filesytem in Userspace - Development header fiels and libraries
Summary(pl):	Systemu plików w przestrzeni u¿ytkownika - Biblioteki dzielone
Group:		Development/Libraries
Release:	%{_rel}
Requires:	libfuse = %{epoch}:%{version}-%{_rel}

%description -n libfuse-devel
Libfuse library header files.

%description -n libfuse-devel -l pl
Libfuse biblioteki nag³ówkowe dla programistów.

%package -n libfuse-static
Summary:	Filesytem in Userspace - static libraries
Summary(pl):	Systemu plików w przestrzeni u¿ytkownika - Biblioteki statyczne
Group:		Development/Libraries
Release:	%{_rel}
Requires:	libfuse-devel = %{epoch}:%{version}-%{_rel}

%description -n libfuse-static
Static libfuse libraries.

%description -n libfuse-static -l pl
Statyczne biblioteki libfuse

%package -n fusermount
Summary:	Filesytem in Userspace utilities
Summary(pl):	Narzêdzia obs³uguj±ce systemu plików w przestrzeni u¿ytkownika
Group:		Applications/System
Release:	%{_rel}

%description -n fusermount
Filesytem in Userspace utilities. It provide a secure method for non
privileged users to create and mount their own filesystem implementations. 

%description -n fusermount -l pl
Narzêdzia obs³uguj±ce systemu plików w przestrzeni u¿ytkownika. Dostarcza bezpieczn±
metodê tworzenia i montowania w³asnych systemów plików dla nie uprzywilejowanych userów.

%clean
rm -rf $RPM_BUILD_ROOT

%prep
%setup -q -n fuse-%{version}
%patch0 -p1

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
    --enable-lib \
    --enable-util \
    --with-kernel=%{_kernelsrcdir}

%if %{with kernel}
cd kernel
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
    if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
	exit 1
    fi
    rm -rf include
    install -d include/{linux,config}
    ln -sf %{_kernelsrcdir}/config-$cfg .config
    ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
    ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
    touch include/config/MARKER
    %{__make} -C %{_kernelsrcdir} clean modules \
	EXTRA_CFLAGS="-I../include -DFUSE_VERSION='1.1'" \
	RCS_FIND_IGNORE="-name '*.ko' -o" \
	M=$PWD O=$PWD \
	%{?with_verbose:V=1}
    mv fuse.ko fuse-$cfg.ko
done
cd -
%endif

cd lib
for f in fuse.c fuse_mt.c helper.c mount.c; do
libtool --mode=compile --tag=CC %{__cc} -c -I. -I../include -DHAVE_CONFIG_H $f
done
libtool --mode=link %{__cc} -o libfuse.la fuse.lo fuse_mt.lo helper.lo mount.lo -rpath %{_libdir}
cd -

%{?with_userspace:%{__make} -C util}

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT{%{_bindir},%{_includedir},%{_libdir}}

%if %{with userspace}
cd util
install fusermount $RPM_BUILD_ROOT%{_bindir}/
cd -
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
cd -
%endif

install include/fuse.h $RPM_BUILD_ROOT%{_includedir}
cd lib
libtool --mode=install install libfuse.la $RPM_BUILD_ROOT%{_libdir}/libfuse.la
cd -

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post -n kernel-smp-misc-fuse
%depmod %{_kernel_ver}

%postun -n kernel-smp-misc-fuse
%depmod %{_kernel_ver}

%if %{with kernel}
%files
%defattr(644,root,root,755)
%doc README NEWS ChangeLog AUTHORS
%doc patch/
/lib/modules/%{_kernel_ver}/kernel/fs/fuse.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-misc-fuse
%defattr(644,root,root,755)
%doc README NEWS ChangeLog AUTHORS
%doc patch/
/lib/modules/%{_kernel_ver}smp/kernel/fs/fuse.ko*
%endif
%endif

%if %{with userspace}
%files -n fusermount
%defattr(644,root,root,755)
# suid needed? NO!
%attr(755,root,root) %{_bindir}/fusermount
# do it ! failed
# %%attr(755,root,root) %{_sbindir}/mount.fuse
%endif

%files -n libfuse
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libfuse.so.*.*.*

%files -n libfuse-devel
%defattr(644,root,root,755)
%{_includedir}/fuse.h
%{_libdir}/libfuse.la
%attr(755,root,root) %{_libdir}/libfuse.so

%files -n libfuse-static
%defattr(644,root,root,755)
%{_libdir}/libfuse.a
