# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage2/livecd-stage2-controller.sh,v 1.15 2005/11/14 19:20:30 wolf31o2 Exp $
. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh

case $1 in
	pre-kmerge)
		# Sets up the build environment before any kernels are compiled
		exec_in_chroot ${clst_sharedir}/targets/support/pre-kmerge.sh
		;;
	post-kmerge)
		# Cleans up the build environment after the kernels are compiled
		exec_in_chroot ${clst_sharedir}/targets/support/post-kmerge.sh
		;;
	kernel)
		shift
		export clst_kname="$1"

		# if we have our own linuxrc, copy it in
		if [ -n "${clst_linuxrc}" ]
		then
			cp -a ${clst_linuxrc} ${clst_chroot_path}/tmp/linuxrc
		fi
		exec_in_chroot ${clst_sharedir}/targets/support/kmerge.sh
		delete_from_chroot tmp/linuxrc

		extract_modules ${clst_chroot_path} ${clst_kname}
		#16:12 <@solar> kernel_name=foo
		#16:13 <@solar> eval clst_boot_kernel_${kernel_name}_config=bar
		#16:13 <@solar> eval echo \$clst_boot_kernel_${kernel_name}_config
		;;

	preclean)
		# move over the motd (if applicable)
		if [ -n "${clst_livecd_motd}" ]
		then
			cp -a ${clst_livecd_motd} ${clst_chroot_path}/etc/motd
		else
			cp -a ${clst_sharedir}/livecd/files/generic.motd.txt \
				${clst_sharedir}/livecd/files/universal.motd.txt \
				${clst_sharedir}/livecd/files/minimal.motd.txt \
				${clst_sharedir}/livecd/files/livecd.motd.txt \
				${clst_sharedir}/livecd/files/gamecd.motd.txt \
				${clst_chroot_path}/etc
		fi
	
		# move over the environment
		cp ${clst_sharedir}/livecd/files/livecd-bashrc \
			${clst_chroot_path}/root/.bashrc
		cp ${clst_sharedir}/livecd/files/livecd-bash_profile \
			${clst_chroot_path}/root/.bash_profile
		cp ${clst_sharedir}/livecd/files/livecd-local.start \
			${clst_chroot_path}/etc/conf.d/local.start
		
		# execute copy gamecd.conf if we're a gamecd
		if [ "${clst_livecd_type}" = "gentoo-gamecd" ]
		then
		    if [ -n "${clst_gamecd_conf}" ]
		    then
			cp ${clst_gamecd_conf} ${clst_chroot_path}/tmp/gamecd.conf
		    else
			echo "gamecd/conf is required for a gamecd!"
			exit 1
		    fi
		fi
		;;
	livecd-update)
		# now, finalize and tweak the livecd fs (inside of the chroot)
		exec_in_chroot  ${clst_sharedir}/targets/support/livecdfs-update.sh
		
		
		# move over the xinitrc (if applicable)
		# this is moved here, so we can override any default xinitrc
		if [ -n "${clst_livecd_xinitrc}" ]
		then
			cp -f ${clst_livecd_xinitrc} ${clst_chroot_path}/etc/X11/xinit/xinitrc
		fi
		;;
	rc-update)
		exec_in_chroot  ${clst_sharedir}/targets/support/rc-update.sh
		;;
	fsscript)
		exec_in_chroot ${clst_fsscript}
		;;

	clean)
		find ${clst_chroot_path}/usr/lib -iname "*.pyc" -exec rm -f {} \;
		;;

	bootloader)
		shift
		# Here is where we poke in our identifier
		touch $1/livecd
		
		# move over the readme (if applicable)
		if [ -n "${clst_livecd_readme}" ]
		then
			cp -f ${clst_livecd_readme} $1/README.txt
		else
			cp -f ${clst_sharedir}/livecd/files/README.txt $1
		fi

		# move over Getting_Online.txt for minimal/GameCD
		if [ "${clst_livecd_type}" = "gentoo-gamecd" ] \
		|| [ "${clst_livecd_type}" = "gentoo-release-minimal" ] \
		|| [ "${clst_livecd_type}" = "gentoo-release-livecd" ]
		then
			cp -f ${clst_sharedir}/livecd/files/Getting_Online.txt $1
		fi
		
		${clst_sharedir}/targets/support/bootloader-setup.sh $1
		;;

	target_image_setup)
		shift
		${clst_sharedir}/targets/support/target_image_setup.sh $1
		;;

	iso)
		shift
		${clst_sharedir}/targets/support/create-iso.sh $1
		;;
esac
exit $?
