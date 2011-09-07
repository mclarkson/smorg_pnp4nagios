Name: pnp4nagios
Version: 0.6.14
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
%defattr(644,root,root,755)
%doc AUTHORS ChangeLog COPYING INSTALL README 
%doc THANKS contrib/
%dir %{_sysconfdir}/pnp4nagios
%dir %{_libexecdir}/pnp4nagios
%config(noreplace) %{_sysconfdir}/pnp4nagios/*
%{_libdir}/npcdmod.o
%{_libdir}/kohana
%{_sysconfdir}/httpd/conf.d/pnp4nagios.conf
%attr(755,root,root) %{_libdir}/npcdmod.o
%attr(755,root,root) %{_initrddir}/npcd
%attr(755,root,root) %{_sbindir}/npcd
%attr(755,root,root) %{_libexecdir}/pnp4nagios/rrd_convert.pl
%attr(755,root,root) %{_libexecdir}/pnp4nagios/verify_pnp_config.pl
%attr(755,root,root) %{_libexecdir}/pnp4nagios/process_perfdata.pl
%attr(755,root,root) %{_libexecdir}/pnp4nagios/check_pnp_rrds.pl
%attr(755,nagios,nagios) %{_localstatedir}/lib/%{name}
%attr(755,nagios,nagios) %{_localstatedir}/log/%{name}
%attr(755,nagios,nagios) %{_localstatedir}/spool/%{name}
%{_datadir}/nagios/html/pnp4nagios 

