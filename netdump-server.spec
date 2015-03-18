Summary: Server for network kernel message logging and crash dumps
Name: netdump-server
Version: 0.7.16
Release: 38%{dist}
# This is a Red Hat maintained package which is specific to
# our distribution.  Thus the source is only available from
# within this srpm.
Source0: netdump-%{version}.tar.gz
Source1: netdump-server.sysconfig
Source2: netdump-server.service

License: GPLv2
Group: System Environment/Daemons
BuildRoot: %(mktemp -ud %{_tmppath}/%{name}-%{version}-%{release}-XXXXXX) 
BuildRequires: glib-devel popt-devel
BuildRequires: systemd-units
Requires: /usr/bin/ssh-keygen /usr/bin/ssh fileutils textutils gawk
Requires(pre): shadow-utils
Requires(post): systemd-units
Requires(postun):systemd-units
Requires(preun):systemd-units

Patch0: netdump-init-typo.patch
Patch1: netdump-localport-option.patch 
Patch2: netdump-dumpdir.patch
Patch3: netdump-dumpdir-docs-scripts.patch
Patch4: netdump-retrans-on-log.patch
Patch5: netdump-verbose-logging.patch
Patch6: netdump-makefile-servonly.patch
Patch7: netdump-server-Makefile.patch
Patch8: netdump-server-init.patch
Patch9: netdump-clientport.patch
Patch10: netdump-server-use-ip-cmd.patch
Patch11: netdump-server-default-dir.patch
Patch12: netdump-ldflags.patch
Patch13: netdump-server-format-security.patch
Patch14: netdump-server-offsetof.patch

Group: System Environment/Daemons

%description
The netdump server listens to the network for crashed kernels to
contact it and then writes the oops log and a memory dump to
/var/netdump/crash before asking the crashed machine to reboot.

%prep
%setup -q -n netdump-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch12 -p1
%patch13 -p1
%patch14 -p1

%build
export CFLAGS="%{optflags} `glib-config --cflags` -fPIE"
export LDFLAGS="-pie"
make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
mkdir -p $RPM_BUILD_ROOT
DESTDIR=$RPM_BUILD_ROOT make install
mkdir -p $RPM_BUILD_ROOT/etc/sysconfig
install -m 644 %{SOURCE1} $RPM_BUILD_ROOT/etc/sysconfig/netdump-server
install -D -p -m 0644 %{SOURCE2} $RPM_BUILD_ROOT/%{_unitdir}/netdump-server.service
mkdir -p $RPM_BUILD_ROOT/var/netdump/crash/netdump

%if 0%{?fedora} >= 23
rm -rf $RPM_BUILD_ROOT/etc/rc.d
%endif

%clean
rm -rf $RPM_BUILD_ROOT


%pre
getent group netdump >/dev/null || groupadd -r -g 34 -f netdump 
getent passwd netdump >/dev/null || \
useradd -r -u 34 -g netdump -d /var/netdump/crash/netdump -s /bin/bash \
	-c "Network Crash Dump user" netdump 
exit 0

%post
%systemd_post netdump-server.service

%postun
%systemd_postun_with_restart netdump-server.service

%preun
%systemd_preun netdump-server.service

%files
%defattr(-,root,root)
/usr/sbin/netdump-server
%config(noreplace) %attr(0644,root,root)/etc/sysconfig/netdump-server
%dir %attr(-,netdump,netdump)/var/netdump/crash
%dir %attr(0700,netdump,netdump)/var/netdump/crash/.ssh
%config(noreplace) %attr(0600,netdump,netdump)/var/netdump/crash/.ssh/authorized_keys2
%dir %attr(0700,netdump,netdump)/var/netdump/crash/magic
%dir %attr(-,netdump,netdump)/var/netdump/crash/scripts
%dir %attr(-,netdump,netdump)/var/netdump/crash/netdump
%if 0%{??fedora} < 23
/etc/rc.d/init.d/netdump-server
%endif
%{_unitdir}/netdump-server.service

%{_mandir}/man8/netdump-server.8*
%doc README
%doc COPYING

%changelog
* Wed Mar 18 2015 Adam Jackson <ajax@redhat.com> 0.7.16-38
- Drop sysvinit script from F23+

* Sun Aug 17 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.16-37
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.16-36
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Tue Dec 03 2013 Neil Horman <nhorman@redhat.com> - 0.7.16-35
- Fix build breaks with -Werror=format-security flag (bz 1037214)
- Fix missing offsetof definition

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.16-34
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Apr 22 2013 Neil Horman <nhorman@redhat.com> - 0.7.16-33
- Updated to build netdump-server with -pie

