# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage2/livecd-stage2-controller.sh,v 1.3 2005/04/06 23:23:57 rocket Exp $
. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh

case $1 in
	kernel)
		shift
		export clst_kname="$1"
		

		exec_in_chroot ${clst_sharedir}/targets/support/pre-kmerge.sh
		exec_in_chroot ${clst_sharedir}/targets/support/kmerge.sh
		exec_in_chroot ${clst_sharedir}/targets/support/post-kmerge.sh

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
				${clst_sharedir}/livecd/files/environmental.motd.txt \
				${clst_sharedir}/livecd/files/gamecd.motd.txt \
				${clst_chroot_path}/etc
		fi
	
		# move over the xinitrc (if applicable)
		if [ -n "${clst_livecd_xinitrc}" ]
		then
			cp -a ${clst_livecd_xinitrc} ${clst_chroot_path}/etc/X11/xinit/xinitrc
		fi

		# move over the environment
		cp ${clst_sharedir}/livecd/files/livecd-bash_profile \
			${clst_chroot_path}/root/.bash_profile
		touch ${clst_chroot_path}/root/.bashrc
		cp ${clst_sharedir}/livecd/files/livecd-local.start \
			${clst_chroot_path}/etc/conf.d/local.start
		cp ${clst_sharedir}/livecd/files/mkvardb \
			${clst_chroot_path}/tmp
		mkdir -p /usr/share/faces
		cp ${clst_sharedir}/livecd/files/gentoo.png \
			${clst_chroot_path}/usr/share/faces
		
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

		# now, finalize and tweak the livecd fs (inside of the chroot)
		exec_in_chroot  ${clst_sharedir}/targets/support/livecdfs-update.sh

		# if the user has their own fs update script, execute it
		if [ -n "${clst_livecd_fsscript}" ]
		then
			exec_in_chroot ${clst_livecd_fsscript}
		fi
		;;

	clean)
		find ${clst_chroot_path}/usr/lib -iname "*.pyc" -exec rm -f {} \;
		;;

	bootloader)
		# Here is where we poke in our identifier
		touch ${clst_target_path}/livecd
		
		${clst_sharedir}/targets/livecd-stage2/livecd-stage2-bootloader.sh
		;;

	cdfs)
		${clst_sharedir}/targets/livecd-stage2/livecd-stage2-cdfs.sh
		;;

	iso)
		shift
		${clst_sharedir}/targets/livecd-stage2/livecd-stage2-iso.sh $1
		;;
esac
exit 0 
