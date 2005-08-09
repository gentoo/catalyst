#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage4/stage4-controller.sh,v 1.8 2005/08/09 19:02:31 rocket Exp $
. ${clst_sharedir}/targets/support/functions.sh


# Only put commands in this section that you want every target to execute.
# This is a global default file and will affect every target
case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;
	kernel)
		shift
		export clst_kname="$1"
		# if we have our own linuxrc, copy it in
		if [ -n "${clst_linuxrc}" ]
		then
			cp -a ${clst_linuxrc} ${clst_chroot_path}/tmp/linuxrc
		fi
		exec_in_chroot ${clst_sharedir}/targets/support/pre-kmerge.sh
		exec_in_chroot ${clst_sharedir}/targets/support/kmerge.sh
		delete_from_chroot tmp/linuxrc
		exec_in_chroot ${clst_sharedir}/targets/support/post-kmerge.sh
		extract_modules ${clst_chroot_path} ${clst_kname}
		extract_kernel ${clst_chroot_path}/boot ${clst_kname}
	;;
	build_packages)
		shift
		export clst_packages="$*"
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
	;;

	preclean)
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-preclean-chroot.sh ${clst_root_path}
	;;
	
	rc-update)
		exec_in_chroot  ${clst_sharedir}/targets/support/rc-update.sh
	;;
	
	fsscript)
		exec_in_chroot ${clst_fsscript}
	;;

	livecd-update)
		# now, finalize and tweak the livecd fs (inside of the chroot)
		exec_in_chroot  ${clst_sharedir}/targets/support/livecdfs-update.sh
	;;

        bootloader)
		exit 0
	;;
	
	target_image_setup)
		shift
		#${clst_sharedir}/targets/livecd-stage2/livecd-stage2-cdfs.sh
		${clst_sharedir}/targets/support/target_image_setup.sh $1
	;;

	iso)
	
		shift
		${clst_sharedir}/targets/support/create-iso.sh $1
	;;

	clean)
		exit 0
	;;
	
	*)
		exit 1
	;;

esac

exit $?
