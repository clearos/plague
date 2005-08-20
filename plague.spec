BuildArch: noarch

Summary: Distributed build system for RPMs
Name: plague
Version: 0.3.3
Release: 1%{?dist}
License: GPL
Group: Development/Tools
Source: http://people.redhat.com/dcbw/plague/%{name}-%{version}.tar.bz2
URL: http://people.redhat.com/dcbw/plague
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: python-sqlite, createrepo
Requires: %{name}-common = %{version}-%{release}
Requires(post): /sbin/chkconfig
Requires(post): /sbin/service
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service

%description
The Plague build system is a client/server distributed build system for
building RPM packages.  This package provides the plague server.


%package common
Summary: Common resources for the Plague build system
Group: Development/Tools
Requires: pyOpenSSL

%description common
This package includes the common Python module that all Plague services require.


%package builder
Summary: Builder daemon for Plague builder slaves
Group: Development/Tools
Requires: %{name}-common = %{version}-%{release}
Requires: yum >= 2.2.1, mock >= 0.3
Requires(post): /sbin/chkconfig
Requires(post): /sbin/service
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service
Requires(pre): /usr/sbin/useradd

%description builder
The Plague builder does the actual RPM package building on slave machines.

%package client
Summary: Package queueing client for the Plague build system
Group: Development/Tools
Requires: %{name}-common = %{version}-%{release}

%description client
Client program for enqueueing package builds and interrogating the build system.


%package utils
Summary: Utility programs for the Plague build system
Group: Development/Tools
Requires: %{name}-common = %{version}-%{release}

%description utils
This package includes user utilities for the Plague build system, including
the interface to the build server.


%prep
%setup -q

%build
make


%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install
install -D -m 0644 etc/plague-builder.config $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}-builder
install -D -m 0755 etc/plague-builder.init $RPM_BUILD_ROOT%{_initrddir}/%{name}-builder
install -D -m 0644 etc/plague-server.config $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/%{name}-server
install -D -m 0755 etc/plague-server.init $RPM_BUILD_ROOT%{_initrddir}/%{name}-server
mkdir -p $RPM_BUILD_ROOT/srv/plague_builder


%clean
rm -rf $RPM_BUILD_ROOT


%post
/sbin/chkconfig --add plague-server
/sbin/service plague-server condrestart >> /dev/null || :

%preun
if [ $1 = 0 ]; then
  /sbin/service plague-server stop &> /dev/null
  /sbin/chkconfig --del plague-server
fi

%pre builder
/usr/sbin/useradd -G mock -s /sbin/nologin -M -r -d /srv/plague_builder plague-builder 2>/dev/null || :

%post builder
/sbin/chkconfig --add plague-builder
/sbin/service plague-builder condrestart >> /dev/null || :

%preun builder
if [ $1 = 0 ]; then
  /sbin/service plague-builder stop &> /dev/null
  /sbin/chkconfig --del plague-builder
fi

%files
%defattr(-, root, root)
%doc README ChangeLog
%{_bindir}/%{name}-server
%dir %{_datadir}/%{name}/server
%{_datadir}/%{name}/server/*.py*
%dir %{_sysconfdir}/%{name}/server
%config(noreplace) %{_sysconfdir}/%{name}/server/CONFIG.py*
%dir %{_sysconfdir}/%{name}/server/certs
%dir %{_sysconfdir}/%{name}/server/addl_pkg_arches
%{_sysconfdir}/%{name}/server/addl_pkg_arches/*
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}-server
%{_initrddir}/%{name}-server

%files common
%defattr(-, root, root)
/usr/lib/python?.?/site-packages/plague/*.py*

%files builder
%defattr(-, root, root)
%{_bindir}/%{name}-builder
%dir  %{_sysconfdir}/%{name}/builder
%config(noreplace) %{_sysconfdir}/%{name}/builder/CONFIG.py*
%dir  %{_sysconfdir}/%{name}/builder/certs
%config(noreplace) %{_sysconfdir}/sysconfig/%{name}-builder
%{_initrddir}/%{name}-builder
%attr(0755, plague-builder, plague-builder) /srv/plague_builder

%files client
%defattr(-, root, root)
%{_bindir}/%{name}-client

%files utils
%defattr(-, root, root)
%{_bindir}/%{name}-user-manager.py*
%{_bindir}/%{name}-certhelper.py*


%changelog
* Mon Aug 15 2005 Dan Williams <dcbw@redhat.com> 0.3.3-1
- Version 0.3.3
    o Add repo script support
    o Fix double-slashes in log URL (Ignacio Vazquez-Abrams)
    o Clear out old job info when requeueing jobs

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
- Grab python files from /usr/lib, not %{_libdir} until the
    multiarch issues get worked out

* Sun Jun 26 2005 Dan Williams <dcbw@redhat.com>
- first version/packaging
