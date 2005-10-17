#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/support/bootloader-setup.sh,v 1.14 2005/10/17 17:11:33 rocket Exp $
. ${clst_sharedir}/targets/support/functions.sh
. ${clst_sharedir}/targets/support/filesystem-functions.sh

# $1 is the destination root

extract_cdtar $1
extract_kernels $1/boot
check_dev_manager
check_bootargs
check_filesystem_type

default_append_line="initrd=${x}.igz root=/dev/ram0 init=/linuxrc ${cmdline_opts} ${custom_kopts} cdroot"

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
		echo "--commandline=0/${first} initrd=${first}.igz root=/dev/ram0 init=/linuxrc ${cmdline_opts}" >> ${icfg}
		echo "--bootloader=boot/iplboot" >> ${icfg}
		echo "--ramdisk=boot/${first}.igz" >> ${icfg}
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
		
		# this sets up the config file for yaboot
		icfg=$1/boot/yaboot.conf
		kmsg=$1/boot/boot.msg
		echo "default ${first}" > ${icfg}
		echo "timeout 300" >> ${icfg}
		echo "device=cd:" >> ${icfg}
		echo "root=/dev/ram" >> ${icfg}
		echo "fgcolor=white" >> ${icfg}
		echo "bgcolor=black" >> ${icfg}
		echo "message=/boot/boot.msg" >> ${icfg}
		for x in ${clst_boot_kernel}
		do
			eval custom_kopts=\$${x}_kernelopts
			echo "APPENDING CUSTOM KERNEL ARGS: ${custom_kopts}"
			echo >> ${icfg}
			echo "image=/boot/${x}" >> ${icfg}
			echo "initrd=/boot/${x}.igz" >> ${icfg}
			echo "label=${x}" >> ${icfg}
			echo "read-write" >> ${icfg}
			if [ "${clst_livecd_splash_type}" == "gensplash" -a -n "${clst_livecd_splash_theme}" ]
			then
			    echo "append ${default_append_line} vga=791 splash=silent,theme:${clst_livecd_splash_theme}" >> ${icfg}
			else
			    echo "append ${default_append_line} vga=791 splash=silent" >> ${icfg}
			fi
		done
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
	ia64)
		iacfg=$1/boot/elilo.conf
		echo 'prompt' > ${iacfg}
		echo 'message=/efi/boot/elilo.msg' >> ${iacfg}
		echo 'chooser=simple' >> ${iacfg}
		echo 'timeout=50' >> ${iacfg}
		echo >> ${iacfg}
		for x in ${clst_boot_kernel}
		do
			echo "image=/efi/boot/${x}" >> ${iacfg}
			echo "  label=${x}" >> ${iacfg}
			echo '  append="'${default_append_line}'"' >> ${iacfg}
			echo "  initrd=/efi/boot/${x}.igz" >> ${iacfg}
			echo >> ${iacfg}
			echo "image=/efi/boot/${x}" >> ${iacfg}
			echo "  label=${x}-serial">> ${iacfg}
			echo '  append="'${default_append_line}' console=tty0 console=ttyS0,9600"' >> ${iacfg}
			echo "  initrd=/efi/boot/${x}.igz" >> ${iacfg}
			echo >> ${iacfg}
		done
		cp ${iacfg} $1/boot/efi/boot
		mv $1/boot/${x}{,.igz} $1/boot/efi/boot
		;;
	x86|amd64)
		if [ -e $1/boot/isolinux.bin ]
		then
			# the rest of this function sets up the config file for isolinux
			icfg=$1/boot/isolinux.cfg
			kmsg=$1/boot/kernels.msg
			echo "default ${first}" > ${icfg}
			echo "timeout 150" >> ${icfg}
			echo "prompt 1" >> ${icfg}
			echo "display boot.msg" >> ${icfg}
			echo "F1 kernels.msg" >> ${icfg}
			echo "F2 F2.msg" >> ${icfg}
			echo "F3 F3.msg" >> ${icfg}
			echo "F4 F4.msg" >> ${icfg}
			echo "F5 F5.msg" >> ${icfg}
			echo "F6 F6.msg" >> ${icfg}
			echo "F7 F7.msg" >> ${icfg}

			echo "Available kernels:" > ${kmsg}
			for i in 2 3 4 5 6 7
			do
				cp ${clst_sharedir}/livecd/files/x86-F$i.msg \
					$1/isolinux/F$i.msg
			done

			for x in ${clst_boot_kernel}
			do

				eval custom_kopts=\$${x}_kernelopts
				echo "APPENDING CUSTOM KERNEL ARGS: ${custom_kopts}"
				echo >> ${icfg}
				echo "label ${x}" >> ${icfg}
				echo "  kernel ${x}" >> ${icfg}
				if [ "${clst_livecd_splash_type}" == "gensplash" -a -n "${clst_livecd_splash_theme}" ]
				then
					echo "  append ${default_append_line} vga=791 splash=silent,theme:${clst_livecd_splash_theme} CONSOLE=/dev/tty1 quiet" >> ${icfg}
				else
					echo "  append ${default_append_line} vga=791 splash=silent" >> ${icfg}
				fi
			
				echo >> ${icfg}
				echo "   ${x}" >> ${kmsg}
				echo "label ${x}-nofb" >> ${icfg}
				echo "  kernel ${x}" >> ${icfg}
				echo "  append ${default_append_line}" >> ${icfg}
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
			echo >> ${icfg}
			echo "title help" >> ${icfg}
			for i in 2 3 4 5 6 7
			do
				cp ${clst_sharedir}/livecd/files/README.txt
					$1/boot/help.msg
				echo "cat /boot/help.msg" >> ${icfg}
			done

			for x in ${clst_boot_kernel}
			do
				eval custom_kopts=\$${x}_kernelopts
				echo "APPENDING CUSTOM KERNEL ARGS: ${custom_kopts}"
				echo >> ${icfg}
				echo "title ${x}" >> ${icfg}
				
				if [ "${clst_livecd_splash_type}" == "gensplash" -a -n "${clst_livecd_splash_theme}" ]
				then
					echo "kernel /boot/${x} ${default_append_line} vga=791 splash=silent,theme:${clst_livecd_splash_theme} CONSOLE=/dev/tty1 quiet" >> ${icfg}
				else
					echo "kernel /boot/${x} ${default_append_line} vga=791 splash=silent" >> ${icfg}
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
	mips)
		# Mips is an interesting arch -- where most archs will
		# use ${1} as the root of the LiveCD, an SGI LiveCD lacks
		# such a root.  Instead, we will use ${1} as a scratch
		# directory to build the components we need for the
		# CD image, and then pass these components to the
		# `sgibootcd` tool which outputs a final CD image
		scratch="${1}"
		mkdir ${scratch}/kernels
		mkdir ${scratch}/kernels/misc
		mkdir ${scratch}/arcload
		echo "" > ${scratch}/arc.cf

		# Move kernel binaries to ${scratch}/kernels, and
		# move everything else to ${scratch}/kernels/misc
		for x in ${clst_boot_kernel}; do
			mv ${1}/boot/${x} ${scratch}/kernels
			mv ${1}/boot/${x}.igz ${scratch}/kernels/misc
		done
		rmdir ${1}/boot

		# Source the bashified arcload config
		source ${clst_sharedir}/targets/support/mips-arcload_conf.sh

		# Generate top portions of the config
		echo -e "${topofconfig}${serial}${dbg}${cmt1}" >> ${scratch}/arc.cf

		# Next, figure out what kernels were specified in the
		# spec file, and generate the appropriate arcload conf
		# blocks specific to each system
		ip22="$(echo ${clst_boot_kernel} | tr " " "\n" | grep "ip22" | tr "\n" " ")"
		ip27="$(echo ${clst_boot_kernel} | tr " " "\n" | grep "ip27" | tr "\n" " ")"
		ip28="$(echo ${clst_boot_kernel} | tr " " "\n" | grep "ip28" | tr "\n" " ")"
		ip30="$(echo ${clst_boot_kernel} | tr " " "\n" | grep "ip30" | tr "\n" " ")"
		ip32="$(echo ${clst_boot_kernel} | tr " " "\n" | grep "ip32" | tr "\n" " ")"

		if [ -n "${ip22}" ]; then
			echo -e "${ip22base}" >> ${scratch}/arc.cf
			for x in ${ip22}; do echo -e "${!x}" >> ${scratch}/arc.cf; done
			echo -e "${ip22vid}${ip22x}" >> ${scratch}/arc.cf
		fi

		[ -n "${ip27}" ] && echo -e "${ip27base}" >> ${scratch}/arc.cf
		[ -n "${ip28}" ] && echo -e "${ip28base}" >> ${scratch}/arc.cf
		[ -n "${ip30}" ] && echo -e "${ip30base}" >> ${scratch}/arc.cf

		if [ -n "${ip32}" ]; then
			echo -e "${ip32base}" >> ${scratch}/arc.cf
			for x in ${ip32}; do echo -e "${!x}" >> ${scratch}/arc.cf; done
			echo -e "${ip32vid}${ip32x}" >> ${scratch}/arc.cf
		fi

		# Finish off the config
		echo -e "${cmt2}" >> ${scratch}/arc.cf

		# Move the bootloader binaries & config to their destination
		mv ${1}/sashARCS ${1}/sash64 ${1}/arc.cf ${scratch}/arcload
		;;
esac
exit $?
