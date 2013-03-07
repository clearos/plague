# Fedora 18 or newer only

BuildArch: noarch

Summary: Distributed build system for RPMs
Name: plague
Version: 0.4.5.8
Release: 12%{?dist}
License: GPLv2+
Group: Development/Tools
#Source: http://fedoraproject.org/projects/plague/releases/%{name}-%{version}.tar.bz2
Source: http://mschwendt.fedorapeople.org/plague/%{name}-%{version}.tar.bz2
Source1: plague-builder.service
Source2: plague-server.service
URL: http://www.fedoraproject.org/wiki/Projects/Plague

# some fixes for systemd compatibility - it doesn't like double-fork daemons,
# where the parent process exits before the main PID is known
Patch0: plague-0.4.5.8-systemd-compat.patch
# Patch that allows using the sqlite3 module from python-2.5+ stdlib
Patch1: plague-python25-sqlite.patch
# Let builder return only .rpm/.log files
Patch2: plague-0.4.5.8-filter-results.patch

BuildRequires: python
BuildRequires: systemd-units
Requires: createrepo >= 0.4.7
# get the version of the sqlite api thats available to us
%if 0%{?rhel} && 0%{?rhel} <= 5
Requires: python-sqlite
%endif
# All other distros have sqlite3 built into the python stdlib

Requires: %{name}-common = %{version}-%{release}
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units


%description
The Plague build system is a client/server distributed build system for
building RPM packages.  This package provides the plague server.


%package common
Summary: Common resources for the Plague build system
Group: Development/Tools
Requires: pyOpenSSL

%description common
This package includes the common Python module that all Plague services
require.


%package builder
Summary: Builder daemon for Plague builder slaves
Group: Development/Tools
Requires: %{name}-common = %{version}-%{release}
Requires: yum >= 2.2.1
Requires: mock >= 0.8
Requires(pre): /usr/sbin/useradd
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

%description builder
The Plague builder does the actual RPM package building on slave machines.

%package client
Summary: Package queueing client for the Plague build system
Group: Development/Tools
Requires: %{name}-common = %{version}-%{release}

%description client
Client program for enqueueing package builds and interrogating the build
system.


%package utils
Summary: Utility programs for the Plague build system
Group: Development/Tools
Requires: %{name}-common = %{version}-%{release}
Requires: %{name} = %{version}-%{release}

%description utils
This package includes user utilities for the Plague build system, including
the interface to the build server.


%prep
%setup -q
%patch0 -p1 -b .systemd-compat
%patch1 -p1 -b .sqlite3
%patch2 -p1 -b .filter-results

%build
make


