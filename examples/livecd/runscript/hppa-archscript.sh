# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/examples/livecd/runscript/Attic/hppa-archscript.sh,v 1.1 2004/03/06 20:41:53 gmsoft Exp $

case $1 in
	kernel)
		genkernel_args=""
		export genkernel_args
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
		
		cdtar=$clst_livecd_cdtar
		[ "$cdtar" = "" ] && die "No livecd/cdtar specified (required)"
		tar xjpvf $cdtar -C $clst_cdroot_path || die "Couldn't extract cdtar $cdtar"
		[ "$clst_boot_kernel" = "" ] && die "No boot/kernel setting defined, exiting."
		first=""
		for x in $clst_boot_kernel
		do
			if [ "$first" = "" ]
			then
				#grab name of first kernel
				first="$x"
			fi
			[ ! -e "$clst_chroot_path/tmp/binaries/$x.tar.bz2" ] && die "Can't find kernel tarball at $clst_chroot_path/tmp/binaries/$x.tar.bz2"
			tar xjvf $clst_chroot_path/tmp/binaries/$x.tar.bz2 -C $clst_cdroot_path/boot
			#change kernel name from "kernel" to "gentoo", for example
		done
		# THIS SHOULD BE IMPROVED !
			mv $clst_cdroot_path/boot/kernel $clst_cdroot_path/vmlinux
			#change initrd name from "initrd" to "gentoo.igz", for example
			mv $clst_cdroot_path/boot/initrd $clst_cdroot_path/initrd
		icfg=$clst_cdroot_path/boot/palo.conf
		kmsg=$clst_cdroot_path/boot/kernels.msg
		hmsg=$clst_cdroot_path/boot/help.msg
		echo "--commandline=0/$first initrd=$x.igz root=/dev/ram0 init=/linuxrc ${cmdline_opts}" >> $icfg
		echo "--bootloader=boot/iplboot" >> $icfg
		echo "--ramdisk=boot/$x.igz" >> $icfg

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
		#this is for the livecd-final target, and calls the proper command to build the iso file
		mkisofs -J -R -r -l -o ${clst_iso_path} $clst_cdroot_path
		palo -f boot/palo.conf -C ${clst_iso_path}
	;;
esac
