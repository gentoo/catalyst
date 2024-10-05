#!/bin/bash

source ${clst_shdir}/support/functions.sh

case $1 in
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
		exec_in_chroot ${clst_shdir}/support/livecdfs-update.sh
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

		# We create a firmware directory, if necessary
		if [ -e ${clst_chroot_path}/lib/firmware.tar.bz2 ]
		then
			echo "Creating firmware directory in $1"
			mkdir -p $1/firmware
			# TODO: Unpack firmware into $1/firmware and remove it from the
			# chroot so newer livecd-tools/genkernel can find it and unpack it.
		fi

		if [ -e ${clst_chroot_path}/boot/memtest86plus/ ]; then
			cp -rv ${clst_chroot_path}/boot/memtest86plus/* $1
		fi

		${clst_shdir}/support/iso-bootloader-setup.sh $1
		;;

	unmerge)
		[ "${clst_diskimage_depclean}" != "no" ] && exec_in_chroot ${clst_shdir}/support/depclean.sh
		shift
        	export clst_packages="$*"
		exec_in_chroot ${clst_shdir}/support/unmerge.sh
	;;

	target_image_setup)
		shift
		${clst_shdir}/support/target_image_setup.sh $1
		;;

	qcow2)
		shift
		${clst_shdir}/support/create-qcow2.sh $1
		;;
esac
exit $?
