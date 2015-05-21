
Name:           collectd
Version:        5.4.1
Release:        13%{?dist}
Summary:        Collectd configured for Open Infinity
BuildArch:      x86_64
Group:          Applications
License:        GNU GPLv2
Vendor:         OpenInfinity
Packager:       OpenInfinity 
BuildRequires:  rrdtool-devel >= 1.3.8
BuildRequires:  perl-ExtUtils-MakeMaker >= 6.5
BuildRequires:  perl-ExtUtils-Embed >= 1.28
BuildRequires:  gcc >= 4
BuildRequires:  make >= 3.81
BuildRequires:  java-1.7.0-openjdk-devel 
BuildRequires:  flex >= 2.5
BuildRequires:  byacc >= 1.9
BuildRequires:  libtool >= 2.2.6 
BuildRequires:  glib2-devel >= 2.26.1
BuildRequires:  mysql-devel >= 5.1.73
BuildRequires:  libdbi-drivers
BuildRequires:  libdbi-dbd-mysql
Requires:       libdbi-drivers
Requires:       libdbi-dbd-mysql
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%global installation_path /opt/openinfinity/3.1.0/healthmonitoring
%global installation_dir %{buildroot}/%{installation_path}

%description
Collectd configured for Open Infinity

%prep
%setup -q

%build
./configure --prefix %{installation_path}/collectd --enable-dbi --enable-mysql --enable-rrdtool --enable-debug --enable-java LDFLAGS='-Wl,-rpath,/usr/lib/jvm/jre-1.7.0/lib/amd64/server' JAVA_CPPFLAGS='-I/usr/lib/jvm/java-1.7.0-openjdk.x86_64/include/linux/ -I/usr/lib/jvm/java-1.7.0-openjdk.x86_64/include/' --with-java=/usr/lib/jvm/java-1.7.0-openjdk-1.7.0.75.x86_64/
make

%install
make install DESTDIR=%{buildroot}
mkdir -p %{buildroot}%{_initddir}
cp -rf ./pkg/etc/init.d/collectd %{buildroot}%{_initddir}
mkdir -p %{installation_dir}/collectd
cp -rf ./pkg/opt/* %{installation_dir}/collectd

%clean

%files
%defattr(-,root,root,-)
%{installation_path}/collectd/
%{_initddir}/collectd
#%exclude %{installation_path}/collectd/etc/collectd.conf
 
%post
useradd collectd > /dev/null 2>&1

/sbin/chkconfig --add collectd
/sbin/chkconfig collectd on

mkdir -p %{installation_path}/collectd/
mkdir -p %{installation_path}/collectd/var/log/
mkdir -p %{installation_path}/collectd/var/lib/collectd/rrd

chown -R collectd /%{installation_path}/collectd
chown -R collectd /%{installation_path}/collectd
chown -R root /%{installation_path}/collectd/sbin

chmod 775 /%{installation_path}/collectd/etc/collectd.d
chmod 755 %{_initddir}/collectd


%preun
if [ "$1" = 0 ]; then
   /sbin/chkconfig collectd off
   /sbin/service collectd stop >/dev/null 2>&1
   /sbin/chkconfig --del collectd
fi

%postun
#if [ "$1" -ge "1" ] ; then
#    /sbin/service collectd condrestart >/dev/null 2>&1 || :
#
#fi
rm -rf /%{installation_path}/collectd
exit 0

%changelog
* Mon Oct 27 2014 Vedran Bartonicek <vedran.bartonicek@tieto.com> - 3.1.0-10
- Daemon runs process with collectd user
- User creation and dir ownership added
- LDFLAGS for java.so for better portabilty 

* Thu Oct 16 2014 Vedran Bartonicek <vedran.bartonicek@tieto.com> - 3.1.0-1
- Versioning changed to Open infinity insead of Collectd version numbers
- Changed --with java arg to us use relative path

* Thu Jun 12 2014 Vedran Bartonicek <vedran.bartonicek@tieto.com> - 5.4.0-9
- Using collectd 5.4.0, commit 4c6303ec6be673df6c9e0964dfc9419c697bf47c.
A version update to 3.1.0 for open infinity. Installation path updated too.

* Thu Jan 14 2014 Vedran Bartonicek <vedran.bartonicek@tieto.com> - 5.4.0-7
- Using collectd 5.4.0, commit 4c6303ec6be673df6c9e0964dfc9419c697bf47c. It
has integrated pull request #498 that brings relative load functionality.
Therefore no need to use pathes for load and df. 

* Wed Dec 14 2013 Vedran Bartonicek <vedran.bartonicek@tieto.com> - 5.2.2-2
- Installation path changed to  opt/openinfinity/3.0.0/healthmonitoring

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
