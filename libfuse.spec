#
# TODO:
#		- userspace and *-libs subpackages
#
# Condtional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# without smp packages
%bcond_with	verbose		# verbose build (V=1)
#
Name:		kernel-misc-fuse
Summary:	Filesystem in Userspace
Summary(pl):	System plików w przestrzeni u¿ytkownika
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

%define	fusemoduledir	/lib/modules/%{_kernel_ver}/kernel/fs/fuse

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

%clean
rm -rf $RPM_BUILD_ROOT

%prep
%setup -q
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

%{__make} -C util

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



%files
%defattr(644,root,root,755)
%doc README TODO NEWS INSTALL ChangeLog AUTHORS COPYING COPYING.LIB
%doc example/
%doc patch/

%{fusemoduledir}
%{_prefix}/lib/libfuse.a
%{_includedir}/fuse.h
%{_prefix}/lib/fuse/

# you want to install fusermount SUID root?
# Then uncomment the "%attr()"-line in favour of the line after it.
#%attr(4500,root,root) %{prefix}/bin/fusermount
%attr(755,root,root) %{_bindir}/fusermount
