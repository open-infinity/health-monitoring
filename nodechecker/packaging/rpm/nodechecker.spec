Name:           oi3-nodechecker
Version:        3.0.0
Release:        6%{?dist}
Summary:        The Health Monitoring package for Open Infinity
BuildArch:      x86_64
License:        Apache 2.0
URL:            http://www.tieto.com
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{release}-root-%(%{__id_u} -n)
Requires:       java-1.7.0-openjdk, Pound, python => 2.6

%global installation_dir opt/openinfinity/3.0.0/healthmonitoring

%description
The Health Monitoring package for Open Infinity

%prep
%setup -q

%install
mkdir -p $RPM_BUILD_ROOT/etc/init.d/
cp -rf ./etc/init.d/oi3-collectd $RPM_BUILD_ROOT/etc/init.d/
cp -rf ./etc/init.d/oi3-healthmonitoring $RPM_BUILD_ROOT/etc/init.d/

mkdir -p $RPM_BUILD_ROOT/etc/profile.d/
cp -rf ./etc/profile.d/oi.sh.x86_64 $RPM_BUILD_ROOT/etc/profile.d/oi.sh

mkdir -p $RPM_BUILD_ROOT/%{installation_dir}/nodechecker/etc
cp -rf ./opt/monitoring/* $RPM_BUILD_ROOT/%{installation_dir}/nodechecker
cp -rf ./lib/python/nodechecker/nodechecker.conf $RPM_BUILD_ROOT/%{installation_dir}/nodechecker/etc/

mkdir -p $RPM_BUILD_ROOT/%{installation_dir}/collectd
cp -rf ./opt/collectd/* $RPM_BUILD_ROOT/%{installation_dir}/collectd

mkdir -p  $RPM_BUILD_ROOT/%{installation_dir}/nodechecker/var/log
mkdir -p $RPM_BUILD_ROOT/%{installation_dir}/nodechecker/var/lib/notifications/inbox
mkdir -p $RPM_BUILD_ROOT/%{installation_dir}/nodechecker/var/lib/notifications/sent

mkdir -p $RPM_BUILD_ROOT/usr/lib/python2.6/site-packages/nodechecker
cp -rf ./lib/python/nodechecker/* $RPM_BUILD_ROOT/usr/lib/python2.6/site-packages/nodechecker/

mkdir -p $RPM_BUILD_ROOT/%{installation_dir}/nodechecker/bin
cp -rf ./lib/python/nodechecker/control/start $RPM_BUILD_ROOT/%{installation_dir}/nodechecker/bin/
cp -rf ./lib/python/nodechecker/control/stop $RPM_BUILD_ROOT/%{installation_dir}/nodechecker/bin/

mkdir -p $RPM_BUILD_ROOT/usr/local/bin
cp -rf ./usr/local/bin/notify $RPM_BUILD_ROOT/usr/local/bin/

%files
%defattr(-,root,root,-)
/etc/init.d/oi3-collectd
/etc/init.d/oi3-healthmonitoring
/etc/profile.d/oi.sh
/%{installation_dir}/nodechecker/
/%{installation_dir}/collectd/
/usr/lib/python2.6/site-packages/nodechecker/
/usr/local/bin/notify

%post
chmod u+x /etc/init.d/oi3-collectd
chmod u+x /etc/init.d/oi3-healthmonitoring
chmod 777 $RPM_BUILD_ROOT/%{installation_dir}/nodechecker/var/lib/notifications/inbox
chmod 777 $RPM_BUILD_ROOT/%{installation_dir}/nodechecker/var/lib/notifications/sent
chmod 755 /usr/local/bin/notify
/sbin/chkconfig --add oi3-healthmonitoring
/sbin/chkconfig oi3-healthmonitoring on

%preun
if [ "$1" = 0 ]; then
   /sbin/chkconfig oi3-healthmonitoring off
   /%{installation_dir}/nodechecker/bin/stop
   /sbin/chkconfig --del oi3-healthmonitoring
fi
exit 0

%changelog
* Wed Dec 18 2013 Version update <vedran.bartonicek@tieto.com> - 3.0.0-1
- Installation path changed. Java upgrade to 1.7. Macro for installation path.

* Mon Apr 17 2013 Monitoring <vedran.bartonicek@tieto.com> 
- Initial version