* Fri Feb 22 2013 Neil Horman <nhorman@redhat.com> - 0.7.16-32
- Updated to use service script for systemd (bz 914748)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.16-31
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.16-30
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Jan 27 2012 Neil Horman <nhorman@redhat.com> - 0.7.16-29
- Removing unneeed Requires on ifconfig (bz 784923)

* Fri Jan 27 2012 Neil Horman <nhorman@redhat.com> - 0.7.16-28
- Swapped use of ip for ifconfig (bz 784923)

* Fri Jan 13 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.16-27
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.16-26
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Jul 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.16-25
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.7.16-24
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Fri Jul 11 2008 Neil Horman <nhorman@redhat.com> - 0.7.16-23
- Respond to clients listening on ports other than 6666 (bz 454703)

* Tue Feb 19 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 0.7.16-22
- Autorebuild for GCC 4.3

* Fri Dec 14 2007 Neil Horman <nhorman@redhat.com> - 0.7.16-21
- Updating build flags to properly pass smp flags

* Wed Dec 12 2007 Neil Horman <nhorman@redhat.com> - 0.7.16-20
- Fixing licensing issues to be unambiguously GPLv2

* Tue Dec 04 2007 Neil Horman <nhorman@redhat.com> - 0.7.16-19
- More fixes for EPEL review

* Mon Dec 03 2007 Neil Horman <nhorman@redhat.com> - 0.7.16-18
- More fixes for EPEL review

* Mon Nov 26 2007 Neil Horman <nhorman@redhat.com> - 0.7.16-17
- More fixes for EPEL review

* Mon Nov 20 2007 Neil Horman <nhorman@redhat.com> - 0.7.16-16
- Fixed spec file for rpmlint/review

* Mon Nov 12 2007 Neil Horman <nhorman@redhat.com> - 0.7.16-15
- Updating for EPEL inclusion

* Fri Mar 09 2007 Neil Horman <nhorman@redhat.com> - 0.7.16-13
- Add verbose logging to netdump
- fixed up packaging error

* Mon Mar 05 2007 Neil Horman <nhorman@redhat.com> - 0.7.16-11
- Allow netdump-server to retrans as long as we get log data (bz 226701)

* Tue Feb 13 2007 Neil Horman <nhorman@redhat.com> - 0.7.16-10
- update netdump-server with docs/scripts for bz 198863

* Thu Jan 18 2007 Neil Horman <nhorman@redhat.com> - 0.7.16-9
- update netdump-server to allow for configurable dump directory (bz 198863)

* Wed Oct 18 2006 Neil Horman <nhorman@redhat.com> - 0.7.16-8
- update previous initscript patch to pass ipaddr to netconsole (bz 211283)

* Wed Jun 21 2006 Neil Horman <nhorman@redhat.com> - 0.7.16-4
- fix netdump to pass localport option to kernel in RHEL4

* Tue Jun 20 2006 Neil Horman <nhorman@redhat.com> - 0.7.16-3
- fix typo in init script (bz 186625)

* Tue Apr 25 2006 Thomas Graf <tgraf@redhat.com> - 0.7.16-1
- update to version 0.7.16

