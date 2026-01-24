#!/bin/bash

source ${clst_shdir}/support/functions.sh

# $1 is the destination root

if [[ -n ${clst_cdtar} ]]; then
	extract_cdtar $1
fi

extract_kernels $1/boot

cmdline_opts=()

# Add any additional options

if [ -n "${clst_livecd_bootargs}" ]
then
	for x in ${clst_livecd_bootargs}
	do
		cmdline_opts+=(${x})
	done
fi

case ${clst_fstype} in
	squashfs)
		cmdline_opts+=(looptype=squashfs loop=/image.squashfs)
	;;
	jffs2)
		cmdline_opts+=(looptype=jffs2 loop=/image.jffs2)
	;;
esac

# Optional memtest setups
memtest_grub() {
  if [[ -e $1/memtest64.bios ]]; then
    echo 'if [ "x$grub_platform" = xpc ]; then'
    echo '  menuentry "Memtest86+ 64bit BIOS" {'
    echo '    linux "/memtest64.bios"'
    echo '  }'
    echo 'fi'
  fi
  if [[ -e $1/memtest.efi64 ]]; then
    echo 'if [ "x$grub_platform" = xefi ]; then'
    echo '  menuentry "Memtest86+ 64bit UEFI" {'
    echo '    chainloader "/memtest.efi64"'
    echo '  }'
    echo 'fi'
  fi
  if [[ -e $1/memtest32.bios ]]; then
    echo 'menuentry "Memtest86+ 32bit BIOS" {'
    echo '  linux "/memtest32.bios"'
    echo '}'
  fi
}

default_append_line=(${cmdline_opts[@]} cdroot)
default_dracut_append_line=(${clst_livecd_bootargs} root=live:CDLABEL=${clst_iso_volume_id} rd.live.dir=/ rd.live.squashimg=image.squashfs cdroot)

