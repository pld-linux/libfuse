%define	kernelversion	%(uname -r)
%define	fusemoduledir	/lib/modules/%{kernelversion}/kernel/fs/fuse

%bcond_without dist_kernel	# without distribution kernel
%bcond_without smp		# without smp packages

%define	kernelrel	%(uname -r | sed -e s/-/_/g)
%define	_rel		0.1
%define	_pre		pre2

#fuse is required by siefs package

# there is another packet in repo named fuse - zx spectrum emulator -- help
Name:		fuse
Version:	1.1
Release:	0.%{_pre}.%{_rel}@%{_kernel_ver_str}
Summary:	Filesystem in Userspace
Summary(pl):	System plików w przestrzeni u¿ytkownika
Source0:	http://dl.sourceforge.net/avf/%{name}-%{version}-%{_pre}.tar.gz
# Source0-md5:	1a245ad3e849bd662372961a597a7391
License:	GPL
Group:		Applications/System
URL:		http://sourceforge.net/projects/avf
%{?with_dist_kernel:BuildRequires:	kernel-headers >= 2.4.0 }
%{?with_dist_kernel:BuildRequires:	kernel-source >= 2.4.0 }
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
# some parts of this specfile are taken from Ian Pilcher's specfile

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

%build
# invoke configure with the --with-kernel option in case we attempt to
# compile for a different kernel and hope the path is right :-)

#if [ "%{kernelversion}" != $(uname -r) ]; then
#	for dir in /lib/modules/%{kernelversion}/build   \
#%{_kernelsrcdir}-%{kernelversion} \
#%{_prefix}/local/src/linux-%{kernelversion} ; do
#		if [ -d "$dir" ]; then
#			WITH_KERNEL="--with-kernel=$dir"
#			break
#		fi
#	done
#fi

./configure \
	--prefix=%{_prefix} \
	$WITH_KERNEL
%{__make}
%{__make} check

## Now build the library as a shared object
#cd lib
#gcc -fPIC -DHAVE_CONFIG_H -I../include -Wall -W -g -O2 -c *.c
#gcc -shared -Wl,-soname,libfuse.so.%{major_ver} -o libfuse.so.%{version} *.o
#cd ..


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
