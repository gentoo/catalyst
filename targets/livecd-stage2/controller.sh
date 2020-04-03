#!/bin/bash

source ${clst_shdir}/support/functions.sh
source ${clst_shdir}/support/filesystem-functions.sh

case $1 in
	pre-kmerge)
		# Sets up the build environment before any kernels are compiled
		exec_in_chroot ${clst_shdir}/support/pre-kmerge.sh
		;;

	post-kmerge)
		# Cleans up the build environment after the kernels are compiled
		exec_in_chroot ${clst_shdir}/support/post-kmerge.sh
		;;

	kernel)
		shift
		export clst_kname="$1"

		# if we have our own linuxrc, copy it in
		if [ -n "${clst_linuxrc}" ]
		then
			cp -pPR ${clst_linuxrc} ${clst_chroot_path}/tmp/linuxrc
		fi
		exec_in_chroot ${clst_shdir}/support/kmerge.sh
		delete_from_chroot /tmp/linuxrc

		extract_modules ${clst_chroot_path} ${clst_kname}
		#16:12 <@solar> kernel_name=foo
		#16:13 <@solar> eval clst_boot_kernel_${kernel_name}_config=bar
		#16:13 <@solar> eval echo \$clst_boot_kernel_${kernel_name}_config
		;;

	preclean)
		# Move over the motd (if applicable)
		case ${clst_livecd_type} in
			gentoo-*)
				if [ -n "${clst_livecd_motd}" ]
				then
					echo "Using livecd/motd is not supported with livecd/type"
					echo "${clst_livecd_type}. You should switch to using"
					echo "generic-livecd instead."
				fi
				cp -pPR ${clst_sharedir}/livecd/files/*.motd.txt ${clst_chroot_path}/etc
			;;
			*)
				if [ -n "${clst_livecd_motd}" ]
				then
					cp -pPR ${clst_livecd_motd} ${clst_chroot_path}/etc/motd
				fi
			;;
		esac

		# move over the environment
		cp -f ${clst_sharedir}/livecd/files/livecd-bashrc \
			${clst_chroot_path}/root/.bashrc
		cp -f ${clst_sharedir}/livecd/files/livecd-bash_profile \
			${clst_chroot_path}/root/.bash_profile
		cp -f ${clst_sharedir}/livecd/files/livecd-local.start \
			${clst_chroot_path}/etc/conf.d/local.start
		;;

	livecd-update)
		# Now, finalize and tweak the livecd fs (inside of the chroot)
		exec_in_chroot ${clst_shdir}/support/livecdfs-update.sh

		# Move over the xinitrc (if applicable)
		# This is moved here, so we can override any default xinitrc
		if [ -n "${clst_livecd_xinitrc}" ]
		then
			mkdir -p ${clst_chroot_path}/etc/X11/xinit
			cp -f ${clst_livecd_xinitrc} \
				${clst_chroot_path}/etc/X11/xinit/xinitrc
		fi
		;;

	rc-update)
		exec_in_chroot ${clst_shdir}/support/rc-update.sh
		;;

	fsscript)
		exec_in_chroot ${clst_fsscript}
		;;

	clean)
		if [ "${clst_livecd_type}" = "gentoo-release-minimal" ] \
		|| [ "${clst_livecd_type}" = "gentoo-release-universal" ]
		then
			# Clean out man, info and doc files
			rm -rf ${clst_chroot_path}/usr/share/{man,doc,info}/*
			# Zap all .pyc and .pyo files
			find ${clst_chroot_path}/usr/lib* -iname "*.py[co]" -exec rm -f {} \;
		fi
		rm -f ${clst_chroot_path}/tmp/packages.txt
		;;

	bootloader)
		shift
		# Here is where we poke in our identifier
		touch $1/livecd

		# We create a firmware directory, if necessary
		if [ -e ${clst_chroot_path}/lib/firmware.tar.bz2 ]
		then
			echo "Creating firmware directory in $1"
			mkdir -p $1/firmware
			# TODO: Unpack firmware into $1/firmware and remove it from the
			# chroot so newer livecd-tools/genkernel can find it and unpack it.
		fi

		# Move over the readme (if applicable)
		if [ -n "${clst_livecd_readme}" ]
		then
			cp -f ${clst_livecd_readme} $1/README.txt
		else
			cp -f ${clst_sharedir}/livecd/files/README.txt $1
		fi

		case ${clst_livecd_type} in
			gentoo-release-livecd)
				mkdir -p $1/snapshots
				if [ -n "${clst_livecd_overlay}" ]
				then
					if [ -e ${clst_livecd_overlay}/snapshots/${clst_snapshot_path} ]
					then
						echo "ERROR: You have a snapshot in your overlay, please"
						echo "remove it, since catalyst adds it automatically."
						exit 1
					fi
				fi
				cp -f ${clst_snapshot_path}{,.DIGESTS} $1/snapshots
			;;
			gentoo-release-livedvd)
				targets="distfiles snapshots stages"
				for i in ${targets}
				do
					mkdir -p $1/$i
					if [ -n "${clst_livecd_overlay}" ]
					then
						if [ -e ${clst_livecd_overlay}/$i ] && \
						[ -n "$(ls ${clst_livecd_overlay}/$i |grep -v README)" ]
						then
							echo "ERROR: You have files in $i in your overlay!"
							echo "This directory is now populated by catalyst."
							exit 1
						fi
					fi
					case ${target} in
						distfiles)
							### TODO: make this fetch the distfiles
							continue
						;;
						snapshots)
							cp -f ${clst_snapshot_path}{,.DIGESTS} $1/snapshots
						;;
						stages)
							### TODO: make this copy stages
							continue
						;;
					esac
				done
			;;
		esac

		${clst_shdir}/support/bootloader-setup.sh $1
		;;

	unmerge)
		[ "${clst_livecd_depclean}" != "no" ] && exec_in_chroot ${clst_shdir}/support/depclean.sh
		shift
        	export clst_packages="$*"
		exec_in_chroot ${clst_shdir}/support/unmerge.sh
	;;

	target_image_setup)
		shift
		${clst_shdir}/support/target_image_setup.sh $1
		;;

	iso)
		shift
		${clst_shdir}/support/create-iso.sh $1
		;;
esac
exit $?
