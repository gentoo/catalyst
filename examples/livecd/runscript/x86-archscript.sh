# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/examples/livecd/runscript/Attic/x86-archscript.sh,v 1.3 2004/01/21 05:48:24 drobbins Exp $

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
			tar xjvf $clst_chroot_path/tmp/binaries/$x.tar.bz2 -C $clst_cdroot_path/isolinux
			#change kernel name from "kernel" to "gentoo", for example
			mv $clst_cdroot_path/isolinux/kernel $clst_cdroot_path/isolinux/$x
			#change initrd name from "initrd" to "gentoo.igz", for example
			mv $clst_cdroot_path/isolinux/initrd $clst_cdroot_path/isolinux/$x.igz
		done
		icfg=$clst_cdroot_path/isolinux/isolinux.cfg
		kmsg=$clst_cdroot_path/isolinux/kernels.msg
		hmsg=$clst_cdroot_path/isolinux/help.msg
		echo "default $first" > $icfg
		echo "timeout 150" >> $icfg
		echo "prompt 1" >> $icfg
		echo "display boot.msg" >> $icfg
		echo "F1 kernels.msg" >> $icfg
		echo "F2 help.msg" >> $icfg

		echo "Available kernels:" > $kmsg
		echo "TEST HELP MESSAGE" > $hmsg

		for x in $clst_boot_kernel
		do
			echo >> $icfg
			echo "label $x" >> $icfg
			echo "	kernel $x" >> $icfg
			echo "	append initrd=$x.igz root=/dev/ram0 init=/linuxrc ${cmdline_opts} cdroot vga=0x317 splash=silent" >> $icfg
			echo >> $icfg
			echo "   $x" >> $kmsg
			echo "label $x-nofb" >> $icfg
			echo "	kernel $x" >> $icfg
			echo "	append initrd=$x.igz root=/dev/ram0 init=/linuxrc ${cmdline_opts} cdroot" >> $icfg
			echo >> $icfg
			echo "   ${x}-nofb" >> $kmsg
		done
	;;

	cdfs)
	;;

	iso)
		#this is for the livecd-final target, and calls the proper command to build the iso file
		mkisofs -J -R -l -o ${clst_iso_path} -b isolinux/isolinux.bin -c isolinux/boot.cat \
			-no-emul-boot -boot-load-size 4 -boot-info-table $clst_cdroot_path
	;;
esac
