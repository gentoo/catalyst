#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/tinderbox/Attic/tinderbox.sh,v 1.10 2004/10/15 02:46:58 zhen Exp $

case $1 in
	run)
		shift

		cp ${clst_sharedir}/targets/tinderbox/tinderbox-chroot.sh ${clst_chroot_path}/tmp
		clst_tinderbox_packages="$*" ${clst_CHROOT} ${clst_chroot_path} /tmp/tinderbox-chroot.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/tinderbox-chroot.sh
	;;

	preclean)
        #cp ${clst_sharedir}/targets/grp/tinderbox-preclean-chroot.sh ${clst_chroot_path}/tmp
        #${clst_CHROOT} ${clst_chroot_path} /tmp/tinderbox-preclean-chroot.sh || exit 1
        #rm -f ${clst_chroot_path}/tmp/tinderbox-preclean-chroot.sh
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
