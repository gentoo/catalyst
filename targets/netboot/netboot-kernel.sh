#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/Attic/netboot-kernel.sh,v 1.1 2004/10/06 01:34:29 zhen Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

if [ -n "${clst_DISTCC}" ]
then   
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gnome -gtk" emerge --oneshot --nodeps -b -k distcc || exit 1
fi

if [ -n "${clst_PKGCACHE}" ]
then
	clst_emergeopts="--usepkg --buildpkg"
else
	clst_emergeopts=""
fi

KERNEL_SOURCES=$1
shift

## setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"

## START BUILD
export USE_ORDER="env:conf:defaults"	

emerge ${clst_emergeopts} genkernel || exit 1

# Fix dumb genkernel bug (#64514) (remove this when genkernel 3.0.2g goes stable)
sed -e "/BUILD_INITRD/{s/&&/& (/
s/$/ )/ }" -i /usr/share/genkernel/gen_package.sh

USE="${@}" emerge ${KERNEL_SOURCES} || exit 1

mkdir -p ${GK_BINARIES}

genkernel --kerneldir=/usr/src/linux --kernel-config=/var/tmp/kernel.config \
		--minkernpackage=${GK_BINARIES}/kernel.tar.bz2 \
		kernel || exit 1
