#!/bin/bash

source ${clst_shdir}/support/functions.sh

case ${1} in
	build_packages)
		echo ">>> Building packages ..."
		shift
		ROOT="/" \
		clst_packages="$*" \
		exec_in_chroot \
		${clst_shdir}/${clst_target}/pkg.sh
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
		[ -n "${clst_busybox_config}" ] && \
			copy_to_chroot ${clst_busybox_config} /tmp/busy-config

		exec_in_chroot ${clst_shdir}/support/kmerge.sh

		delete_from_chroot /tmp/linuxrc
		delete_from_chroot /tmp/busy-config

		extract_modules ${clst_chroot_path} ${kname}
	;;

	image)
		# Creates the base initramfs image for the netboot
		echo -e ">>> Preparing Image ..."
		shift

		# Copy remaining files over to the initramfs target
		clst_files="${@}" \
		exec_in_chroot \
		${clst_shdir}/${clst_target}/copyfile.sh
	;;

	final)
		# For each arch, fetch the kernel images and put them in builds/
		echo -e ">>> Copying completed kernels to ${clst_target_path}/ ..."
		${clst_shdir}/support/netboot-final.sh
	;;

	clean)
		exit 0;;

	*)
		exit 1;;
esac

exit $?
