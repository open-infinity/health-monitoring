Name:           oi3-nodechecker
Version:        3.0.0
Release:        13%{?dist}
Summary:        Main Health Monitoring package for Open Infinity
BuildArch:      x86_64
License:        Apache 2.0
URL:            https://github.com/open-infinity/health-monitoring
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{release}-root-%(%{__id_u} -n)
Requires:       java-1.7.0-openjdk, Pound, python => 2.6

%global installation_path opt/openinfinity/3.0.0/healthmonitoring
%global installation_dir %{buildroot}/%{installation_path}

%description
Main Health Monitoring package for Open Infinity

%prep
%setup -q

%install
mkdir -p %{buildroot}%{_initddir}
cp -rf ./etc/init.d/oi3-collectd %{buildroot}%{_initddir}
cp -rf ./etc/init.d/oi3-healthmonitoring %{buildroot}%{_initddir}

mkdir -p %{buildroot}%{_sysconfdir}/profile.d/
cp -rf ./etc/profile.d/oi.sh.x86_64 %{buildroot}%{_sysconfdir}/profile.d/oi.sh

mkdir -p %{installation_dir}/nodechecker/etc
cp -rf ./opt/monitoring/* %{installation_dir}/nodechecker
cp -rf ./lib/python/nodechecker/nodechecker.conf %{installation_dir}/nodechecker/etc/

mkdir -p %{installation_dir}/collectd
cp -rf ./opt/collectd/* %{installation_dir}/collectd

mkdir -p %{installation_dir}/nodechecker/var/log
mkdir -p %{installation_dir}/nodechecker/var/lib/notifications/inbox
mkdir -p %{installation_dir}/nodechecker/var/lib/notifications/sent

mkdir -p %{buildroot}/usr/lib/python2.6/site-packages/nodechecker
cp -rf ./lib/python/nodechecker/* %{buildroot}/usr/lib/python2.6/site-packages/nodechecker/

mkdir -p %{installation_dir}/nodechecker/bin
cp -rf ./lib/python/nodechecker/control/start %{installation_dir}/nodechecker/bin/
cp -rf ./lib/python/nodechecker/control/stop %{installation_dir}/nodechecker/bin/

mkdir -p %{buildroot}/usr/local/bin
cp -rf ./usr/local/bin/notify %{buildroot}/usr/local/bin/

%files
%defattr(-,root,root,-)
%{_initddir}/oi3-collectd
%{_initddir}/oi3-healthmonitoring
%{_sysconfdir}/profile.d/oi.sh
/%{installation_path}/nodechecker/
/%{installation_path}/collectd/
/usr/lib/python2.6/site-packages/nodechecker/
/usr/local/bin/notify

%post
chmod 755 %{_initddir}/oi3-collectd
chmod 755 %{_initddir}/oi3-healthmonitoring
chmod 777 %{installation_path}/nodechecker/var/lib/notifications/inbox
chmod 777 %{installation_path}/nodechecker/var/lib/notifications/sent
chmod 755 /usr/local/bin/notify
/sbin/chkconfig --add oi3-healthmonitoring
/sbin/chkconfig oi3-healthmonitoring on

%preun
if [ "$1" = 0 ]; then
   /sbin/service oi3-healthmonitoring stop >/dev/null 2>&1
   /sbin/chkconfig --del oi3-healthmonitoring
fi
exit 0

%postun
if [ "$1" -ge "1" ] ; then
   /sbin/service oi3-healthmonitoring condrestart >/dev/null 2>&1 || :
fi

%changelog
* Wed Jan 08 2014 Macros <vbartoni@gmail.com> - 3.0.0-9
- Usage of macros. Init files moved ro rc.d/init.d. %postun part added, to control package upgrade.

* Wed Dec 18 2013 Version update <vedran.bartonicek@tieto.com> - 3.0.0-1
- Installation path changed. Java upgrade to 1.7. Macro for installation path.

* Mon Apr 17 2013 Monitoring <vedran.bartonicek@tieto.com> 
- Initial version
