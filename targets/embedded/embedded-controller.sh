#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/embedded-controller.sh,v 1.3 2005/04/27 17:44:58 rocket Exp $

. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh
case $1 in
	enter)
	;;

	build_packages)
		shift
		export clst_packages="$*"
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
	;;

	preclean)
	;;

#	package)
#		export root_fs_path="${clst_chroot_path}/tmp/mergeroot"
#		install -d ${clst_image_path}
		
#		${clst_sharedir}/targets/embedded/embedded-fs-runscript.sh ${clst_embedded_fs_type} || exit 1
#		imagesize=`du -sk ${clst_image_path}/root.img | cut -f1`
#		echo "Created ${clst_embedded_fs_type} image at ${clst_image_path}/root.img"
#		echo "Image size: ${imagesize}k"
	
#	;;

	kernel)
		shift
		export clst_kname="$1"
		exec_in_chroot ${clst_sharedir}/targets/support/pre-kmerge.sh
		exec_in_chroot ${clst_sharedir}/targets/support/kmerge.sh
		exec_in_chroot ${clst_sharedir}/targets/support/post-kmerge.sh
	
	;;

	target_image_setup)
		shift
		${clst_sharedir}/targets/support/target_image_setup.sh $1

	;;
        livecd-update)
	        # now, finalize and tweak the livecd fs (inside of the chroot)
		exec_in_chroot  ${clst_sharedir}/targets/support/livecdfs-update.sh
	;;

	bootloader)
		shift
		# Here is where we poke in our identifier
		touch $1/livecd

		${clst_sharedir}/targets/support/bootloader-setup.sh $1
	;;
	
	iso)
		shift
		${clst_sharedir}/targets/support/create-iso.sh $1
	;;


	clean)
	;;

	*)
	;;

esac
exit $?
