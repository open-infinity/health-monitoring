
Name:           collectd
Version:        5.2.2
Release:        1%{?dist}
Summary:        Collectd patched, modified and configured for OpenInfinity
BuildArch:      x86_64
Group:          Applications
License:        todo Distributable
Vendor:         OpenInfinity
Packager:       OpenInfinity 
BuildRequires:  rrdtool-devel >= 1.3.8
BuildRequires:  perl-ExtUtils-MakeMaker >= 6.55
BuildRequires:  gcc >= 4
BuildRequires:  make >= 3.81
Source0:        %{name}-%{version}.tar.gz
Patch1:         df.patch
Patch2:	        load.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Collectd patched, modified and configured for OpenInfinity

%prep
%setup -q
%patch1 -p1
%patch2 -p1

%build
./configure --prefix /opt/openinfinity/2.0.0/healthmonitoring/collectd --with-java=/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.0.x86_64 --enable-rrdtool --enable-debug --enable-java
make

%install
make install DESTDIR=$RPM_BUILD_ROOT

%clean

%files
%defattr(-,root,root,-)
/opt/openinfinity/2.0.0/healthmonitoring/collectd/
%exclude /opt/openinfinity/2.0.0/healthmonitoring/collectd/etc/collectd.conf
 
%post
/sbin/chkconfig --add collectd
/sbin/chkconfig collectd on

mkdir -p /opt/openinfinity/2.0.0/healthmonitoring/collectd/
mkdir -p /opt/openinfinity/2.0.0/healthmonitoring/collectd/var/log/
mkdir -p /opt/openinfinity/2.0.0/healthmonitoring/collectd/run/
mkdir -p /opt/openinfinity/2.0.0/healthmonitoring/collectd/var/lib/collectd/rrd

%preun
if [ "$1" = 0 ]; then
   /sbin/chkconfig collectd off
   /etc/init.d/collectd stop
   /sbin/chkconfig --del collectd
fi
exit 0

%changelog
* Thu Nov 14 2013 Vedran Bartonicek <vedran.bartonicek@tieto.com> - 5.2.2-1
- Using openjdk 1.7

* Thu Aug 01 2013 Vedran Bartonicek <vedran.bartonicek@tieto.com> - 5.2.1-10
- Added java plugin

* Fri Jun 07 2013 Vedran Bartonicek <vedran.bartonicek@tieto.com> - 5.2.1-9
- Plugin load patch, load relative to number of cores. Commit:
-    https://github.com/vbartoni/collectd/commit/0c98674a8adbaa8d0b2efdfe107c1011536504f4

* Thu Jun 06 2013 Vedran Bartonicek <vedran.bartonicek@tieto.com> - 5.2.1-8
- Improved patch for df. Commit:
-    https://github.com/vbartoni/collectd/commit/a17b41455505dda43c42d90444fb76e3a57ad6a3

* Mon Jun 03 2013 Vedran Bartonicek <vedran.bartonicek@tieto.com> - 5.2.1-7
- Added patch for df. Commits:
-    https://github.com/collectd/collectd/commit/7e2a10e78c6fd263d0360bf929158dc1b2257704
-    https://github.com/collectd/collectd/commit/a6ea8a31f4f27655640f7a517d2b157fa8fc62d7

* Tue Apr 23 2013 Vedran Bartonicek <vedran.bartonicek@tieto.com> 5.2.1-1
- Initial version
