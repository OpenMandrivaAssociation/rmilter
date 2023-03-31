%define rmilter_user      rmilter
%define rmilter_group     adm
%define rmilter_home      %{_localstatedir}/run/rmilter

Name:		rmilter
Version:	1.10.0
Release:	4
Summary:	Multi-purpose milter
Group:		System/Servers

# BSD License (two clause)
# http://www.freebsd.org/copyright/freebsd-license.html
License:	BSD-2-Clause
URL:	    https://github.com/vstakhov/rmilter
BuildRequires:  sendmail-devel,pkgconfig(libssl),pkgconfig(libpcre),pkgconfig(glib-2.0)
BuildRequires:  cmake,bison,flex,pkgconfig(opendkim),pkgconfig(sqlite3)
BuildRequires:  systemd
Requires(pre):  systemd
Requires(post): systemd
Requires(preun): systemd
Requires(postun): systemd
Requires(pre):  shadow
Suggests:	clamav clamd rspamd redis

Source0:	https://github.com/vstakhov/rmilter/archive/%{version}.tar.gz
# Based on, but not identical to https://rspamd.com/rpm/SOURCES/%{name}.conf.common
Source1:	%{name}.conf
Source2:	https://rspamd.com/rpm/SOURCES/80-rmilter.preset

%description
The rmilter utility is designed to act as milter for sendmail and postfix MTA.
It provides several filter and mail scan features.

%prep
%setup -q
rm -rf %{buildroot} || true

%build

%{__cmake} \
	-DCMAKE_C_OPT_FLAGS="%{optflags}" \
	-DCMAKE_INSTALL_PREFIX=%{_prefix} \
	-DCONFDIR=%{_sysconfdir}/rmilter \
	-DMANDIR=%{_mandir} \
	-DWANT_SYSTEMD_UNITS=ON \
	-DSYSTEMDDIR=%{_unitdir} \
	-DNO_SHARED=ON \
	-DRMILTER_GROUP=%{rmilter_group} \
	-DRMILTER_USER=%{rmilter_user}

%make

%install
%make install DESTDIR=%{buildroot} INSTALLDIRS=vendor

%{__install} -p -d -D -m 0755 %{buildroot}%{_sysconfdir}/%{name}
%{__install} -p -D -m 0644 %{SOURCE1} %{buildroot}%{_sysconfdir}/%{name}/
%{__install} -p -D -m 0644 %{SOURCE2} %{buildroot}%{_presetdir}/80-rmilter.preset
%{__install} -p -D -d -m 0755 %{buildroot}%{_sysconfdir}/%{name}/rmilter.conf.d/

sed -i -e 's,User=_rmilter,User=%{rmilter_user},g' %{buildroot}%{_unitdir}/%{name}.service

%pre
%{_sbindir}/groupadd -r %{rmilter_group} 2>/dev/null || :
%{_sbindir}/useradd -g %{rmilter_group} -c "Rmilter user" -s /sbin/nologin -r %{rmilter_user} 2>/dev/null || :

%files
%defattr(-,root,root,-)
%{_unitdir}/%{name}.service
%{_presetdir}/80-rmilter.preset
%{_sbindir}/rmilter
%dir %{_sysconfdir}/rmilter
%dir %{_sysconfdir}/rmilter/rmilter.conf.d
%config(noreplace) %{_sysconfdir}/rmilter/%{name}.conf
