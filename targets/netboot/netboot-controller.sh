#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/netboot-controller.sh,v 1.3 2005/07/05 21:53:41 wolf31o2 Exp $
. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh


case ${1} in

	#### Couldnt busybox step be in packages ....

	build_packages)
		shift
		clst_root_path="/" \
		clst_packages="$*" \
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
	;;

	busybox)
		# Custom busybox config support
		if [ -f "${clst_netboot_busybox_config}" ]
		then
			mkdir -p ${clst_chroot_path}/etc/busybox/${clst_CHOST}
			cp -v ${clst_netboot_busybox_config} ${clst_chroot_path}/etc/busybox/${clst_CHOST}/busybox.config
			clst_netboot_use="savedconfig" 
		fi
		
		# Main Busybox emerge
		clst_root_path="/" \
		clst_netboot_use="${clst_netboot_use} netboot" \
		clst_myemergeopts="${clst_myemergeopts} -O" \
		clst_packages="busybox" \
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
	;;

	kernel)
		shift
                export clst_kname="$1"
		export clst_root_path="/"
                #exec_in_chroot ${clst_sharedir}/targets/support/pre-kmerge.sh
                #exec_in_chroot ${clst_sharedir}/targets/support/kmerge.sh
                #exec_in_chroot ${clst_sharedir}/targets/support/post-kmerge.sh
		#extract_kernels kernels
		
	;;

	image)
		#Creates the base initrd image for the netboot

		shift

		# Could this step be a parameter in case there is a different baselayout to add???
		clst_myemergeopts="${clst_myemergeopts} --nodeps" \
		clst_packages="netboot-base" \
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-chroot.sh
		
		clst_files="${@}" \
		exec_in_chroot ${clst_sharedir}/targets/${clst_target}/${clst_target}-image.sh
	;;

	finish)
	

		
		${clst_sharedir}/targets/${clst_target}/${clst_target}-combine.sh
	;;

	clean)
		exit 0;;
	*)
		exit 1;;
esac

exit $?