%install
make DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p" install
mkdir -p $RPM_BUILD_ROOT%{_unitdir}
install -p -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}
install -p -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_unitdir}
chmod +x $RPM_BUILD_ROOT%{_bindir}/*
install -p -D -m 0644 etc/plague-builder.config $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}-builder
install -p -D -m 0755 etc/plague-builder.init $RPM_BUILD_ROOT%{_initrddir}/%{name}-builder
install -p -D -m 0644 etc/plague-server.config $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}-server
install -p -D -m 0755 etc/plague-server.init $RPM_BUILD_ROOT%{_initrddir}/%{name}-server
mkdir -p $RPM_BUILD_ROOT/var/lib/plague/builder


%post
%systemd_post plague-server.service

%preun
%systemd_preun plague-server.service

%postun
%systemd_postun_with_restart plague-server.service 


%post builder
%systemd_post plague-builder.service

%pre builder
/usr/sbin/useradd -G mock -s /sbin/nologin -M -r -d /var/lib/plague/builder plague-builder 2>/dev/null || :

%preun builder
%systemd_preun plague-builder.service

%postun builder
%systemd_postun_with_restart plague-builder.service 


%files
%defattr(-, root, root)
%{_bindir}/%{name}-server
%dir %{_datadir}/%{name}/server
%{_datadir}/%{name}/server/*.py*
%dir %{_sysconfdir}/%{name}/server
%dir %{_sysconfdir}/%{name}/server/certs
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}-server
%{_initrddir}/%{name}-server
%{_unitdir}/%{name}-server.service
%doc www

%files common
%defattr(-, root, root)
%doc README ChangeLog
%dir %{_sysconfdir}/%{name}
%dir %{_datadir}/%{name}
%dir /usr/lib/python?.?/site-packages/%{name}
/usr/lib/python?.?/site-packages/%{name}/*.py*

%files builder
%defattr(-, root, root)
%{_bindir}/%{name}-builder
%dir %{_datadir}/%{name}/builder
%{_datadir}/%{name}/builder/*.py*
%dir %{_sysconfdir}/%{name}/builder
%dir %{_sysconfdir}/%{name}/builder/certs
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}-builder
%{_initrddir}/%{name}-builder
%{_unitdir}/%{name}-builder.service
%dir /var/lib/plague
%attr(0755, plague-builder, plague-builder) /var/lib/plague/builder

%files client
%defattr(-, root, root)
%{_bindir}/%{name}-client

%files utils
%defattr(-, root, root)
%{_bindir}/%{name}-user-manager
%{_bindir}/%{name}-certhelper


%changelog
* Thu Mar  7 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.8-12
- Fix the patch in -11.

* Mon Mar  4 2013 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.8-11
- Since new Mock creates additional result files "available_pkgs" and
  "installed_pkgs", but the Plague Server only wants .rpm/.log files,
  ignore anything else.

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.5.8-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Aug 30 2012 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.8-9
- Introduce new systemd-rpm macros in plague spec file (#850272), but
  don't add conditionals for "Fedora 17 and older".

* Sat Jul 21 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.5.8-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Fri Feb 17 2012 Toshio Kuratomi <toshio@fedoraproject.org> - 0.4.5.8-7
- Apply the patch for real

* Fri Feb 17 2012 Toshio Kuratomi <toshio@fedoraproject.org> - 0.4.5.8-6
- Patch to allow plague to run with the sqlite3 module from the python-2.5+ stdlib

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.5.8-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Wed Nov  9 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.8-4
- drop old chkconfig/service usage and deps
- add systemd package deps also to -builder package
- s/multiuser/multi-user/ in systemd unit files
- start After=rpcbind.service 

* Tue Nov  8 2011 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.8-3
- Some fixes for systemd compatibility, e.g. patch daemonize.py double-fork
  to let parent die only after second child has written PID file.
- Add systemd unit files and related package scriptlets.

* Wed Feb 09 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.5.8-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Tue Aug 10 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.8-1
- update to 0.4.5.8 to get rid of patches

* Wed Aug  4 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.7-9.20100505cvs
- Fix Python 2.7 xmlrpclib/httplib fall-out in SSLConnection.py and 
  XMLRPCServerProxy.py (#621340).

* Wed Jul 21 2010 David Malcolm <dmalcolm@redhat.com> - 0.4.5.7-8.20100505cvs
- Rebuilt for https://fedoraproject.org/wiki/Features/Python_2.7/MassRebuild

* Wed May  5 2010 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.7-7.20100505cvs
- patch with fix from cvs (file download with Mock createrepo_on_rpms).

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.5.7-6.20090612cvs
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 17 2009 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.7-5.20090612cvs
- patch with fix from cvs (SSLConnection.py shutdown)

* Thu Feb 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0.4.5.7-4.20081216cvs
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Tue Dec 16 2008 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.7-3.20081216cvs
- patch with fixes from cvs, also to make work with Python 2.6

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.4.5.7-2
- Rebuild for Python 2.6

* Wed Nov  5 2008 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.7-1
- update to 0.4.5.7 (Python 2.4 fix and optional POSIX lockfile support)

* Sun Sep 21 2008 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.6-1
- update to 0.4.5.6

* Sat Sep 20 2008 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.5-2
- add fix for sqlite's limited ALTER TABLE

* Mon Sep  8 2008 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.5-1
- update to 0.4.5.5

* Sun Sep 07 2008 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.4-1
- update to 0.4.5.4 to make it work with MySQL 5

* Sun Sep  7 2008 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.3-2
- fix mod_user in plague-user-manager for sqlite2/3

* Fri Sep  5 2008 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5.3-1
- update to 0.4.5.3 for sqlite2 compatibility fixes for Fedora
- merge fedora pkg spec changes
- include the www tree as server pkg docs

* Thu Sep 04 2008 Dennis Gilmore <dennis@ausil.us> - 0.4.5.2-1
- fix bug in find option to plague-user-manager

* Wed Sep 03 2008 Dennis Gilmore <dennis@ausil.us> - 0.4.5.1-1
- update to 0.4.5.1  applying Michael schwendt's logging and mock patches
- using pysqlite2 on fedora and python-sqlite on RHEL
- requires mock > 0.8
- requires createrepo >= 0.4.7

* Wed Sep  3 2008 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.5-2
- add the patches from 0.4.5-0.4 (sqlite3, mock08, logtail)
- merge more spec changes

* Tue Sep 02 2008 Dennis Gilmore <dennis@ausil.us> - 0.4.5-1
- update to 0.4.5  lots of fixes 

* Thu May 22 2008 Seth Vidal <skvidal at fedoraproject.org> - 0.4.4.1-6
- licensing tag fix

* Tue Sep 18 2007 Michael Schwendt <mschwendt@fedoraproject.org> - 0.4.4.1-5
- Add dirs /etc/plague and /usr/share/plague to plague-common
  since "plague-builder" and "plague" use them (#233904).

* Fri Dec 15 2006 Toshio Kuratomi <toshio@tiki-lounge.com> - 0.4.4.1-4
- Small fix for a change in python 2.5's xmlrpc library.  The patch has been
  upstreamed.

* Thu Dec 14 2006 Jason L Tibbitts III <tibbs@math.uh.edu> - 0.4.4.1-3
- Rebuild for new Python

* Thu Sep 14 2006 Dennis Gilmore <dennis@ausil.us> 0.4.4.0-2
- add patch  for bad umask setting

* Mon Mar 13 2006 Dan Williams <dcbw@redhat.com> 0.4.4.1-1
- Update to 0.4.4.1
- Fix createrepo dep to >= 0.4.3 (#rh170531)

* Sun Mar 12 2006 Dan Williams <dcbw@redhat.com> 0.4.4-1
- Update to 0.4.4 release
    - Don't use pyOpenSSL's sendall() call, but simulate it to achieve
        timeouts, better error handling, and more efficient CPU usage
    - Fix up initscripts and lifecycle management
    - Implement a TERM handler in server & builder for clean shutdown
    - Ensure jobs don't hang around on builders if they get left there for
        some reason (ie, server didn't unlock repo for the job)
    - Make Additional Package Arches really work (kmod support)
- Own /usr/lib/python?.?/site-packages/plague (#rh172794#)
- Require createrepo >= 4.3 (#rh170531#)

* Tue Jan 24 2006 Dan Williams <dcbw@redhat.com> 0.4.3-6
- Increase build server builder thread sleep time to work around SSL issues
- Spawn mock in a new process group, and when killing jobs kill the entire
    process group.  Hopefully fix orphaned rpmbuild processes on job kill

* Mon Jan 23 2006 Dan Williams <dcbw@redhat.com> 0.4.3-5
- Restore builder connection timeout

* Mon Jan 23 2006 Dan Williams <dcbw@redhat.com> 0.4.3-4
- Revert SSL fixes from last build

* Sun Jan 22 2006 Dan Williams <dcbw@redhat.com> 0.4.3-3
- Don't traceback when killing jobs on builders
- Work around SSL hanging issues

* Tue Nov 29 2005 Dan Williams <dcbw@redhat.com> 0.4.3-2
- Move README and ChangeLog to -common package
- Traceback/debug functionality added in server, depends on
    threadframe module from elsewhere.  Disabled by default.

* Thu Nov 24 2005 Dan Williams <dcbw@redhat.com> 0.4.3-1
- Add socket timeouts for fileserver and xmlrpc bits

* Fri Nov 18 2005 Dan Williams <dcbw@redhat.com> 0.4.2-7
- Suspend builders on hard errors such as running out of disk space
- Retry downloads from server/builder 5 times, not 3
- Log retried downloads on the server
- Add socket timeouts to downloads to work around hanging issues
    when downloading from the builder (the downloading/done issue)

* Tue Nov 15 2005 Dan Williams <dcbw@redhat.com> 0.4.2-5
- Log kill requests on the server

* Mon Nov 14 2005 Dan Williams <dcbw@redhat.com> 0.4.2-4
- In the builder, close files we open before exec-ing the
    child process.  Fixes massive file descriptor leaks.

* Sun Nov 13 2005 Dan Williams <dcbw@redhat.com> 0.4.2-3
- Hopefully fix builds not moving past downloading/done
- Immediately kill jobs in the 'waiting' state when requested
- Utilize pthread_sigmask python module, if present, on Python
    2.3 and earlier to work around signal blocking issues in
    Python

* Tue Nov  1 2005 Dan Williams <dcbw@redhat.com> 0.4.2-2
- Make builders retry downloads from the server up to 3 times

* Tue Nov  1 2005 Dan Williams <dcbw@redhat.com> 0.4.2-1
- Fix job download from the builders
- Fix RPM copy to the repository on the server

* Mon Oct 31 2005 Dan Williams <dcbw@redhat.com> 0.4.1-1
- Fail jobs on restart if we can't access the original SRPM
- For the server, honor config file location passed in on
	the command line (Jeff Sheltren)
- Catch another mock failure case (Alexandr Kanevskiy)

* Tue Oct 25 2005 Dan Williams <dcbw@redhat.com> 0.4-6
- Retry downloads from builders up to 3 times before failing
    the job

* Tue Oct 25 2005 Dan Williams <dcbw@redhat.com> 0.4-5
- Add a MySQL database backend (Jeff Sheltren)
- Trap repo copy errors rather than doing a traceback
- On the builder, deal correctly with jobs in 'downloaded' state
    that have been killed

* Wed Oct 19 2005 Dan Williams <dcbw@redhat.com> 0.4-4
- Really fix client's "allow_uploads" problem

* Wed Oct 19 2005 Dan Williams <dcbw@redhat.com> 0.4-3
- Fix errors in client's 'job detail' function
- Ignore missing "allow_uploads" option in client config file
- Fix server when the Additional Package Arches section is missing
    from a target config file
- Make server more robust against random builder SSL issues

* Mon Oct 17 2005 Dan Williams <dcbw@redhat.com> 0.4-2
- Increase field size of 'username' and 'status' fields when
	we initially create them on the server.  Server ops will
	need to increase manually or blow away their jobdb.

* Sun Oct 16 2005 Dan Williams <dcbw@redhat.com> 0.4-1
- Version 0.4
    o Server:
        - Per-target config files, new format
        - Support PostgreSQL as a database backend

    o Builder:
        - Multiple concurrent builds with one builder process
        - Better tracking of mock child processes
        - Autodetect supported architectures and number of
            concurrent build processes
        - Per-target config files, new format

    o Client:
        - Ability to upload packages to server

    o Utilities:
        - New distro-rebuild.py utility
        - Fixes for certhelper.py

* Tue Aug 23 2005 Dan Williams <dcbw@redhat.com> 0.3.4-1
- Version 0.3.4
    o Make repo scripts actually work
    o Don't traceback when cleaning up job files if we have none

* Fri Aug 19 2005 Dan Williams <dcbw@redhat.com> 0.3.3-1
- Version 0.3.3
    o Add repo script support
    o Fix double-slashes in log URL (Ignacio Vazquez-Abrams)
    o Clear out old job info when requeueing jobs

* Mon Aug 15 2005 Dan Williams <dcbw@redhat.com> 0.3.2-3
- Clear out old job info when requeueing jobs

* Mon Aug 15 2005 Dan Williams <dcbw@redhat.com> 0.3.2-2
- Append %{?dist} to Releases to get correct precedence on FC3, FC4, and Rawhide

* Mon Aug 15 2005 Dan Williams <dcbw@redhat.com> 0.3.2-1
- Version 0.3.2
    o Fix errors in enqueue and enqueue_srpm return values
    o Implement client/server API versioning

* Thu Aug 11 2005 Dan Williams <dcbw@redhat.com> 0.3.1-1
- Version 0.3.1
    o Clean up web interface error handling, catches more errors
    o Clean up builder code, hopefully deal with block mock processes waiting
        to write to stderr
    o Use HTTP GET rather than POST for web forms, more back/forward/reload
        friendly (Ville Skyttä)

* Mon Aug  8 2005 Dan Williams <dcbw@redhat.com> 0.3-1
- Version 0.3

* Sat Jul 16 2005 Dan Williams <dcbw@redhat.com>
- Bump version to 0.2
- Grab python files from /usr/lib, not %%{_libdir} until the
    multiarch issues get worked out

* Sun Jun 26 2005 Dan Williams <dcbw@redhat.com>
- first version/packaging
