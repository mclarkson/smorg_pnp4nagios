Name: pnp4nagios
Version: 0.6.19
Release: 1

Group: Applications/System
License: GPLv2
URL: http://www.pnp4nagios.org/
Source0: %{name}-%{version}.tar.gz
BuildRoot: %{_tmppath}/%{name}-buildroot
Packager: Mark Clarkson <mark.clarkson@smorg.co.uk>
Vendor: Smorg
Summary: Nagios performance data analysis tool



BuildRequires: rrdtool-perl
Requires: nagios
Requires: rrdtool-perl
Requires: php-gd
Requires(post): chkconfig
Requires(preun): chkconfig
Requires(preun): initscripts
Requires(postun): initscripts


%description
PNP is an addon to nagios which analyzes performance data provided by plugins
and stores them automatically into RRD-databases.


%prep
%setup -q -n %{name}-%{version}


%build
%configure --with-nagios-user=nagios \
           --with-nagios-group=nagios \
           --bindir=%{_sbindir} \
	   --libexecdir=%{_libexecdir}/%{name} \
	   --sysconfdir=%{_sysconfdir}/%{name} \
	   --localstatedir=%{_localstatedir}/log/%{name} \
	   --datadir=%{_datadir}/nagios/html/%{name} \
	   --datarootdir=%{_datadir}/nagios/html/%{name} \
	   --with-perfdata-dir=%{_localstatedir}/lib/%{name} \
	   --with-perfdata-spool-dir=%{_localstatedir}/spool/%{name}
make %{?_smp_mflags} all


%install
rm -rf $RPM_BUILD_ROOT
install -d -m 0755 ${RPM_BUILD_ROOT}/etc/httpd/conf.d

make install DESTDIR=$RPM_BUILD_ROOT INIT_OPTS= INSTALL_OPTS=
make install-webconf DESTDIR=$RPM_BUILD_ROOT INIT_OPTS= INSTALL_OPTS=
make install-config DESTDIR=$RPM_BUILD_ROOT INIT_OPTS= INSTALL_OPTS=
make install-init DESTDIR=$RPM_BUILD_ROOT INIT_OPTS= INSTALL_OPTS=
find $RPM_BUILD_ROOT/%{_sysconfdir}/pnp4nagios -name *-sample -exec rename "-sample" "" {} ';'
sed -i -e 's|/usr/libexec/process_perfdata.pl|/usr/libexec/pnp4nagios/process_perfdata.pl|' \
       -e 's|^log_type = syslog|log_type = file|' \
       $RPM_BUILD_ROOT/%{_sysconfdir}/pnp4nagios/npcd.cfg

mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/lib/%{name}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/spool/%{name}
mkdir -p $RPM_BUILD_ROOT%{_localstatedir}/log/%{name}


#%clean
#rm -rf $RPM_BUILD_ROOT


%post
/sbin/chkconfig --add npcd


%preun
if [ $1 = 0 ]; then
/sbin/service npcd stop >/dev/null 2>&1
/sbin/chkconfig --del npcd
fi


%postun
if [ "$1" -ge "1" ]; then
/sbin/service npcd condrestart >/dev/null 2>&1 || :
fi


%files
%defattr(-,nagios,nagios,-)
%doc AUTHORS
%doc ChangeLog
%doc COPYING
%doc INSTALL
%doc README
%doc THANKS
%config(noreplace) %{_sysconfdir}/%{name}/check_commands/check_all_local_disks.cfg-sample
%config(noreplace) %{_sysconfdir}/%{name}/check_commands/check_nrpe.cfg-sample
%config(noreplace) %{_sysconfdir}/%{name}/check_commands/check_nwstat.cfg
%config(noreplace) %{_sysconfdir}/%{name}/npcd.cfg
%config(noreplace) %{_sysconfdir}/%{name}/pages/web_traffic.cfg
%config(noreplace) %{_sysconfdir}/%{name}/process_perfdata.cfg
%config(noreplace) %{_sysconfdir}/%{name}/rra.cfg
%config(noreplace) %{_sysconfdir}/httpd/conf.d/%{name}.conf
%{_sysconfdir}/%{name}/background.pdf
%{_sysconfdir}/%{name}/config.php
%{_sysconfdir}/%{name}/misccommands.cfg-sample
%{_sysconfdir}/%{name}/nagios.cfg-sample
%{_sysconfdir}/%{name}/pnp4nagios_release
%attr(755,root,root) %{_sysconfdir}/rc.d/init.d/npcd
%attr(755,root,root) %{_sysconfdir}/rc.d/init.d/pnp_gearman_worker
%{_bindir}/npcd
%{_libdir}/pnp4nagios/npcdmod.o
%{_libdir}/%{name}
%{_libexecdir}/check_pnp_rrds.pl
%{_libexecdir}/process_perfdata.pl
%{_libexecdir}/rrd_convert.pl
%{_datadir}/%{name}
%{_mandir}/man8/npcd.8.gz
