#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/tinderbox/Attic/tinderbox.sh,v 1.7 2004/04/14 00:17:59 zhen Exp $

case $1 in
	run)
		shift

		cp ${clst_sharedir}/targets/tinderbox/tinderbox-chroot.sh ${clst_chroot_path}/tmp
		clst_tinderbox_packages="$*" ${clst_CHROOT} ${clst_chroot_path} /tmp/tinderbox-chroot.sh
		rm -f ${clst_chroot_path}/tmp/tinderbox-chroot.sh

		[ $? -ne 0 ] && exit 1
	;;

	preclean)
        cp ${clst_sharedir}/targets/grp/tinderbox-preclean-chroot.sh ${clst_chroot_path}/tmp
        ${clst_CHROOT} ${clst_chroot_path} /tmp/tinderbox-preclean-chroot.sh
        rm -f ${clst_chroot_path}/tmp/tinderbox-preclean-chroot.sh

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
