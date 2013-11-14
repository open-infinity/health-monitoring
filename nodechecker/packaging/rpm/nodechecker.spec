Name:           nodechecker
Version:        1.3.0
Release:        31%{?dist}
Summary:        Health Monitoring system for OpenInfinity
BuildArch:      x86_64
License:        Apache 2.0
URL:            http://www.tieto.com
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{release}-root-%(%{__id_u} -n)
Requires:       java-1.6.0-openjdk >= 1.6, Pound, python => 2.6

%description
Health Monitoring system for OpenInfinity

%prep
%setup -q

%install
mkdir -p $RPM_BUILD_ROOT/etc/init.d/
cp -rf ./etc/init.d/collectd $RPM_BUILD_ROOT/etc/init.d/
cp -rf ./etc/init.d/oi-healthmonitoring $RPM_BUILD_ROOT/etc/init.d/

mkdir -p $RPM_BUILD_ROOT/etc/profile.d/
cp -rf ./etc/profile.d/toas.sh.x86_64 $RPM_BUILD_ROOT/etc/profile.d/toas.sh

mkdir -p $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/nodechecker
cp -rf ./opt/monitoring/* $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/nodechecker
cp -rf ./lib/python/nodechecker/nodechecker.conf $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/nodechecker/etc/

mkdir -p $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/collectd
cp -rf ./opt/collectd/* $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/collectd

mkdir -p $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/nodechecker/var/lib/notifications/inbox
mkdir -p $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/nodechecker/var/lib/notifications/sent

mkdir -p $RPM_BUILD_ROOT/usr/lib/python2.6/site-packages/nodechecker
cp -rf ./lib/python/nodechecker/* $RPM_BUILD_ROOT/usr/lib/python2.6/site-packages/nodechecker/

mkdir -p $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/nodechecker/bin
cp -rf ./lib/python/nodechecker/control/start $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/nodechecker/bin/
cp -rf ./lib/python/nodechecker/control/stop $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/nodechecker/bin/

mkdir -p $RPM_BUILD_ROOT/usr/local/bin
cp -rf ./usr/local/bin/notify $RPM_BUILD_ROOT/usr/local/bin/

%files
%defattr(-,root,root,-)
/etc/init.d/collectd
/etc/init.d/oi-healthmonitoring
/etc/profile.d/toas.sh
/opt/openinfinity/2.0.0/healthmonitoring/nodechecker/
/opt/openinfinity/2.0.0/healthmonitoring/collectd/
/usr/lib/python2.6/site-packages/nodechecker/
/usr/local/bin/notify

%post
chmod u+x /etc/init.d/collectd
chmod u+x /etc/init.d/oi-healthmonitoring
chmod 777 $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/nodechecker/var/lib/notifications/inbox
chmod 777 $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/nodechecker/var/lib/notifications/sent
chmod 755 /usr/local/bin/notify
/sbin/chkconfig --add oi-healthmonitoring
/sbin/chkconfig oi-healthmonitoring on

%preun
if [ "$1" = 0 ]; then
   /sbin/chkconfig oi-healthmonitoring off
   /opt/openinfinity/2.0.0/healthmonitoring/nodechecker/bin/stop
   /sbin/chkconfig --del oi-healthmonitoring
fi
exit 0

%changelog
* Mon Apr 17 2013 Monitoring <vedran.bartonicek@tieto.com> 
- Initial version
