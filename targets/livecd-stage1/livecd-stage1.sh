#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage1/Attic/livecd-stage1.sh,v 1.15 2005/01/11 14:10:19 wolf31o2 Exp $

case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;
	run)
		shift

		cp ${clst_sharedir}/targets/livecd-stage1/livecd-stage1-chroot.sh ${clst_chroot_path}/tmp
		clst_packages="$*" ${clst_CHROOT} ${clst_chroot_path} /tmp/livecd-stage1-chroot.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/livecd-stage1-chroot.sh
	;;

	preclean)
		#killall -9 gconfd-2
		#cp ${clst_sharedir}/targets/livecd-stage1/livecd-stage1-preclean-chroot.sh ${clst_chroot_path}/tmp
		#${clst_CHROOT} ${clst_chroot_path} /tmp/livecd-stage1-preclean-chroot.sh || exit 1
		#rm -f ${clst_chroot_path}/tmp/livecd-stage1-preclean-chroot.sh
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
