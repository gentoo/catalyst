#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage1/Attic/livecd-stage1.sh,v 1.9 2004/04/12 14:38:26 zhen Exp $

case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;
	run)
		shift
	
		if [ -n "${clst_ENVSCRIPT}" ]
		then
			cp "${clst_ENVSCRIPT}" ${clst_chroot_path}/tmp/envscript
		fi

		cp ${clst_sharedir}/targets/livecd-stage1/livecd-stage1-chroot.sh ${clst_chroot_path}/tmp
		clst_packages="$*" ${clst_CHROOT} ${clst_chroot_path} /tmp/livecd-stage1-chroot.sh
		rm -f ${clst_chroot_path}/tmp/livecd-stage1-chroot.sh
		[ $? -ne 0 ] && exit 1
	;;

	preclean)
        cp ${clst_sharedir}/targets/livecd-stage1/livecd-stage1-preclean-chroot.sh ${clst_chroot_path}/tmp
        ${clst_CHROOT} ${clst_chroot_path} /tmp/livecd-stage1-preclean-chroot.sh
        rm -f ${clst_chroot_path}/tmp/livecd-stage1-preclean-chroot.sh

        [ $? -ne 0 ] && exit 1
    ;;

    clean)
        exit 0
    ;;

    *)
        exit 1
    ;;

esac
exit 0
