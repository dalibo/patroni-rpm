%global pkgname patroni
%{!?pkgrevision: %global pkgrevision 1}
%{!?patronidcs: %global patronidcs "etcd"}
%define INSTALLPATH /opt/patroni

Name:          %{pkgname}
Version:       %{pkgversion}
Release:       %{pkgrevision}%{?dist}
Summary:       A template for PostgreSQL High Availability with etcd
License:       MIT
Source0:       %{pkgname}-%{version}.tar.gz
Source1:       patroni.service
Patch0:        rpm-patroni-service.patch
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires:      python-psycopg2 >= 2.5.4, PyYAML, python-requests, python-six >= 1.7, python-prettytable >= 0.7, python-dateutil, postgresql-server
Requires(post):   %{_sbindir}/update-alternatives
Requires(postun): %{_sbindir}/update-alternatives

%description
A template for PostgreSQL High Availability with ZooKeeper, etcd, or Consul

%prep
%setup -q -n %{pkgname}-%{version}
%patch0 -p0

%build

%install
%{__install} -d %{buildroot}%{INSTALLPATH}
%{__install} -d %{buildroot}/usr/share
%{__install} -d %{buildroot}/etc/patroni
%{__install} -d %{buildroot}/etc/systemd/system
%{__install} -d %{buildroot}/lib/systemd/system

virtualenv --system-site-packages --no-wheel --no-setuptools %{buildroot}%{INSTALLPATH}
# Remove dependancies already here in base repo.
grep -vEi "psycopg2|pyyaml|requests|six|prettytable|dateutil" requirements.txt > requirements-new.txt
mv requirements-new.txt requirements.txt

%{buildroot}%{INSTALLPATH}/bin/pip install -U setuptools
%{buildroot}%{INSTALLPATH}/bin/pip install .[%{patronidcs}]
%{buildroot}%{INSTALLPATH}/bin/pip uninstall setuptools -y
%{buildroot}%{INSTALLPATH}/bin/pip uninstall pip -y

virtualenv --relocatable %{buildroot}%{INSTALLPATH}
sed -i "s#%{buildroot}##" %{buildroot}%{INSTALLPATH}/bin/activate*

cp -r extras/ %{buildroot}/usr/share/patroni
%{__install} -m 0600 postgres0.yml %{buildroot}/etc/patroni/patroni.sample.yml
%{__install} -m 0644 extras/startup-scripts/patroni.service %{buildroot}/lib/systemd/system
%{__install} -m 0644 %{SOURCE1} %{buildroot}/etc/systemd/system

%files
/opt/patroni
/usr/share/patroni
/lib/systemd/system/patroni.service
/etc/systemd/system/patroni.service
%attr(-, postgres, postgres) /etc/patroni

%post
%{_sbindir}/update-alternatives --install %{_bindir}/patroni \
    patroni %{INSTALLPATH}/bin/patroni 10
%{_sbindir}/update-alternatives --install %{_bindir}/patronictl \
    patronictl %{INSTALLPATH}/bin/patronictl 10

%postun
%{_sbindir}/update-alternatives --remove \
    patroni %{INSTALLPATH}/bin/patroni
%{_sbindir}/update-alternatives --remove \
    patronictl %{INSTALLPATH}/bin/patronictl

%changelog
* Sat Feb 02 2019 Julien Tachoires <julmon@gmail.com> - %{pkgversion}-%{pkgrevision}
- Initial release
