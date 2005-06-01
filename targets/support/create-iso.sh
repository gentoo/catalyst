# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/create-iso.sh,v 1.4 2005/06/01 13:41:12 wolf31o2 Exp $
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

# If not volume ID is set, make up a sensible default
if [ -z "${clst_iso_volume_id}" ]
then
	case ${clst_livecd_type} in
		gentoo-*)
			case ${clst_mainarch} in
				alpha)
					clst_iso_volume_id="Gentoo Linux - Alpha"
				;;
				amd64)
					clst_iso_volume_id="Gentoo Linux - AMD64"
				;;
				arm)
					clst_iso_volume_id="Gentoo Linux - ARM"
				;;
				hppa)
					clst_iso_volume_id="Gentoo Linux - HPPA"
				;;
				ia64)
					clst_iso_volume_id="Gentoo Linux - IA64"
				;;
				m68k)
					clst_iso_volume_id="Gentoo Linux - M68K"
				;;
				mips)
					clst_iso_volume_id="Gentoo Linux - MIPS"
				;;
				ppc)
					clst_iso_volume_id="Gentoo Linux - PPC"
				;;
				ppc64)
					clst_iso_volume_id="Gentoo Linux - PPC64"
				;;
				s390)
					clst_iso_volume_id="Gentoo Linux - S390"
				;;
				sh)
					clst_iso_volume_id="Gentoo Linux - SH"
				;;
				sparc)
					clst_iso_volume_id="Gentoo Linux - SPARC"
				;;
				x86)
					clst_iso_volume_id="Gentoo Linux - X86"
				;;
			esac
		*)
			clst_iso_volume_id="Catalyst LiveCD"
		;;
	esac
fi

# Here we actually create the ISO images for each architecture
case ${clst_mainarch} in
	alpha)
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
		mkisofs -J -R -l -V "${clst_iso_volume_id}" -o  ${1} ${clst_target_path}  || die "Cannot make ISO image"
		palo -f boot/palo.conf -C ${1}
	;;
	ppc*)
		mkisofs -J -r -l -netatalk -hfs -probe -map ${clst_target_path}/boot/map.hfs -part -no-desktop -hfs-volid \
		"${clst_iso_volume_id}" -hfs-bless ${clst_target_path}/boot -V "${clst_iso_volume_id}" -o ${1} ${clst_target_path} \
			|| die "Cannot make ISO image"
	;;
	sparc)
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
	
	x86|amd64)
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
