#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/bootloader-setup.sh,v 1.5 2005/06/16 13:40:01 wolf31o2 Exp $
. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh

# $1 is the destination root

extract_cdtar $1
extract_kernels $1/boot
check_dev_manager
check_filesystem_type

default_append_line="initrd=${x}.igz root=/dev/ram0 init=/linuxrc acpi=off ${cmdline_opts} ${custom_kopts} cdroot"

case ${clst_mainarch} in
	alpha)
		acfg=$1/etc/aboot.conf
		bctr=0
		for x in ${clst_boot_kernel}
		do
			echo -n "${bctr}:/boot/${x} " >> ${acfg}
			echo -n "initrd=/boot/${x}.igz root=/dev/ram0 " >> ${acfg}
			echo "init=/linuxrc ${cmdline_opts} cdroot" >> ${acfg}
			((bctr=${bctr}+1))
		done
		;;

	arm)
		;;
	hppa)
		icfg=$1/boot/palo.conf
		kmsg=$1/boot/kernels.msg
		hmsg=$1/boot/help.msg
		echo "--commandline=0/${first} initrd=${x}.igz root=/dev/ram0 init=/linuxrc ${cmdline_opts}" >> ${icfg}
		echo "--bootloader=boot/iplboot" >> ${icfg}
		echo "--ramdisk=boot/${x}.igz" >> ${icfg}

