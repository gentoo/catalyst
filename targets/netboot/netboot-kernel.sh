#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/Attic/netboot-kernel.sh,v 1.4 2004/10/22 04:23:16 wolf31o2 Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

# setup our environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"
export USE_ORDER="env:conf:defaults"	

mkdir -p ${GK_BINARIES}
BUILD_KERNEL=1

if [ -n "${clst_KERNCACHE}" ]
then
	GK_PKGDIR="$(portageq envvar PKGDIR)/All/genkernel"
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
	# Fix dumb genkernel bug (#64514)
	sed -e "/BUILD_INITRD/{s/&&/& (/
	s/$/ )/ }" -i /usr/share/genkernel/gen_package.sh

	# Build the kernel !
	emerge ${clst_myemergeopts} ${SOURCES} || exit 1

	genkernel \
		--no-mountboot \
		--kerneldir=/usr/src/linux \
		--kernel-config=${CONFIG} \
		--module-prefix=${GK_BINARIES} \
		--minkernpackage=${GK_BINARIES}/kernel.tar.bz2 \
		kernel || exit 1

	find ${GK_BINARIES}/lib \
		-name '*.o' -o -name '*.ko' \
		-exec strip -R .comment -R .note {} \; \
		|| exit 1 
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
fi

cp ${GK_BINARIES}/kernel / || exit 1
