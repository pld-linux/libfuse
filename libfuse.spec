%define kernelversion %(uname -r)
%define fusemoduledir /lib/modules/%{kernelversion}/kernel/fs/fuse

%define kernelrel %(uname -r | sed -e s/-/_/g)
%define real_release 6

Name:		fuse
Version:	1.0
Release:	kernel_%{kernelrel}_%{real_release}
Summary:	Filesystem in Userspace
Source0:	%{name}-%{version}.tar.gz
License:	GPL
Group:		Applications/System
URL:		http://sourceforge.net/projects/avf
Buildroot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)
# some parts of this specfile are taken from Ian Pilcher's specfile

# don't restrict to RedHat kernels but also allow compilation with
# vanilla kernels, too.
#Requires: kernel = %{kernelrel}, redhat-release >= 7
#BuildRequires: kernel-source = %{kernelrel}


%description
FUSE (Filesystem in Userspace) is a simple interface for userspace
programs to export a virtual filesystem to the linux kernel. FUSE also
aims to provide a secure method for non privileged users to create and
mount their own filesystem implementations.


%clean
case "$RPM_BUILD_ROOT" in *-root) rm -rf $RPM_BUILD_ROOT ;; esac

%prep
%setup -q

%build
# invoke configure with the --with-kernel option in case we attempt to
# compile for a different kernel and hope the path is right :-)
if [ "%{kernelversion}" != $(uname -r) ]; then
	for dir in /lib/modules/%{kernelversion}/build   \
%{_kernelsrcdir}-%{kernelversion} \
%{_prefix}/local/src/linux-%{kernelversion} ; do
		if [ -d "$dir" ]; then
			WITH_KERNEL="--with-kernel=$dir"
			break
		fi
	done
fi

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
case "$RPM_BUILD_ROOT" in *-root) rm -rf $RPM_BUILD_ROOT ;; esac
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
