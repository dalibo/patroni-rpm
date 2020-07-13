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
Requires:      python-psycopg2 >= 2.5.4, PyYAML, python-requests, python-six >= 1.7, python-prettytable >= 0.7, python-dateutil
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
if [ $1 -eq 0 ] ; then
  %{_sbindir}/update-alternatives --remove \
      patroni %{INSTALLPATH}/bin/patroni
  %{_sbindir}/update-alternatives --remove \
      patronictl %{INSTALLPATH}/bin/patronictl
fi

%changelog
* Mon Jul 13 2020 Nicolas Thauvin <nicolas.thauvin@dalibo.com> - 1.6.5-1
- Version 1.6.5

* Wed Oct 09 2019 Julien Tachoires <julmon@gmail.com> - 1.6.0-1
- Version 1.6.0

* Mon May 06 2019 Julien Tachoires <julmon@gmail.com> - 1.5.6-1
- Version 1.5.6

* Fri Mar 01 2019 Julien Tachoires <julmon@gmail.com> - 1.5.5-4
- Include patch on callback kill when it failed

* Tue Feb 28 2019 Julien Tachoires <julmon@gmail.com> - 1.5.5-3
- Ship a decent version of setuptools
- Fix upgrade process to keep alternative scripts in /usr/bin and /bin

* Sat Feb 02 2019 Julien Tachoires <julmon@gmail.com> - 1.5.4-1
- Initial release
