# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript/Attic/hppa-archscript.sh,v 1.7 2005/01/28 20:53:39 wolf31o2 Exp $

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

		# Create a filesystem tree for the ISO at $clst_cdroot_path.
		# We extract the "cdtar" to this directory, which will normally contains a pre-built
		# binary boot-loader/filesystem skeleton for the ISO. 
		
		cdtar=${clst_livecd_cdtar}
		[ -z "$cdtar" ] && die "Required key livecd/cdtar not specified, exiting"
		tar xjpvf ${cdtar} -C ${clst_cdroot_path} || die "Couldn't extract cdtar ${cdtar}"
		
		[ -z "$clst_boot_kernel" ] && die "Required key boot/kernel not specified, exiting"
		
		# install our kernel(s) that were built in kmerge.sh
		first=""
		for x in ${clst_boot_kernel}
		do
			kbinary="${clst_chroot_path}/usr/portage/packages/gk_binaries/${x}-${clst_version_stamp}.tar.bz2"	
			if [ -z "$first" ]
			then
				# grab name of first kernel
				first="${x}"
			fi
			[ ! -e "${kbinary}" ] && die "Can't find kernel tarball at ${kbinary}"
			tar xjvf ${kbinary} -C ${clst_cdroot_path}/boot
		done

		# figure out what device manager we are using and handle it accordingly
		if [ "${clst_livecd_devmanager}" == "udev" ]
		then
			cmdline_opts="${cmdline_opts} udev nodevfs"
		else
			cmdline_opts="${cmdline_opts} noudev devfs"
		fi
		
		# THIS SHOULD BE IMPROVED !
		mv ${clst_cdroot_path}/boot/kernel* ${clst_cdroot_path}/vmlinux
		mv ${clst_cdroot_path}/boot/initrd* ${clst_cdroot_path}/initrd
		icfg=${clst_cdroot_path}/boot/palo.conf
		kmsg=${clst_cdroot_path}/boot/kernels.msg
		hmsg=${clst_cdroot_path}/boot/help.msg
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

	cdfs)
	;;

	iso)
		#this is for the livecd-stage2 target, and calls the proper command to build the iso file
		mkisofs -J -R -l -o  ${2} ${clst_cdroot_path}  || die "Cannot make ISO image"
		palo -f boot/palo.conf -C ${2}
	;;
esac