* Mon Nov 21 2005 Dave Anderson <anderson@redhat.com> - 0.7.14-4
- Updated source package to netdump- 0.7.14.tar.gz:
  Creates target /var/crash/ directory on the fly if it does not
  exist or has been removed.  BZ #162587 (RHEL3 BZ #162586)
  Close vmcore before netdump-reboot script is run, allowing
  unimpeded usage of the file by a custom script.  (RHEL3 BZ #165100)
  Made /etc/sysconfig/netdump config(noreplace)  (RHEL3 BZ #168601)
  Generate syslog messages if any script fails to execute.
  Use sparse file space in vmcore if page is zero-filled.
  Update README.client re: usage of alt-sysrq-c for forced crashes.
  Cleaned up numerous compiler warnings seen in Fedora build environment.

* Mon Aug  1 2005 Jeff Moyer <jmoyer@redhat.com> - 0.7.10-3
- If the sysconfig file specifies all of the needed information, then don't
  fail in the event that the server is either unreachable or the name is
  unresolvable at load time.  BZ #161513

* Tue Mar  1 2005 Jeff Moyer <jmoyer@redhat.com> - 0.7.7-3
- Add support for auto-detecting the first hop on the way to the netdump
  server.

* Tue Dec 21 2004 Dave Anderson <anderson@redhat.com> - 0.7.5-2
- Updated source package to netdump- 0.7.5.tar.gz:
  Allows multiple "service netdump start" to handle magic numbers
  properly.  BZ #142752

* Tue Nov 30 2004 Dave Anderson <anderson@redhat.com> - 0.7.4-2
- Fix for unintentional failure of netconsole modprobe when NETLOGADDR=NONE.
  BZ #141373.

* Wed Nov 24 2004 Dave Anderson <anderson@redhat.com> - 0.7.3-2
- Replaces "set" usage with "read" for gathering arp output in
  print_address_info().  BZ #139781.
- Convert netdump-server.8 man page to UTF-8 format.  BZ #140707

* Mon Nov 22 2004 Dave Anderson <anderson@redhat.com> - 0.7.1-2
- Changed netdump.init file to use "set -f" in print_address_info().
  Fixes "service netdump start" bug if /e, /t, /h, or /r files exist,
  i.e., characters in "ether".

* Mon Nov 15 2004 Dave Anderson <anderson@redhat.com> - 0.7.0-2
- rebuild for RHEL-4

* Wed Sep 29 2004 Dave Anderson <anderson@redhat.com>  - 0.7.0-1
- Added BuildRequires and updated to latest package

* Fri Jul  9 2004 Jeff Moyer <jmoyer@redhat.com> - 0.6.13-1
- More init script fixes.  Namely, don't load netdump module if netdumpaddr 
  isn't filled in.

* Thu Jul  8 2004 Jeff Moyer <jmoyer@redhat.com> - 0.6.12-1
- Add support for 2.6 netdump.
- Allow netlog to be configured indepndently from netdump.
- Change the server to create only one directory in /var/crash per boot
  of a system.

* Tue Nov 02 2003 Dave Anderson <anderson@redhat.com> - 0.6.11-3
- rebuild

* Tue Nov 02 2003 Dave Anderson <anderson@redhat.com> - 0.6.11-2
- fix config_init() in configuration.c to work with PPC64. 
- fix netdump.init to allow SYSLOGADDR to be configured w/o NETDUMPADDR, and
- to properly handle configuration errors.

* Thu Oct 23 2003 Jeff Moyer <jmoyer@redhat.com> - 0.6.11-1
- Incorporate the latest netdump sources.  See file ChangeLog.

* Wed Sep 10 2003 Dave Anderson <anderson@redhat.com> - 0.6.10-2
- correct README.client to indicate netdump password (instead of root)

* Fri Aug 15 2003 Michael K. Johnson <johnsonm@redhat.com> - 0.6.10-1
- make iconv happy with man page

* Tue Aug 05 2003 Michael K. Johnson <johnsonm@redhat.com> - 0.6.9-4
- rebuild

* Mon Aug 04 2003 Michael K. Johnson <johnsonm@redhat.com> - 0.6.9-3
- rebuild

* Mon Jul 07 2003 Dave Anderson <anderson@redhat.com> - 0.6.9-2
- memory_packet(): cast lseek() offset argument as off_t to avoid wrap-around.
- memory_remove_outstanding_timeouts(): remove return arg to avoid warning.
 
* Mon Mar 17 2003 Michael K. Johnson <johnsonm@redhat.com> - 0.6.9-1
- fixed references to ttywatch instead of netdump-server in man page

* Wed Feb 26 2003 Dave Anderson <anderson@redhat.com> - 0.6.8-3
- built 0.6.7-1.1 for AS2.1 errata; bumped to 0.6.8-3 for future builds

* Tue Jan 28 2003 Michael K. Johnson <johnsonm@redhat.com> - 0.6.8-2
- rebuild

* Fri Dec 13 2002 Elliot Lee <sopwith@redhat.com>
- Rebuild

* Fri Apr 12 2002 Michael K. Johnson <johnsonm@redhat.com>
- added call to condrestart

* Tue Apr 02 2002 Michael K. Johnson <johnsonm@redhat.com>
- mhz separated from IDLETIMEOUT

* Thu Mar 21 2002 Michael K. Johnson <johnsonm@redhat.com>
- netdump and syslog disassociated

* Thu Mar 21 2002 Michael K. Johnson <johnsonm@redhat.com>
- added IDLETIMEOUT

* Tue Mar 19 2002 Michael K. Johnson <johnsonm@redhat.com>
- netconsole module now does arp, netdump-arphelper no longer needed

* Mon Mar 18 2002 Michael K. Johnson <johnsonm@redhat.com>
- special netdump dsa key

* Fri Mar 15 2002 Michael K. Johnson <johnsonm@redhat.com>
- added syslog setup

* Thu Mar 14 2002 Michael K. Johnson <johnsonm@redhat.com>
- netdump-client -> netdump
- finish ssh setup in netdump package

* Tue Feb 19 2002 Alex Larsson <alexl@redhat.com>
- shut up post scripts

* Tue Dec 18 2001 Alex Larsson <alexl@redhat.com>
- Update version to 0.2

* Thu Dec  6 2001 Alex Larsson <alexl@redhat.com>
- Initial build.
