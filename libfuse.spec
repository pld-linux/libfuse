#
# TODO:
# - review patches
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
Version:	2.2
%define		_rel	0.4
Release:	%{_rel}@%{_kernel_ver_str}
Epoch:		0
License:	GPL v2
Group:		Base/Kernel
Source0:	http://dl.sourceforge.net/fuse/fuse-%{version}.tar.gz
# Source0-md5:	6f7fe60795324111fea18143e81512ec
# Source0-size:	126361
Patch0:		%{name}-configure.in.patch
Patch1:		%{name}-perm.patch
URL:		http://fuse.sourceforge.net/
BuildRequires:	autoconf
BuildRequires:	automake
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
%endif
BuildRequires:	libtool
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel}
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
Group:		Base/Kernel
Provides:	kernel-misc-fuse
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel-smp}

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
privileged users to create and mount their own filesystem
implementations.

%description -n fusermount -l pl
Narzêdzia obs³uguj±ce systemu plików w przestrzeni u¿ytkownika.
Dostarcza bezpieczn± metodê tworzenia i montowania w³asnych systemów
plików dla nie uprzywilejowanych userów.

%prep
%setup -q -n fuse-%{version}
%patch0 -p0
#patch1 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoheader}
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
    %{__make} -C %{_kernelsrcdir} clean \
	RCS_FIND_IGNORE="-name '*.ko' -o" \
	M=$PWD O=$PWD \
	%{?with_verbose:V=1}
    %{__make} -C %{_kernelsrcdir} modules \
	EXTRA_CFLAGS='-I../include -DFUSE_VERSION=\"2.2\"' \
	RCS_FIND_IGNORE="-name '*.ko' -o" \
	CC="%{__cc}" CPP="%{__cpp}" \
	M=$PWD O=$PWD \
	%{?with_verbose:V=1}

    mv fuse.ko fuse-$cfg.ko
done
cd -
%endif

%if %{with userspace}
cp kernel/fuse_kernel.h include/
for DIR in include lib util; do
%{__make} -C $DIR
done
%endif

%install
rm -rf $RPM_BUILD_ROOT

install -d $RPM_BUILD_ROOT%{_pkgconfigdir}

%if %{with userspace}
for DIR in include lib util; do
%{__make} -C $DIR install \
	DESTDIR=$RPM_BUILD_ROOT
done

install fuse.pc $RPM_BUILD_ROOT%{_pkgconfigdir}
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

%post
%depmod %{_kernel_ver}

%postun
%depmod %{_kernel_ver}

%post -n kernel-smp-misc-fuse
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-misc-fuse
%depmod %{_kernel_ver}smp

%post -n libfuse -p /sbin/ldconfig
%postun -n libfuse -p /sbin/ldconfig

%if %{with kernel}
%files
%defattr(644,root,root,755)
%doc README NEWS ChangeLog AUTHORS doc/*
/lib/modules/%{_kernel_ver}/kernel/fs/fuse.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-misc-fuse
%defattr(644,root,root,755)
%doc README NEWS ChangeLog AUTHORS doc/*
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

%files -n libfuse
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libfuse.so.*.*.*

%files -n libfuse-devel
%defattr(644,root,root,755)
%{_includedir}/fuse*
%{_libdir}/libfuse.la
%attr(755,root,root) %{_libdir}/libfuse.so
%{_pkgconfigdir}/fuse.pc

%files -n libfuse-static
%defattr(644,root,root,755)
%{_libdir}/libfuse.a
%endif
