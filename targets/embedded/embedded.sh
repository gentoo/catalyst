#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/Attic/embedded.sh,v 1.5 2004/10/15 02:46:58 zhen Exp $

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
