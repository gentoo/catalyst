#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/Attic/netboot.sh,v 1.1 2004/10/06 01:34:29 zhen Exp $

export GK_BINARIES=/usr/portage/packages/gk_binaries
export IMAGE_PATH=/image

# Force usage of -Os for smaller size
export CFLAGS="-Os -pipe"
export CXXFLAGS="-Os -pipe"

case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;
	packages)
		shift
	
		cp ${clst_sharedir}/targets/netboot/netboot-packages.sh ${clst_chroot_path}/tmp
		clst_packages="$*" ${clst_CHROOT} ${clst_chroot_path} /tmp/netboot-packages.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/netboot-packages.sh
	;;
	busybox)
		shift
	
		cp ${clst_sharedir}/targets/netboot/netboot-busybox.sh ${clst_chroot_path}/tmp
		mkdir -p ${clst_chroot_path}/etc/busybox/${clst_CHOST}/
		# Seems busybox doesn't have a CCHOST set when emerging
		CCHOST=
		cp ${1} ${clst_chroot_path}/etc/busybox/${CCHOST}/busybox.config
		${clst_CHROOT} ${clst_chroot_path} /tmp/netboot-busybox.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/netboot-busybox.sh
	;;

	kernel)
		shift
		SOURCES=${1}
		shift
		CONFIG=${1}
		shift
		
		cp ${clst_sharedir}/targets/netboot/netboot-kernel.sh ${clst_chroot_path}/tmp
		cp ${CONFIG} ${clst_chroot_path}/var/tmp/kernel.config
		${clst_CHROOT} ${clst_chroot_path} /tmp/netboot-kernel.sh ${SOURCES} ${clst_netboot_kernel_use} || exit 1
		rm -f ${clst_chroot_path}/tmp/netboot-kernel.sh
	;;

	image)
		shift
		TARBALL=${1}
		shift

		cp ${clst_sharedir}/targets/netboot/netboot-image.sh ${clst_chroot_path}/tmp
		cp ${TARBALL} ${clst_chroot_path}/netboot-base.tar.bz2
		${clst_CHROOT} ${clst_chroot_path} /tmp/netboot-image.sh ${IMAGE_PATH} /netboot-base.tar.bz2 ${@} || exit 1
		rm -f ${clst_chroot_path}/tmp/netboot-image.sh
		exit 0

	;;
	finish)
		[ ! -e ${clst_target_path} ] && mkdir -p ${clst_target_path}
		cp ${clst_chroot_path}/ramdisk ${clst_chroot_path}/kernel ${clst_target_path}
		strip ${clst_target_path}/kernel > /dev/null 2>&1
		gzip -9f ${clst_target_path}/ramdisk
		exit 0
	;;

	clean)
		exit 0
	;;

	*)
		exit 1
	;;

esac
exit 0
