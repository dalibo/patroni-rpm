#!/bin/bash -eux

# Patroni version
VERSION="1.6.5"
# DCS list, comma separated
# Values: etcd,aws,exhibitor,zookeeper,kubernetes,consul
# WARNING: consul support seems to be broken
DCS="etcd"

sudo yum install python-virtualenv gcc python-devel wget epel-release -y
sudo yum install python-pip -y
sudo pip install "setuptools<44" wheel
wget https://github.com/zalando/patroni/archive/v${VERSION}.tar.gz -O /workspace/patroni-${VERSION}.tar.gz
sudo yum-builddep -y /workspace/patroni.spec
sudo pip install psycopg2-binary

sudo rpmbuild \
	--clean \
	--define "pkgversion ${VERSION}" \
	--define "_topdir ${PWD}/tmp/rpm" \
	--define "_sourcedir ${PWD}/workspace" \
	--define "patronidcs ${DCS}" \
	-bb /workspace/patroni.spec

cp ${PWD}/tmp/rpm/RPMS/*/*.rpm ${PWD}/workspace/.
