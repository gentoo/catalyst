# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/create-iso.sh,v 1.3 2005/04/29 13:32:51 rocket Exp $
. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh
#. ${clst_sharedir}/targets/${clst_target}/${clst_mainarch}-archscript.sh

#source ${clst_livecd_archscript}
## START RUNSCRIPT

if [ ! -f /usr/bin/mkisofs ]
then
	echo
	echo
	die "        /usr/bin/mkisofs is not found.  Have you merged cdrtools?"
	echo
	echo
fi

case ${clst_mainarch} in
	alpha)
		# this is for the livecd-final target, and calls the proper
		# command to build the iso file
		case ${clst_fstype} in
			zisofs)
				mkisofs -J -R -l -z -V "${clst_iso_volume_id}" -o ${1} ${clst_target_path}  || die "Cannot make ISO image"
			;;
			*)
				mkisofs -J -R -l -V "${clst_iso_volume_id}" -o ${1} ${clst_target_path} || die "Cannot make ISO image"
			;;
		esac
		isomarkboot ${1} /boot/bootlx
	;;

	arm)
		;;
	hppa)
                #this is for the livecd-stage2 target, and calls the proper command to build the iso file
	        mkisofs -J -R -l -V "${clst_iso_volume_id}" -o  ${1} ${clst_target_path}  || die "Cannot make ISO image"
	        palo -f boot/palo.conf -C ${1}

	;;
	ppc)
		# The name of the iso should be retrieved from the specs. For now, asssume GentooPPC_2004.0
		mkisofs -J -r -l -netatalk -hfs -probe -map ${clst_target_path}/boot/map.hfs -part -no-desktop -hfs-iso_volume_id \
			"${clst_iso_volume_id}" -hfs-bless ${clst_target_path}/boot -V "${clst_iso_volume_id}" -o ${1} ${clst_target_path}
	;;
	sparc)
		# this is for the livecd-final target, and calls the proper
		# command to build the iso file
		mkisofs -J -R -l -V "${clst_iso_volume_id}" -o ${1} -G ${clst_target_path}/boot/isofs.b -B ... ${clst_target_path} \
			|| die "Cannot make ISO image"

	;;
	sparc64)
		# Old silo + patched mkisofs fubar magic
		# Only silo 1.2.x seems to work for most hardware
		# Seems silo 1.3.x+ breaks on newer machines
		# when booting from CD (current as of silo 1.4.8)
		mv ${clst_target_path}/boot/mkisofs.sparc.fu /tmp 
		/tmp/mkisofs.sparc.fu -o ${1} -D -r -pad -quiet -S 'boot/cd.b' -B '/boot/second.b' \
		-s '/boot/silo.conf' -abstract 'Gentoo Linux Sparc' -copyright 'Gentoo Foundation' \
		-P 'Gentoo Linux Sparc' -p 'Gentoo Linux Sparc' -V "${clst_iso_volume_id}" \
		-A 'G entoo Linux Sparc' ${clst_target_path}  || die "Cannot make ISO image"
		rm /tmp/mkisofs.sparc.fu
															
	;;
	
	x86)
		#this is for the livecd-stage2 target, and calls the proper command
		# to build the iso file
		#
		if [ -e ${clst_target_path}/boot/isolinux.bin ]
		then
			echo "Creating ISO using ISOLINUX bootloader"
			if [ -d ${clst_target_path}/isolinux ]
			then
				rm -r ${clst_target_path}/isolinux
			fi
			mv ${clst_target_path}/boot ${clst_target_path}/isolinux
			
			case ${clst_fstype} in
				zisofs)
					mkisofs -J -R -l -V "${clst_iso_volume_id}" -o ${1} -b boot/isolinux.bin -c boot/boot.cat -no-emul-boot \
					-boot-load-size 4 -boot-info-table -z ${clst_target_path} || die "Cannot make ISO image"
				;;
				*)
					mkisofs -J -R -l -V "${clst_iso_volume_id}" -o ${1} -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot \
					-boot-load-size 4 -boot-info-table ${clst_target_path} || die "Cannot make ISO image"
				;;
			esac
		elif [ -e ${clst_target_path}/boot/grub/stage2_eltorito ]
		then
			echo "Creating ISO using GRUB bootloader"
			case ${clst_fstype} in
				zisofs)
					mkisofs -J -R -l -V "${clst_iso_volume_id}" -o ${1} -b boot/grub/stage2_eltorito -c boot/boot.cat -no-emul-boot \
					-boot-load-size 4 -boot-info-table -z ${clst_target_path} || die "Cannot make ISO image"
				;;
				*)
					mkisofs -J -R -l -V "${clst_iso_volume_id}" -o ${1} -b boot/grub/stage2_eltorito -c boot/boot.cat -no-emul-boot \
					-boot-load-size 4 -boot-info-table ${clst_target_path} || die "Cannot make ISO image"
				;;
			esac
		else	
			case ${clst_fstype} in
				zisofs)
					mkisofs -J -R -l -V "${clst_iso_volume_id}" -o ${1} \
					-z ${clst_target_path} || die "Cannot make ISO image"
				;;
				*)
					mkisofs -J -R -l -V "${clst_iso_volume_id}" -o ${1} \
					${clst_target_path} || die "Cannot make ISO image"
				;;
			esac
		fi
	;;
esac
exit  $?
