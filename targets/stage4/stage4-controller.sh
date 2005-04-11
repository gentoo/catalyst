#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage4/stage4-controller.sh,v 1.2 2005/04/11 20:05:40 rocket Exp $
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
		exec_in_chroot ${clst_sharedir}/targets/support/pre-kmerge.sh
		exec_in_chroot ${clst_sharedir}/targets/support/kmerge.sh
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


	clean)
		exit 0
	;;
	
	*)
		exit 1
	;;

esac

exit 0
