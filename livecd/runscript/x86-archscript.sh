# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript/Attic/x86-archscript.sh,v 1.10 2004/09/29 01:32:51 zhen Exp $

case $1 in
	kernel)
		;;
	
	preclean)
		;;

	clean)
		;;

	bootloader)
		# CDFSTYPE and loop_opts are exported from the default
		# runscript

		# Time to create a filesystem tree for the ISO at $clst_cdroot_path.
		# We extract the "cdtar" to this directory, which will normally contains a pre-built
		# binary boot-loader/filesystem skeleton for the ISO. 
		
		cdtar=${clst_livecd_cdtar}
		[ -z "${cdtar}" ] && die "Required key livecd/cdtar not defined, exiting"
		tar xjpvf ${cdtar} -C ${clst_cdroot_path} || die "Couldn't extract cdtar ${cdtar}"
		
		[ -z "${clst_boot_kernel}" ] && die "Required key boot/kernel not defined, exiting."
		
		first=""
		for x in ${clst_boot_kernel}
		do
			kbinary="${clst_chroot_path}/usr/portage/packages/gk_binaries/${x}-${clst_version_stamp}.tar.bz2"

			if [ -z "${first}" ]
			then
				# grab name of first kernel
				first="${x}"
			fi
			
			# unpack the kernel that was compiled in kmerge.sh
			[ ! -e "${kbinary}" ] && die "Can't find kernel tarball at ${kbinary}"
			tar xjvf "${kbinary}" -C "${clst_cdroot_path}"/isolinux
			
			#change kernel name from "kernel" to "gentoo", for example
			mv "${clst_cdroot_path}"/isolinux/kernel* "${clst_cdroot_path}"/isolinux/"${x}"
			
			#change initrd name from "initrd" to "gentoo.igz", for example
			mv "${clst_cdroot_path}"/isolinux/initrd* "${clst_cdroot_path}"/isolinux/"${x}".igz
		done
		
		# the rest of this function sets up the config file for isolinux
		icfg=${clst_cdroot_path}/isolinux/isolinux.cfg
		kmsg=${clst_cdroot_path}/isolinux/kernels.msg
		hmsg=${clst_cdroot_path}/isolinux/help.msg
		echo "default ${first}" > ${icfg}
		echo "timeout 150" >> ${icfg}
		echo "prompt 1" >> ${icfg}
		echo "display boot.msg" >> ${icfg}
		echo "F1 kernels.msg" >> ${icfg}
		echo "F2 help.msg" >> ${icfg}

		# figure out what device manager we are using and handle it accordingly
		if [ ${clst_livecd_devmanager} == "udev" ]
		then
			cmdline_opts="${cmdline_opts} udev nodevfs"
		fi	

		echo "Available kernels:" > ${kmsg}
		cp ${clst_sharedir}/livecd/files/x86-help.msg ${hmsg}

		for x in ${clst_boot_kernel}
		do

			eval custom_kopts=\$${x}_kernelopts
			echo "APPENDING CUSTOM KERNEL ARGS: ${custom_kopts}"
			echo >> ${icfg}
			echo "label ${x}" >> ${icfg}
			echo "	kernel ${x}" >> ${icfg}
			echo "	append initrd=${x}.igz root=/dev/ram0 init=/linuxrc acpi=off ${cmdline_opts} ${custom_kopts} cdroot vga=791 splash=silent" >> ${icfg}
			echo >> ${icfg}
			echo "   ${x}" >> ${kmsg}
			echo "label ${x}-nofb" >> ${icfg}
			echo "	kernel ${x}" >> ${icfg}
			echo "	append initrd=${x}.igz root=/dev/ram0 init=/linuxrc acpi=off ${cmdline_opts} ${custom_kopts} cdroot" >> ${icfg}
			echo >> ${icfg}
			echo "   ${x}-nofb" >> ${kmsg}
		done

		if [ -f ${clst_cdroot_path}/isolinux/memtest86 ]
		then
			echo >> $icfg
			echo "   memtest86" >> $kmsg
			echo "label memtest86" >> $icfg
			echo "  kernel memtest86" >> $icfg
		fi
		;;
	
	cdfs)
		;;

	iso)
		#this is for the livecd-stage2 target, and calls the proper command to build the iso file
		mkisofs -J -R -l -o  ${2} -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -z ${clst_cdroot_path}
		;;
esac
