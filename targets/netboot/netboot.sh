#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/Attic/netboot.sh,v 1.5 2004/10/12 18:01:22 zhen Exp $

export GK_BINARIES=/var/tmp/gk_binaries
export IMAGE_PATH=/tmp/image

if [ -n "${clst_CCACHE}" ]
then
	export clst_myfeatures="${clst_myfeatures} ccache"
fi
if [ -n "${clst_DISTCC}" ]
then   
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"
fi
if [ -n "${clst_PKGCACHE}" ]
then
	export clst_myemergeopts="${clst_myemergeopts} --usepkg --buildpkg --newuse"
fi

scriptdir=${clst_sharedir}/targets/netboot

cmd=$1
shift
case ${cmd} in

	setup)
		cp ${scriptdir}/netboot-setup.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/netboot-setup.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/netboot-setup.sh
	;;
	
	packages)
		cp ${scriptdir}/netboot-packages.sh ${clst_chroot_path}/tmp
		clst_packages="$*" ${clst_CHROOT} ${clst_chroot_path} /tmp/netboot-packages.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/netboot-packages.sh
	;;

	busybox)
		# Custom busybox config support
		if [ ! -z "${1}" ]
		then
			mkdir -p ${clst_chroot_path}/etc/busybox/${clst_CHOST}
			cp ${1} ${clst_chroot_path}/etc/busybox/${clst_CHOST}/busybox.config
		fi
	
		cp ${scriptdir}/netboot-busybox.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/netboot-busybox.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/netboot-busybox.sh
	;;

	kernel)
		KERNEL_TYPE=${1}
		SOURCES=${2}
		CONFIG=${3}
		if [ "${KERNEL_TYPE}" == "kernel-sources" ]
		then
			cp ${scriptdir}/netboot-kernel.sh ${clst_chroot_path}/tmp
			cp ${CONFIG} ${clst_chroot_path}/var/tmp/kernel.config || die
			env SOURCES=${SOURCES} CONFIG=/var/tmp/kernel.config \
				${clst_CHROOT} ${clst_chroot_path} /tmp/netboot-kernel.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/netboot-kernel.sh
		else
			cp ${clst_netboot_kernel_prebuilt} ${clst_chroot_path}/kernel
		fi
	;;

	image)
		cp ${scriptdir}/netboot-image.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/netboot-image.sh "$@" || exit 1
		rm -f ${clst_chroot_path}/tmp/netboot-image.sh
	;;

	finish)
		cp ${scriptdir}/netboot-combine.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/netboot-combine.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/netboot-combine.sh

		mkdir -p ${clst_target_path}
		cp \
			${clst_chroot_path}/{initrd.gz,kernel,netboot.$clst_mainarch} \
			${clst_target_path} || exit 1
	;;

	clean)
		exit 0;;
	*)
		exit 1;;
esac

exit 0
