#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage4/stage4-controller.sh,v 1.1 2005/04/04 17:48:33 rocket Exp $
. ${clst_sharedir}/targets/support/functions.sh


# Only put commands in this section that you want every target to execute.
# This is a global default file and will affect every target
case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;

	build_packages)
		shift
		export clst_packages="$*"
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
	;;

	preclean)
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-preclean-chroot.sh ${clst_root_path}
	;;

	clean)
		exit 0
	;;
	
	*)
		exit 1
	;;

esac

exit 0
