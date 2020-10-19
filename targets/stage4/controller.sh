#!/bin/bash

source ${clst_shdir}/support/functions.sh

# Only put commands in this section that you want every target to execute.
# This is a global default file and will affect every target
case $1 in
	enter)
		${clst_CHROOT} ${clst_chroot_path}
	;;

	pre-kmerge)
		# Sets up the build environment before any kernels are compiled
		exec_in_chroot ${clst_shdir}/support/pre-kmerge.sh
	;;

	kernel)
		shift
		export kname="$1"

		# If we have our own linuxrc, copy it in
		[ -n "${clst_linuxrc}" ] && \
			copy_to_chroot ${clst_linuxrc} /tmp/linuxrc
		exec_in_chroot ${clst_shdir}/support/kmerge.sh
		delete_from_chroot /tmp/linuxrc

		extract_modules ${clst_chroot_path} ${kname}
	;;

	build_packages)
		shift
		export clst_packages="$*"
		exec_in_chroot ${clst_shdir}/${clst_target}/chroot.sh
	;;

	preclean)
		exec_in_chroot ${clst_shdir}/${clst_target}/preclean-chroot.sh
	;;

	rc-update)
		exec_in_chroot ${clst_shdir}/support/rc-update.sh
	;;

	fsscript)
		exec_in_chroot ${clst_fsscript}
	;;

	livecd-update)
		# Now, finalize and tweak the livecd fs (inside of the chroot)
		exec_in_chroot ${clst_shdir}/support/livecdfs-update.sh

		# Move over the xinitrc (if applicable)
		# This is moved here, so we can override any default xinitrc
		if [ -n "${clst_livecd_xinitrc}" ]
		then
			cp -f ${clst_livecd_xinitrc} \
				${clst_chroot_path}/etc/X11/xinit/xinitrc
		fi
	;;

	bootloader)
		exit 0
	;;

	target_image_setup)
		shift
		${clst_shdir}/support/target_image_setup.sh $1
	;;

	unmerge)
		shift
		export clst_packages="$*"
		exec_in_chroot ${clst_shdir}/support/unmerge.sh
	;;

	iso)
		shift
		${clst_shdir}/support/create-iso.sh $1
	;;

	clean)
		exit 0
	;;

	*)
		exit 1
	;;
esac
exit $?
