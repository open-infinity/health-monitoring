Name:           rrd-http-server
Version:        1.3.0
Release:        5%{?dist}
Summary:        Server for rrd data gathered by OpenInfinity Health monitoring
BuildArch:      x86_64
License:        Tieto
URL:            http://www.tieto.com
Source0:        %{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{release}-root-%(%{__id_u} -n)
Requires:       java-1.6.0-openjdk >= 1.6, jakarta-commons-daemon-jsvc >= 1.0.1, nodechecker

%description
The http server for rrd data gathered by OpenInfinity Health monitoring

%prep
%setup -q

%install
mkdir -p $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/rrd-http-server/lib/java
cp -rf ./lib/java/* $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/rrd-http-server/lib/java
mkdir -p $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/rrd-http-server/bin
cp -rf ./opt/rrd-http-server/bin/* $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/rrd-http-server/bin
mkdir -p $RPM_BUILD_ROOT/etc/init.d/
cp -rf ./etc/init.d/rrd-http-server $RPM_BUILD_ROOT/etc/init.d/
mkdir -p $RPM_BUILD_ROOT/opt/openinfinity/2.0.0/healthmonitoring/rrd-http-server/var/log

%files
%defattr(-,root,root,-)
/opt/openinfinity/2.0.0/healthmonitoring/rrd-http-server/
/etc/init.d/rrd-http-server

%post
useradd toas
chown toas /opt/openinfinity/2.0.0/healthmonitoring/rrd-http-server/var/log
chmod u+x /etc/init.d/rrd-http-server
chmod 755 /opt/openinfinity/2.0.0/healthmonitoring/rrd-http-server/bin/start-rrd-http-server.sh
chmod 755 /opt/openinfinity/2.0.0/healthmonitoring/rrd-http-server/bin/stop-rrd-http-server.sh
/sbin/chkconfig --add rrd-http-server
/sbin/chkconfig rrd-http-server on

%preun
if [ "$1" = 0 ]; then
   /sbin/chkconfig rrd-http-server off
   /opt/openinfinity/2.0.0/healthmonitoring/rrd-http-server/bin/stop-rrd-http-server.sh
   /sbin/chkconfig --del rrd-http-server
fi
exit 0

%changelog
* Thu Sep 19 2013 rrd-http-server <vedran.bartonicek@tieto.com>
- Create user toas

* Mon May 14 2013 rrd-http-server <vedran.bartonicek@tieto.com>
- Dependency to jsvc

* Mon May 07 2013 rrd-http-server <vedran.bartonicek@tieto.com> 
- Initial version
