#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/Attic/embedded.sh,v 1.3 2004/04/12 14:38:26 zhen Exp $

case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;

	run)
		if [ -n "${clst_ENVSCRIPT}" ]
		then
			cp "${clst_ENVSCRIPT}" ${clst_chroot_path}/tmp/envscript
		fi
	
		cp ${clst_sharedir}/targets/embedded/embedded-chroot.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/embedded-chroot.sh
		rm -f ${clst_chroot_path}/tmp/embedded-chroot.sh

		[ $? -ne 0 ] && exit 1
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
