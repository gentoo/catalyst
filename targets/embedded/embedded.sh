#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/Attic/embedded.sh,v 1.6 2004/12/16 20:01:38 wolf31o2 Exp $

case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;

	run)
		cp ${clst_sharedir}/targets/embedded/embedded-chroot.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/embedded-chroot.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/embedded-chroot.sh
	;;
	package)
		export root_fs_path="${clst_chroot_path}/tmp/mergeroot"
		install -d ${clst_image_path}
		${clst_sharedir}/targets/embedded/embedded-fs-runscript.sh ${clst_embedded_fs_type} || exit 1
	imagesize=`du -sk ${clst_image_path}/root_fs | cut -f1`
	echo "Created ${clst_embedded_fs_type} image at ${clst_image_path}/root_fs"
	echo "Image size: ${imagesize}k"
	;;
	*)
		exit 1
	;;

esac
exit 0
