#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/Attic/stage3.sh,v 1.16 2004/10/15 02:46:58 zhen Exp $

case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;

	run)
		cp ${clst_sharedir}/targets/stage3/stage3-chroot.sh ${clst_chroot_path}/tmp	
		${clst_CHROOT} ${clst_chroot_path} /tmp/stage3-chroot.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/stage3-chroot.sh
	;;

	preclean)
		cp ${clst_sharedir}/targets/stage3/stage3-preclean-chroot.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/stage3-preclean-chroot.sh || exit 1
		rm -rf ${clst_chroot_path}/tmp/stage3-preclean-chroot.sh
	;;

	clean)
		exit 0
	;;
	
	*)
		exit 1
	;;

esac
exit 0
