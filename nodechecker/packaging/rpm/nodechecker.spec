Name:           oi3-nodechecker
Version:        3.1.0
Release:        10%{?dist}
Summary:        Main Health Monitoring package for Open Infinity
BuildArch:      x86_64
License:        Apache 2.0
URL:            https://github.com/open-infinity/health-monitoring
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{release}-root-%(%{__id_u} -n)
Requires:       java-1.7.0-openjdk, Pound, python => 2.6

%global installation_path opt/openinfinity/3.1.0/healthmonitoring
%global installation_dir %{buildroot}/%{installation_path}

%description
Main Health Monitoring package for Open Infinity. It contains the main logic of the
monitoring system. Configures and controlls other OpenInfinity Health Monitoring
components: rrd-http-server, collectd and pound.  

%prep
%setup -q

%install
mkdir -p %{buildroot}%{_initddir}
#cp -rf ./etc/init.d/oi3-collectd %{buildroot}%{_initddir}
cp -rf ./etc/init.d/oi3-nodechecker %{buildroot}%{_initddir}

#mkdir -p %{buildroot}%{_sysconfdir}/profile.d/
#cp -rf ./etc/profile.d/oi.sh.x86_64 %{buildroot}%{_sysconfdir}/profile.d/oi.sh

mkdir -p %{installation_dir}/nodechecker/etc
cp -rf ./opt/monitoring/* %{installation_dir}/nodechecker
cp -rf ./lib/python/nodechecker/nodechecker.conf %{installation_dir}/nodechecker/etc/

#mkdir -p %{installation_dir}/collectd
#cp -rf ./opt/collectd/* %{installation_dir}/collectd

#mkdir -p %{installation_dir}/pound
#cp -rf ./opt/pound/* %{installation_dir}/pound

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
#%{_initddir}/oi3-collectd
%{_initddir}/oi3-nodechecker
%{_sysconfdir}/profile.d/oi.sh
/%{installation_path}/nodechecker/
#/%{installation_path}/collectd
/%{installation_path}/pound/
/usr/lib/python2.6/site-packages/nodechecker/
/usr/local/bin/notify

%post
#TODO: move collectd config stuff to colelctd package
useradd nodechecker > /dev/null 2>&1
#usermod -a -G collectd nodechecker  > /dev/null 2>&1
mkdir -p /%{installation_path}/nodechecker/var/run

chown -R nodechecker /%{installation_path}/nodechecker
chown -R nodechecker /%{installation_path}/pound
chown nodechecker /etc/pound.cfg
#chown -R collectd /%{installation_path}/collectd
#chown -R root /%{installation_path}/collectd/sbin
#chown -R root /%{installation_path}/pound/bin

chmod 775 /%{installation_path}/collectd/etc/collectd.d
chmod 755 %{_initddir}/oi3-collectd
chmod 755 %{_initddir}/oi3-nodechecker
chmod 777 /%{installation_path}/nodechecker/var/lib/notifications/inbox
chmod 777 /%{installation_path}/nodechecker/var/lib/notifications/sent
chmod 755 /usr/local/bin/notify


/sbin/chkconfig --add oi3-nodechecker
/sbin/chkconfig oi3-nodechecker on

%preun
echo "unistalling oi3-nodechecker"
if [ "$1" = 0 ]; then
   echo "stopping oi3-nodechecker service"
   /sbin/service oi3-nodechecker stop >/dev/null 2>&1
   /sbin/chkconfig --del oi3-nodechecker
fi
exit 0

%postun
#if [ "$1" -ge "1" ] ; then
#   1/sbin/service oi3-nodechecker condrestart >/dev/null 2>&1 || :
#fi
rm -rf /%{installation_path}/nodechecker
#rm -rf/%{installation_path}/collectd/etc
#rm -rf/%{installation_path}/collectd/share

%changelog
* Mon Oct 27 2014 Version update <vbartoni@gmail.com> - 3.1.0-10
- User set to nodechecker

* Fri Jun 13 2014 Version update <vbartoni@gmail.com> - 3.1.0-1
- Set version to 3.1.0. Updated installation path

* Wed Jan 08 2014 Macros <vbartoni@gmail.com> - 3.0.0-9
- Usage of macros. Init files moved to rc.d/init.d. %postun part added, to control package upgrade.

* Wed Dec 18 2013 Version update <vedran.bartonicek@tieto.com> - 3.0.0-1
- Installation path changed. Java upgrade to 1.7. Macro for installation path.

* Mon Apr 17 2013 Monitoring <vedran.bartonicek@tieto.com> 
- Initial version
