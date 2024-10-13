#!/bin/bash

source ${clst_shdir}/support/functions.sh

case $1 in
        run)
		# We need to install grub's EFI files and do very basic configuration
		exec_in_chroot "${clst_shdir}/support/diskimage-installation.sh" || exit 1
		;;

	pre-kmerge)
		# Sets up the build environment before any kernels are compiled
		exec_in_chroot ${clst_shdir}/support/pre-kmerge.sh
		;;

	kernel)
		shift
		export kname="$1"

		[ -n "${clst_linuxrc}" ] && \
			copy_to_chroot ${clst_linuxrc} /tmp/linuxrc
		exec_in_chroot ${clst_shdir}/support/kmerge.sh
		delete_from_chroot /tmp/linuxrc

		extract_modules ${clst_chroot_path} ${kname}
		;;

	pre-distkmerge)
		# Install dracut
		exec_in_chroot ${clst_shdir}/support/pre-distkmerge.sh
		;;
	preclean)
		;;

	diskimage-update)
		# Now, finalize and tweak the livecd fs (inside of the chroot)
		exec_in_chroot ${clst_shdir}/support/diskimagefs-update.sh
		;;

	rc-update)
		exec_in_chroot ${clst_shdir}/support/rc-update.sh
		;;
	fsscript)
		exec_in_chroot ${clst_fsscript}
		;;

	clean)
		;;

	bootloader)
		shift
		# We don't have to create any directories or copy any stuff here, since
		# the qcow2 has no internal squashfs or similar

		${clst_shdir}/support/qcow2-bootloader-setup.sh $1
		;;

	unmerge)
		[ "${clst_diskimage_depclean}" != "no" ] && exec_in_chroot ${clst_shdir}/support/depclean.sh
		shift
        	export clst_packages="$*"
		exec_in_chroot ${clst_shdir}/support/unmerge.sh
		;;
	qcow2)
		shift
		${clst_shdir}/support/create-qcow2.sh $1
		;;
esac
exit $?
