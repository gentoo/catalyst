#!/bin/bash

source ${clst_shdir}/support/functions.sh
source ${clst_shdir}/support/filesystem-functions.sh


case ${1} in
	#### Couldnt busybox step be in packages ....
	build_packages)
		shift
		clst_root_path="/" \
		clst_packages="$*" \
		exec_in_chroot \
		${clst_shdir}/${clst_target}/chroot.sh
	;;

	busybox)
		# Custom busybox config support
		if [ -f "${clst_netboot_busybox_config}" ]
		then
			mkdir -p ${clst_chroot_path}/etc/busybox/${clst_CHOST}
			cp -v ${clst_netboot_busybox_config} \
				${clst_chroot_path}/etc/busybox/${clst_CHOST}/busybox.config
			clst_use="savedconfig"
		fi

		# Main Busybox emerge
		clst_root_path="/" \
		clst_use="${clst_use} netboot make-busybox-symlinks" \
		clst_myemergeopts="${clst_myemergeopts} -O" \
		clst_packages="busybox" \
		exec_in_chroot \
		${clst_shdir}/${clst_target}/chroot.sh
	;;

	pre-kmerge)
		# Sets up the build environment before any kernels are compiled
		#exec_in_chroot ${clst_shdir}/support/pre-kmerge.sh
	;;

	post-kmerge)
		# Cleans up the build environment after the kernels are compiled
		#exec_in_chroot ${clst_shdir}/support/post-kmerge.sh
	;;

	kernel)
		shift
		export clst_kname="$1"
		export clst_root_path="/"
		#exec_in_chroot ${clst_shdir}/support/pre-kmerge.sh
		#exec_in_chroot ${clst_shdir}/support/kmerge.sh
		#exec_in_chroot ${clst_shdir}/support/post-kmerge.sh
		#extract_kernels kernels
	;;

	image)
		#Creates the base initrd image for the netboot
		shift
		# Could this step be a parameter in case there is a different
		# baselayout to add???
		clst_myemergeopts="${clst_myemergeopts} --nodeps" \
		clst_packages="netboot-base" \
		exec_in_chroot \
		${clst_shdir}/${clst_target}/chroot.sh

		clst_files="${@}" \
		exec_in_chroot \
		${clst_shdir}/${clst_target}/image.sh
	;;

	finish)
		${clst_shdir}/${clst_target}/combine.sh
	;;

	clean)
		exit 0;;

	*)
		exit 1;;
esac

exit $?