case ${clst_hostarch} in
	alpha)
		# NO SOFTLEVEL SUPPORT YET
		acfg=$1/etc/aboot.conf
		bctr=0
		# Pass 1 is for non-serial
		for x in ${clst_boot_kernel}
		do
			echo -n "${bctr}:/boot/${x} " >> ${acfg}
			echo -n "initrd=/boot/${x}.igz " >> ${acfg}
			echo "${cmdline_opts[@]} cdroot" >> ${acfg}
			((bctr=${bctr}+1))
		done
		# Pass 2 is for serial
		cmdline_opts+=(console=ttyS0)
		for x in ${clst_boot_kernel}
		do
			echo -n "${bctr}:/boot/${x} " >> ${acfg}
			echo -n "initrd=/boot/${x}.igz " >> ${acfg}
			echo "${cmdline_opts[@]} cdroot" >> ${acfg}
			((bctr=${bctr}+1))
		done
	;;
	arm)
		# NO SOFTLEVEL SUPPORT YET
	;;
	hppa)
		# NO SOFTLEVEL SUPPORT YET
		mkdir -p $1/boot

		icfg=$1/boot/palo.conf
		kmsg=$1/boot/kernels.msg
		hmsg=$1/boot/help.msg
		# Make sure we strip the extension to the kernel to allow palo to choose
		boot_kernel_common_name=${first/%32/}
		boot_kernel_common_name=${boot_kernel_common_name/%64/}

		# copy the bootloader for the final image
		cp /usr/share/palo/iplboot $1/boot/

		echo "--commandline=0/${boot_kernel_common_name} initrd=${first}.igz ${default_append_line[@]}" >> ${icfg}
		echo "--bootloader=boot/iplboot" >> ${icfg}
		echo "--ramdisk=boot/${first}.igz" >> ${icfg}
		for x in ${clst_boot_kernel}
		do
			echo "--recoverykernel=boot/${x}" >> ${icfg}
		done
	;;
	amd64|arm64|ia64|ppc*|powerpc*|sparc*|x86|i?86)
		kern_subdir=/boot
		iacfg=$1/boot/grub/grub.cfg
		mkdir -p $1/boot/grub
		echo 'set default=0' > ${iacfg}
		echo 'set gfxpayload=keep' >> ${iacfg}
		echo 'set timeout=10' >> ${iacfg}
		echo 'insmod all_video' >> ${iacfg}
		echo 'insmod png' >> ${iacfg}
		echo 'insmod gfxterm' >> ${iacfg}
		echo 'terminal_output gfxterm' >> ${iacfg}
		echo 'set gfxmode=auto' >> ${iacfg}
		echo 'set theme=/boot/grub/themes/gentoo_frosted/theme.txt' >> ${iacfg}
		echo '' >> ${iacfg}
		for x in ${clst_boot_kernel}
		do
			eval "kernel_console=\$clst_boot_kernel_${x}_console"
			eval "distkernel=\$clst_boot_kernel_${x}_distkernel"

			echo "menuentry 'Boot LiveGUI (kernel: ${x}) (persistent)' --class gnu-linux --class os {"  >> ${iacfg}
			if [ ${distkernel} = "yes" ]
			then
				echo "	search --no-floppy --set=root -l ${clst_iso_volume_id}" >> ${iacfg}
				echo "	linux ${kern_subdir}/${x} ${default_dracut_append_line[@]} rd.live.overlay=PARTLABEL=Appended3:/LiveGUI-Overlay rd.live.overlay.cowfs=xfs" >> ${iacfg}
			else
				echo "	linux ${kern_subdir}/${x} ${default_append_line[@]}" >> ${iacfg}
			fi
			echo "	initrd ${kern_subdir}/${x}.igz" >> ${iacfg}
			echo "}" >> ${iacfg}
			echo "" >> ${iacfg}

			echo "menuentry 'Boot LiveGUI (kernel: ${x})' --class gnu-linux --class os {"  >> ${iacfg}
			if [ ${distkernel} = "yes" ]
			then
				echo "	search --no-floppy --set=root -l ${clst_iso_volume_id}" >> ${iacfg}
				echo "	linux ${kern_subdir}/${x} ${default_dracut_append_line[@]}" >> ${iacfg}
			else
				echo "	linux ${kern_subdir}/${x} ${default_append_line[@]}" >> ${iacfg}
			fi
			echo "	initrd ${kern_subdir}/${x}.igz" >> ${iacfg}
			echo "}" >> ${iacfg}
			echo "" >> ${iacfg}

			echo "menuentry 'Boot LiveGUI (kernel: ${x}) (cached)' --class gnu-linux --class os {"  >> ${iacfg}
			if [ ${distkernel} = "yes" ]
			then
				echo "	search --no-floppy --set=root -l ${clst_iso_volume_id}" >> ${iacfg}
				echo "	linux ${kern_subdir}/${x} ${default_dracut_append_line[@]} rd.live.ram=1" >> ${iacfg}
			else
				echo "	linux ${kern_subdir}/${x} ${default_append_line[@]} docache" >> ${iacfg}
			fi

			echo "	initrd ${kern_subdir}/${x}.igz" >> ${iacfg}
			echo "}" >> ${iacfg}

			if [ -n "${kernel_console}" ]
			then
			echo "submenu 'Special console options (kernel: ${x})' --class gnu-linux --class os {" >> ${iacfg}
				for y in ${kernel_console}
				do
					echo "menuentry 'Boot LiveCD (kernel: ${x} console=${y})' --class gnu-linux --class os {"  >> ${iacfg}
					echo "	linux ${kern_subdir}/${x} ${default_append_line[@]} console=${y}" >> ${iacfg}
					echo "	initrd ${kern_subdir}/${x}.igz" >> ${iacfg}
					echo "}" >> ${iacfg}
					echo "" >> ${iacfg}
				done
				echo "}" >> ${iacfg}
			fi
			echo "" >> ${iacfg}
		done
		memtest_grub $1 >> ${iacfg}
	;;
	mips)
		# NO SOFTLEVEL SUPPORT YET

		# Mips is an interesting arch -- where most archs will
		# use ${1} as the root of the LiveCD, an SGI LiveCD lacks
		# such a root.  Instead, we will use ${1} as a scratch
		# directory to build the components we need for the
		# CD image, and then pass these components to the
		# `sgibootcd` tool which outputs a final CD image
		scratch="${1}"
		mkdir -p ${scratch}/{kernels/misc,arcload}
		echo "" > ${scratch}/arc.cf

		# Move kernel binaries to ${scratch}/kernels, and
		# move everything else to ${scratch}/kernels/misc
		for x in ${clst_boot_kernel}; do
			[ -e "${1}/boot/${x}" ] && mv ${1}/boot/${x} ${scratch}/kernels
			[ -e "${1}/boot/${x}.igz" ] && mv ${1}/boot/${x}.igz ${scratch}/kernels/misc
		done
		[ -d "${1}/boot" ] && rmdir ${1}/boot

		# Source the arcload source file to generated required sections of arc.cf
		source ${clst_shdir}/support/mips-arcload_conf.sh

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
		[ -e "${1}/sashARCS" ] && mv ${1}/sashARCS ${scratch}/arcload
		[ -e "${1}/sash64" ] && mv ${1}/sash64 ${scratch}/arcload
		[ -e "${1}/arc.cf" ] && mv ${1}/arc.cf ${scratch}/arcload
		;;
esac
exit $?
