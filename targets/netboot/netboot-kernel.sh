#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/Attic/netboot-kernel.sh,v 1.6 2005/01/26 21:59:40 wolf31o2 Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

# setup our environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"
export USE_ORDER="env:pkg:conf:defaults"	

mkdir -p ${GK_BINARIES}
BUILD_KERNEL=1
CONFIG_MD5_EQUAL=0

GK_PKGDIR="$(portageq envvar PKGDIR)/All/genkernel"

if [ -e "${GK_PKGDIR}/config-md5" -a "`md5sum ${CONFIG}`" = "$(< ${GK_PKGDIR}/config-md5)" ]
then
	CONFIG_MD5_EQUAL=1
	echo "Using the cached kernel since your .config didn't changed."
fi

if [ -n "${clst_KERNCACHE}" -a ${CONFIG_MD5_EQUAL} -eq 1 ] 
then
	mkdir -p ${GK_PKGDIR}
	if [ -f ${GK_PKGDIR}/kernel ] && [ -d ${GK_PKGDIR}/lib ]
	then
		cp -r ${GK_PKGDIR}/lib ${GK_BINARIES}/ || exit 1
		cp ${GK_PKGDIR}/kernel ${GK_BINARIES}/ || exit 1
		BUILD_KERNEL=0
	fi
fi

if [ ${BUILD_KERNEL} -eq 1 ]
then
	# setup genkernel
	emerge ${clst_myemergeopts} genkernel || exit 1

	# Build the kernel !
	emerge ${clst_myemergeopts} ${SOURCES} || exit 1

	genkernel \
		--no-mountboot \
		--kerneldir=/usr/src/linux \
		--kernel-config=${CONFIG} \
		--module-prefix=${GK_BINARIES} \
		--minkernpackage=${GK_BINARIES}/kernel.tar.bz2 \
		kernel || exit 1

	# DO NOT STRIP MODULES !!! It makes them unloadable !


	kernname="$(tar -tjf ${GK_BINARIES}/kernel.tar.bz2)"
	tar -jxf ${GK_BINARIES}/kernel.tar.bz2 -C ${GK_BINARIES}
	mv ${GK_BINARIES}/{${kernname},kernel} || exit 1 

	if [ -n "${clst_KERNCACHE}" ]
	then
		case ${clst_mainarch} in
			alpha|arm|sparc);;
			*)
				cp -r ${GK_BINARIES}/lib ${GK_PKGDIR}/ || exit 1
				cp ${GK_BINARIES}/kernel ${GK_PKGDIR}/ || exit 1
				;;
		esac
	fi

	md5sum "${CONFIG}" > "${GK_PKGDIR}/config-md5"
fi

cp ${GK_BINARIES}/kernel / || exit 1
