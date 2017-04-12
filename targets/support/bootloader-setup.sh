#!/bin/bash

source ${clst_shdir}/support/functions.sh
source ${clst_shdir}/support/filesystem-functions.sh

# $1 is the destination root

# We handle boot loader a little special.  Most arches require a cdtar with bootloader files
# but we can generate one for amd64/x86 now
if [ -n "${clst_cdtar}" ]
then
	extract_cdtar $1
elif [ "${clst_buildarch}" = "x86" ] || [ "${clst_buildarch}" = "amd64" ]
then
	#assume if there is no cdtar and we are on a supported arch that the user just wants us to handle this
	create_bootloader $1
else
	#While this seems a little crazy, it's entirely possible the bootloader is just shoved in isoroot overlay
	echo "No cdtar and unable to auto generate boot loader files... good luck"
fi

extract_kernels $1/boot
check_bootargs
check_filesystem_type

default_append_line="root=/dev/ram0 init=/linuxrc ${cmdline_opts} ${custom_kopts} cdroot"
[ -n "${clst_splash_theme}" ] && default_append_line="${default_append_line} splash=silent,theme:${clst_livecd_splash_theme} CONSOLE=/dev/tty1 quiet"

case ${clst_hostarch} in
	alpha)
		# NO SOFTLEVEL SUPPORT YET
		acfg=$1/etc/aboot.conf
		bctr=0
		# Pass 1 is for non-serial
		for x in ${clst_boot_kernel}
		do
			echo -n "${bctr}:/boot/${x} " >> ${acfg}
			echo -n "initrd=/boot/${x}.igz root=/dev/ram0 " >> ${acfg}
			echo "init=/linuxrc ${cmdline_opts} cdroot" >> ${acfg}
			((bctr=${bctr}+1))
		done
		# Pass 2 is for serial
		cmdline_opts="${cmdline_opts} console=ttyS0"
		for x in ${clst_boot_kernel}
		do
			echo -n "${bctr}:/boot/${x} " >> ${acfg}
			echo -n "initrd=/boot/${x}.igz root=/dev/ram0 " >> ${acfg}
			echo "init=/linuxrc ${cmdline_opts} cdroot" >> ${acfg}
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

		for x in ${clst_boot_kernel}
		do
			eval kopts=\$clst_boot_kernel_${x}_kernelopts
			my_kopts="${my_kopts} ${kopts}"
		done

		# copy the bootloader for the final image
		cp /usr/share/palo/iplboot $1/boot/

		echo "--commandline=0/${boot_kernel_common_name} initrd=${first}.igz ${default_append_line} ${my_kopts}" >> ${icfg}
		echo "--bootloader=boot/iplboot" >> ${icfg}
		echo "--ramdisk=boot/${first}.igz" >> ${icfg}
		for x in ${clst_boot_kernel}
		do
			echo "--recoverykernel=boot/${x}" >> ${icfg}
		done
	;;
	ppc*|powerpc*)
	    # GRUB2 Openfirmware
		kern_subdir=/boot
		iacfg=$1/boot/grub/grub.cfg
		mkdir -p $1/boot/grub
		echo 'set default=0' > ${iacfg}
		echo 'set gfxpayload=keep' >> ${iacfg}
		echo 'set timeout=10' >> ${iacfg}
		echo 'insmod all_video' >> ${iacfg}
		echo '' >> ${iacfg}
		for x in ${clst_boot_kernel}
		do
			eval "clst_kernel_console=\$clst_boot_kernel_${x}_console"
			eval custom_kopts=\$${x}_kernelopts

			echo "menuentry 'Boot LiveCD (kernel: ${x})' --class gnu-linux --class os {"  >> ${iacfg}
			echo "	linux ${kern_subdir}/${x} ${default_append_line}" >> ${iacfg}
			echo "	initrd ${kern_subdir}/${x}.igz" >> ${iacfg}
			echo "}" >> ${iacfg}
			echo "" >> ${iacfg}
			echo "menuentry 'Boot LiveCD (kernel: ${x}) (cached)' --class gnu-linux --class os {"  >> ${iacfg}
			echo "	linux ${kern_subdir}/${x} ${default_append_line} docache" >> ${iacfg}
			echo "	initrd ${kern_subdir}/${x}.igz" >> ${iacfg}
			echo "}" >> ${iacfg}
			if [ -n "${clst_kernel_console}" ]
			then
			echo "submenu 'Special console options (kernel: ${x})' --class gnu-linux --class os {" >> ${iacfg}
				for y in ${clst_kernel_console}
				do
					echo "menuentry 'Boot LiveCD (kernel: ${x} console=${y})' --class gnu-linux --class os {"  >> ${iacfg}
					echo "	linux ${kern_subdir}/${x} ${default_append_line} console=${y}" >> ${iacfg}
					echo "	initrd ${kern_subdir}/${x}.igz" >> ${iacfg}
					echo "}" >> ${iacfg}
					echo "" >> ${iacfg}
				done
				echo "}" >> ${iacfg}
			fi
			echo "" >> ${iacfg}
		done
	;;
	sparc*)
		# NO SOFTLEVEL SUPPORT YET
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
		echo "image=\"cat /boot/parameters.msg\"" >> ${scfg}
		echo -e "label=\"parameters\"" >> ${scfg}
	;;
	ia64)
		# NO SOFTLEVEL SUPPORT YET
		iacfg=$1/boot/elilo.conf
		echo 'prompt' > ${iacfg}
		echo 'message=/efi/boot/elilo.msg' >> ${iacfg}
		echo 'chooser=simple' >> ${iacfg}
		echo 'timeout=50' >> ${iacfg}
		echo 'relocatable' >> ${iacfg}
		echo >> ${iacfg}
		for x in ${clst_boot_kernel}
		do
			echo "image=/efi/boot/${x}" >> ${iacfg}
			echo "  label=${x}" >> ${iacfg}
			echo '  append="'initrd=${x}.igz ${default_append_line}'"' >> ${iacfg}
			echo "  initrd=/efi/boot/${x}.igz" >> ${iacfg}
			echo >> ${iacfg}
			echo "image=/efi/boot/${x}" >> ${iacfg}
			echo "  label=${x}-serial">> ${iacfg}
			echo '  append="'initrd=${x}.igz ${default_append_line}' console=tty0 console=ttyS0,9600"' >> ${iacfg}
			echo "  initrd=/efi/boot/${x}.igz" >> ${iacfg}
			echo >> ${iacfg}
			echo "image=/efi/boot/${x}" >> ${iacfg}
			echo "  label=${x}-ilo">> ${iacfg}
			echo '  append="'initrd=${x}.igz ${default_append_line}' console=tty0 console=ttyS3,9600"' >> ${iacfg}
			echo "  initrd=/efi/boot/${x}.igz" >> ${iacfg}
			echo >> ${iacfg}
			echo "image=/efi/boot/${x}" >> ${iacfg}
			echo "  label=${x}-sgi">> ${iacfg}
			echo '  append="'initrd=${x}.igz ${default_append_line}' console=tty0 console=ttySG0,115200"' >> ${iacfg}
			echo "  initrd=/efi/boot/${x}.igz" >> ${iacfg}
			echo >> ${iacfg}
			mv $1/boot/${x}{,.igz} $1/boot/efi/boot
		done
		cp ${iacfg} $1/boot/efi/boot
	;;
	x86|amd64)
		if [ -e $1/isolinux/isolinux.bin ]
		then
			# the rest of this function sets up the config file for isolinux
			icfg=$1/isolinux/isolinux.cfg
			kmsg=$1/isolinux/kernels.msg
			echo "default ${first}" > ${icfg}
			echo "timeout 150" >> ${icfg}
			echo "ontimeout localhost" >> ${icfg}
			echo "prompt 1" >> ${icfg}
			echo "display boot.msg" >> ${icfg}
			echo "F1 kernels.msg" >> ${icfg}
			for k in {2..7}
			do
				echo "F${k} F${k}.msg" >> ${icfg}
			done

			echo "Available kernels:" > ${kmsg}
			for i in {2..7}
			do
				cp ${clst_sharedir}/livecd/files/x86-F$i.msg \
					$1/isolinux/F$i.msg
			done

			for x in ${clst_boot_kernel}
			do
				eval custom_kopts=\$${x}_kernelopts
				echo "APPENDING CUSTOM KERNEL ARGS: ${custom_kopts}"
				echo >> ${icfg}

				eval "clst_kernel_softlevel=\$clst_boot_kernel_${x}_softlevel"

				if [ -n "${clst_kernel_softlevel}" ]
				then
					for y in ${clst_kernel_softlevel}
					do
						echo "label ${x}-${y}" >> ${icfg}
						echo "  kernel /boot/${x}" >> ${icfg}
						echo "  append ${default_append_line} softlevel=${y} initrd=/boot/${x}.igz vga=791" >> ${icfg}

						echo >> ${icfg}
						echo "   ${x}" >> ${kmsg}
						echo "label ${x}-${y}-nofb" >> ${icfg}
						echo "  kernel /boot/${x}" >> ${icfg}
						echo "  append ${default_append_line} softlevel=${y} initrd=/boot/${x}.igz" >> ${icfg}
						echo >> ${icfg}
						echo "   ${x}-nofb" >> ${kmsg}
					done
				else
					echo "label ${x}" >> ${icfg}
					echo "  kernel /boot/${x}" >> ${icfg}
					echo "  append ${default_append_line} initrd=/boot/${x}.igz vga=791" >> ${icfg}
					echo >> ${icfg}
					echo "   ${x}" >> ${kmsg}
					echo "label ${x}-nofb" >> ${icfg}
					echo "  kernel /boot/${x}" >> ${icfg}
					echo "  append ${default_append_line} initrd=/boot/${x}.igz" >> ${icfg}
					echo >> ${icfg}
					echo "   ${x}-nofb" >> ${kmsg}
				fi
			done

			if [ -f $1/isolinux/memtest86 ]
			then
				echo >> $icfg
				echo "   memtest86" >> $kmsg
				echo "label memtest86" >> $icfg
				echo "  kernel memtest86" >> $icfg
			fi
			echo >> $icfg
			echo "label localhost" >> $icfg
			echo "  localboot -1" >> $icfg
			echo "  MENU HIDE" >> $icfg
		fi

		# GRUB2
		if [ -d $1/grub ] || [ -f "$1/boot/EFI/BOOT/BOOTX64.EFI" ]
		then
			#the grub dir may not exist, better safe than sorry
			[ -d "$1/grub" ] || mkdir -p "$1/grub"

			iacfg=$1/grub/grub.cfg
			echo 'set default=0' > ${iacfg}
			echo 'set gfxpayload=keep' >> ${iacfg}
			echo 'set timeout=10' >> ${iacfg}
			echo 'insmod all_video' >> ${iacfg}
			echo '' >> ${iacfg}
			for x in ${clst_boot_kernel}
			do
				echo "menuentry 'Boot LiveCD (kernel: ${x})' --class gnu-linux --class os {"  >> ${iacfg}
				echo "	linux /boot/${x} ${default_append_line}" >> ${iacfg}
				echo "	initrd /boot/${x}.igz" >> ${iacfg}
				echo "}" >> ${iacfg}
				echo "" >> ${iacfg}
				echo "menuentry 'Boot LiveCD (kernel: ${x}) (cached)' --class gnu-linux --class os {"  >> ${iacfg}
				echo "	linux /boot/${x} ${default_append_line} docache" >> ${iacfg}
				echo "	initrd /boot/${x}.igz" >> ${iacfg}
				echo "}" >> ${iacfg}
				echo "" >> ${iacfg}
			done
		fi
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
		[ ! -d "${scratch}/kernels" ] && mkdir ${scratch}/kernels
		[ ! -d "${scratch}/kernels/misc" ] && mkdir ${scratch}/kernels/misc
		[ ! -d "${scratch}/arcload" ] && mkdir ${scratch}/arcload
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