#		for x in $clst_boot_kernel
#		do
#
#			eval custom_kopts=\$${x}_kernelopts
#			echo "APPENDING CUSTOM KERNEL ARGS: ${custom_kopts}"
#			echo >> $icfg
#			echo "label $x" >> $icfg
#			echo "	kernel $x" >> $icfg
#			echo "	append initrd=$x.igz root=/dev/ram0 init=/linuxrc ${cmdline_opts} ${custom_kopts} cdroot vga=0x317 splash=silent" >> $icfg
#			echo >> $icfg
#			echo "   $x" >> $kmsg
#			echo "label $x-nofb" >> $icfg
#			echo "	kernel $x" >> $icfg
#			echo "	append initrd=$x.igz root=/dev/ram0 init=/linuxrc ${cmdline_opts} ${custom_kopts} cdroot" >> $icfg
#			echo >> $icfg
#			echo "   ${x}-nofb" >> $kmsg
#		done
		;;
	ppc)
		# PPC requirements: 
		# -----------------
		# The specs indicate the kernels to be build. We need to put
		# those kernels and the corresponding initrd.img.gz(s) in the
		# /boot directory. This directory contains a message boot.msg 
		# containing some info to be displayed on boot, a configuration
		# (yaboot.conf) specifying the boot options (kernel/initrd 
		# combinations). The boot directory also contains a file called
		# yaboot, which normally gets copied from the live environment.
		# For now we supply a prebuilt file, prebuilt configuration 
		# and prebuilt boot message. This can be enhanced later on
		# but the following suffices for now:
		;;
	sparc*)
		scfg=$1/boot/silo.conf
		echo "default=\"help\"" > ${scfg}
		echo "message=\"/boot/boot.msg\"" >> ${scfg}

		for x in ${clst_boot_kernel}
		do
			echo >> ${icfg}
			echo "image=\"/boot/${x}\"" >> ${scfg}
			echo -e "\tlabel=\"${x}\"" >> ${scfg}
			echo -e "\tappend=\"initrd=/boot/${x}.igz root=/dev/ram0 init=/linuxrc ${cmdline_opts} cdroot\"" >> ${scfg}

		done

		echo "image=\"cat /boot/silo.conf\"" >> ${scfg}
		echo -e "label=\"config\"" >> ${scfg}
		echo "image=\"cat /boot/video.msg\"" >> ${scfg}
		echo -e "label=\"video\"" >> ${scfg}
		echo "image=\"cat /boot/help.msg\"" >> ${scfg}
		echo -e "label=\"help\"" >> ${scfg}
		;;
	x86|amd64)
		if [ -e $1/boot/isolinux.bin ]
		then
			# the rest of this function sets up the config file for isolinux
			icfg=$1/boot/isolinux.cfg
			kmsg=$1/boot/kernels.msg
			hmsg=$1/boot/help.msg
			echo "default ${first}" > ${icfg}
			echo "timeout 150" >> ${icfg}
			echo "prompt 1" >> ${icfg}
			echo "display boot.msg" >> ${icfg}
			echo "F1 kernels.msg" >> ${icfg}
			echo "F2 help.msg" >> ${icfg}

			echo "Available kernels:" > ${kmsg}
			cp ${clst_sharedir}/livecd/files/x86-help.msg ${hmsg}

			for x in ${clst_boot_kernel}
			do

				eval custom_kopts=\$${x}_kernelopts
				echo "APPENDING CUSTOM KERNEL ARGS: ${custom_kopts}"
				echo >> ${icfg}
				echo "label ${x}" >> ${icfg}
				echo "  kernel ${x}" >> ${icfg}
				if [ "${clst_livecd_splash_type}" == "gensplash" -a -n "${clst_livecd_splash_theme}" ]
				then
					echo "  append ${default_append_line} vga=791 dokeymap splash=silent,theme:${clst_livecd_splash_theme}" >> ${icfg}
				else
					echo "  append ${default_append_line} vga=791 dokeymap splash=silent" >> ${icfg}
				fi
			
				echo >> ${icfg}
				echo "   ${x}" >> ${kmsg}
				echo "label ${x}-nofb" >> ${icfg}
				echo "  kernel ${x}" >> ${icfg}
				echo "  append ${default_append_line} " >> ${icfg}
				echo >> ${icfg}
				echo "   ${x}-nofb" >> ${kmsg}
			done

			if [ -f $1/boot/memtest86 ]
			then
				echo >> $icfg
				echo "   memtest86" >> $kmsg
				echo "label memtest86" >> $icfg
				echo "  kernel memtest86" >> $icfg
			fi
		fi

		if [ -e $1/boot/grub/stage2_eltorito ]
		then
			icfg=$1/boot/grub/grub.conf
			echo "default 1" > ${icfg}
			echo "timeout 150" >> ${icfg}
			
			
			# Setup help message	
			hmsg=${clst_sharedir}/livecd/files/x86-help.msg
			hmsg_txt="$(cat ${hmsg})"
			
			echo >> ${icfg}
			echo "title help" >> ${icfg}
			echo "pause ${hmsg_txt}" >> ${icfg}
			
			
			for x in ${clst_boot_kernel}
			do
				eval custom_kopts=\$${x}_kernelopts
				echo "APPENDING CUSTOM KERNEL ARGS: ${custom_kopts}"
				echo >> ${icfg}
				echo "title ${x}" >> ${icfg}
				
				if [ "${clst_livecd_splash_type}" == "gensplash" -a -n "${clst_livecd_splash_theme}" ]
				then
					echo "kernel /boot/${x} ${default_append_line} vga=791 dokeymap splash=silent,theme:${clst_livecd_splash_theme}" >> ${icfg}
				else
					echo "kernel /boot/${x} ${default_append_line} vga=791 dokeymap splash=silent" >> ${icfg}
				fi

				if [ -e $1/boot/${x}.igz ]
				then
					echo "initrd /boot/${x}.igz" >> ${icfg}
				fi
				
				echo >> ${icfg}
				echo "title ${x} [ No FrameBuffer ]" >> ${icfg}
				echo "kernel ${x} /boot/${x} ${default_append_line}" >> ${icfg}
				if [ -e $1/boot/${x}.igz ]
				then
					echo "initrd /boot/${x}.igz" >> ${icfg}
				fi
			done

			if [ -f $1/boot/memtest86 ]
			then
				echo >> ${icfg}
				echo "title memtest86" >> ${icfg}
				echo "kernel /boot/memtest86" >> ${icfg}
			fi
		fi
		;;
esac
exit $?
