#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/Attic/grp.sh,v 1.18 2004/10/15 02:46:58 zhen Exp $

case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;
	run)
		shift
		export clst_grp_type=$1
		shift
		export clst_grp_target=$1
		shift
				
		cp ${clst_sharedir}/targets/grp/grp-chroot.sh ${clst_chroot_path}/tmp
		clst_grp_packages="$*" ${clst_CHROOT} ${clst_chroot_path} /tmp/grp-chroot.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/grp-chroot.sh
	;;

	preclean)
		#cp ${clst_sharedir}/targets/grp/grp-preclean-chroot.sh ${clst_chroot_path}/tmp
		#${clst_CHROOT} ${clst_chroot_path} /tmp/grp-preclean-chroot.sh || exit 1
		#rm -f ${clst_chroot_path}/tmp/grp-preclean-chroot.sh
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
