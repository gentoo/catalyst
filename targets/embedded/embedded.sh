#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/Attic/embedded.sh,v 1.7 2005/01/10 01:16:07 zhen Exp $

case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;

	run)
		cp ${clst_sharedir}/targets/embedded/embedded-chroot.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/embedded-chroot.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/embedded-chroot.sh
	;;

	preclean)
		# currently this doesn't do much
		cp ${clst_sharedir}/targets/embedded/embedded-preclean-chroot.sh ${clst_chroot_path}
		${clst_CHROOT} ${clst_chroot_path} /tmp/embedded-preclean-chroot.sh || exit 1
		rm -rf ${clst_chroot_path}/tmp/embedded-preclean-chroot.sh
	;;
	package)
		export root_fs_path="${clst_chroot_path}/tmp/mergeroot"
		install -d ${clst_image_path}
		${clst_sharedir}/targets/embedded/embedded-fs-runscript.sh ${clst_embedded_fs_type} || exit 1
	imagesize=`du -sk ${clst_image_path}/root_fs | cut -f1`
	echo "Created ${clst_embedded_fs_type} image at ${clst_image_path}/root_fs"
	echo "Image size: ${imagesize}k"
	;;

	# almost the same code as livecd-stage2
	kernel)
		shift
		numkernels="$1"
		cp -a ${clst_sharedir}/livecd/runscript-support/pre-kmerge.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/pre-kmerge.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/pre-kmerge.sh
		cp -a ${clst_sharedir}/targets/embedded/kmerge.sh ${clst_chroot_path}/tmp
		count=0
		while [ ${count} -lt ${numkernels} ]
		do
			sleep 30
		
			shift
			export clst_kname="$1"
			shift
			export clst_ksource="$1"
			shift
			export clst_kextversion="$1"
			shift
			export clst_gk_action="$1"
			echo "exporting clst_gk_action as:${1}" 
			shift
			${clst_CHROOT} ${clst_chroot_path} /tmp/kmerge.sh || exit 1
			count=$(( ${count} + 1 ))
		done
		rm -f ${clst_chroot_path}/tmp/pre-kmerge.sh
		cp -a ${clst_sharedir}/livecd/runscript-support/post-kmerge.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/post-kmerge.sh || exit 1
		;;
	*)
		exit 1
	;;

esac
exit 0
