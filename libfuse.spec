#
# TODO:
#		- kernel-smp-* subpackage
#		- fix %%install and check %%files
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
Summary(pl):	System plik�w w przestrzeni u�ytkownika
Version:	1.1
Release:	1.1@%{_kernel_ver_str}
License:	GPL
Group:		Applications/System
Source0:	http://dl.sourceforge.net/avf/fuse-%{version}.tar.gz
# Source0-md5:	adfbf15cf196ca597e1ff7fb7839938e
Patch0:		%{name}-configure.in.patch
URL:		http://sourceforge.net/projects/avf
%if %{with kernel} && %{with dist_kernel}
BuildRequires:	kernel-module-build
%endif
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the Linux kernel. FUSE also
aims to provide a secure method for non privileged users to create and
mount their own filesystem implementations.

%description -l pl
FUSE stanowi prosty interfejs dla program�w dzia�aj�cych w przestrzeni
u�ytkownika eksportuj�cy wirtualny system plik�w do j�dra Linuksa.
FUSE ma r�wnie� na celu udost�pnienie bezpiecznej metody tworzenia i
montowania w�asnych implementacji system�w plik�w przez zwyk�ych
(nieuprzywilejowanych) u�ytkownik�w.

%package -n libfuse
Summary:	Shared library for Filesytem in Userspace
Summary(pl):	Biblioteki dzielone Systemu plik�w w przestrzeni u�ytkownika
Group:		Applications/System

%description -n libfuse
- -- empty --

%description -n libfuse -l pl
- -- pusty --

%package -n libfuse-devel
Summary:	Filesytem in Userspace - Development header fiels and libraries
Summary(pl):	Systemu plik�w w przestrzeni u�ytkownika - Biblioteki dzielone
Group:		Development/Libraries
Requires:	libfuse = %{epoch}:%{version}-%{release}

%description -n libfuse-devel
- -- empty --

%description -n libfuse-devel -l pl
- -- pusty --

%package -n libfuse-static
Summary:	Filesytem in Userspace - static libraries
Summary(pl):	Systemu plik�w w przestrzeni u�ytkownika - Biblioteki statyczne
Group:		Development/Libraries
Requires:	libfuse-devel = %{epoch}:%{version}-%{release}

%description -n libfuse-static
- -- empty --

%description -n libfuse-static -l pl
- -- pusty --

%package -n fusermount
Summary:	Filesytem in Userspace utilities
Summary(pl):	Narz�dzia obs�uguj�ce systemu plik�w w przestrzeni u�ytkownika
Group:		Applications/System

%description -n fusermount
- -- empty --

%description -n fusermount -l pl
- -- pusty --

%clean
rm -rf $RPM_BUILD_ROOT

%prep
%setup -q -n fuse-%{version}
%patch0 -p1

%build
%{__aclocal}
%{__autoconf}
%{__automake}
%configure

%if %{with kernel}
cd kernel
rm -rf built
mkdir built
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
    if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
	exit 1
    fi
    %{__make} -C %{_kernelsrcdir} mrproper \
	SUBDIRS=$PWD \
	O=$PWD \
	RCS_FIND_IGNORE="-name built" \
	%{?with_verbose:V=1}
    rm -rf include
    install -d include/{linux,config}
    ln -sf %{_kernelsrcdir}/config-$cfg .config
    ln -sf %{_kernelsrcdir}/include/linux/autoconf-${cfg}.h include/linux/autoconf.h
    touch include/config/MARKER
    %{__make} -C %{_kernelsrcdir} modules \
	SUBDIRS=$PWD \
	O=$PWD \
	%{?with_verbose:V=1}
    mv fuse.ko built/fuse-$cfg.ko
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

%{__make} install \
	prefix=$RPM_BUILD_ROOT%{_prefix} \
	fusemoduledir=$RPM_BUILD_ROOT%{fusemoduledir}

install -d $RPM_BUILD_ROOT%{_prefix}/lib/fuse/example
install -s -m 755 example/{fusexmp,hello,null} $RPM_BUILD_ROOT%{_prefix}/lib/fuse/example/

# remove binaries form example folder so we can include it
# as a form of documentation into the package
%{__make} -C example clean
rm -rf example/.deps/

%post
/sbin/depmod -aq

%preun
/sbin/modprobe -r fuse

%postun
/sbin/depmod -aq


%if %{with kernel}
%files
%defattr(644,root,root,755)
%doc README TODO NEWS INSTALL ChangeLog AUTHORS COPYING COPYING.LIB
%doc patch/
/lib/modules/%{_kernel_ver}/kernel/fs/fuse.ko*
%endif

%if %{with userspace}
%files -n fusermount
# suid needed?
%attr(755,root,root) %{_bindir}/fusermount
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
%{_prefix}/lib/libfuse.a
