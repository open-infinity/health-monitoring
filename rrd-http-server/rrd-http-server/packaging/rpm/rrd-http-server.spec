Name:           oi3-rrd-http-server
Version:        3.1.0
Release:        2%{?dist}
Summary:        HTTP Server for rrd data gathered by Health Monitoring for Open Infinity
BuildArch:      x86_64
License:        Apache 
URL:            http://www.tieto.com
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{release}-root-%(%{__id_u} -n)
Requires:       java-1.7.0-openjdk, jakarta-commons-daemon-jsvc >= 1.0.1, oi3-nodechecker

%global installation_dir opt/openinfinity/3.1.0/healthmonitoring

%description
The http server for rrd data gathered by Health Monitoring for Open Infinity

%prep
%setup -q

%install
mkdir -p $RPM_BUILD_ROOT/%{installation_dir}/rrd-http-server/lib/java
cp -rf ./lib/java/* $RPM_BUILD_ROOT/%{installation_dir}/rrd-http-server/lib/java
mkdir -p $RPM_BUILD_ROOT/%{installation_dir}/rrd-http-server/bin
cp -rf ./opt/rrd-http-server/bin/* $RPM_BUILD_ROOT/%{installation_dir}/rrd-http-server/bin
mkdir -p $RPM_BUILD_ROOT/etc/init.d/
cp -rf ./etc/init.d/oi3-rrd-http-server $RPM_BUILD_ROOT/etc/init.d/
mkdir -p $RPM_BUILD_ROOT/%{installation_dir}/rrd-http-server/var/log

%files
%defattr(-,root,root,-)
/%{installation_dir}/rrd-http-server/
/etc/init.d/oi3-rrd-http-server

%post
useradd oiuser
chown oiuser /%{installation_dir}/rrd-http-server/var/log
chmod u+x /etc/init.d/oi3-rrd-http-server
chmod 755 /%{installation_dir}/rrd-http-server/bin/start-rrd-http-server.sh
chmod 755 /%{installation_dir}/rrd-http-server/bin/stop-rrd-http-server.sh
/sbin/chkconfig --add oi3-rrd-http-server
/sbin/chkconfig oi3-rrd-http-server on

%preun
if [ "$1" = 0 ]; then
   /sbin/chkconfig oi3-rrd-http-server off
   /%{installation_dir}/rrd-http-server/bin/stop-rrd-http-server.sh
   /sbin/chkconfig --del oi3-rrd-http-server
fi
exit 0

%changelog
* Fri Jun 13 2014 Vedran Bartonicek <vedran.bartonicek@tieto.com> - 3.1.0-1
- Version change to 3.1.0. Installation path changed accordinglly.

* Wed Dec 18 2013 Vedran Bartonicek <vedran.bartonicek@tieto.com> - 3.0.0-1
- Version change. Macro for path and version. Java version changed to 1.7. User changed to oiuser.

* Thu Sep 19 2013 Vedran Bartonicek <vedran.bartonicek@tieto.com>
- Create user toas

* Mon May 14 2013 Vedran Bartonicek <vedran.bartonicek@tieto.com>
- Dependency to jsvc

* Mon May 07 2013 Vedran Bartonicek <vedran.bartonicek@tieto.com> 
- Initial version
