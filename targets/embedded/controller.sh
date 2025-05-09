#!/bin/bash

source ${clst_shdir}/support/functions.sh

case ${1} in
	build_packages)
		shift
		export clst_packages="$*"
		exec_in_chroot \
			${clst_shdir}/${clst_target}/chroot.sh
	;;

	preclean)
	;;

#	package)
#		export root_fs_path="${clst_chroot_path}/tmp/mergeroot"
#		install -d ${clst_image_path}

#		${clst_shdir}/embedded/fs-runscript.sh \
#			${clst_embedded_fs_type} || exit 1
#		imagesize=`du -sk ${clst_image_path}/root.img | cut -f1`
#		echo "Created ${clst_embedded_fs_type} image at \
#			${clst_image_path}/root.img"
#		echo "Image size: ${imagesize}k"
#	;;

	pre-kmerge)
		# Sets up the build environment before any kernels are compiled
		exec_in_chroot ${clst_shdir}/support/pre-kmerge.sh
	;;

	kernel)
		shift
		export kname="${1}"

		[ -n "${clst_linuxrc}" ] && \
			copy_to_chroot ${clst_linuxrc} /tmp/linuxrc
		exec_in_chroot ${clst_shdir}/support/kmerge.sh
		delete_from_chroot /tmp/linuxrc
	;;

	target_image_setup)
		shift
		${clst_shdir}/support/target_image_setup.sh ${1}

	;;
	livecd-update)
		shift
		# Now, finalize and tweak the livecd fs (inside of the chroot)
		exec_in_chroot  ${clst_shdir}/support/livecdfs-update.sh ${@}
	;;

	bootloader)
		shift
		# Here is where we poke in our identifier
		touch ${1}/livecd

		${clst_shdir}/support/iso-bootloader-setup.sh ${1}
	;;

	iso)
		shift
		${clst_shdir}/support/create-iso.sh ${@}
	;;

	clean)
	;;

	*)
	;;

esac
exit $?
