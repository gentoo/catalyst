# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/examples/livecd/runscript/Attic/x86-runscript.sh,v 1.1 2004/01/15 00:25:56 brad_mssw Exp $

# Section has been handled, do not execute additional scripts
RETURN_GOOD=0
# An error has occurred
RETURN_BAD=1
# This script executed properly, continue with additional scripts
RETURN_CONTINUE=2

die() {
	echo "$1"
	exit $RETURN_BAD
}

case $1 in
	kernbuild)
		echo "no generic process for x86, continuing"
		exit $RETURN_CONTINUE
	;;

	setupfs)
		echo "no generic process for x86, continuing"
		exit $RETURN_CONTINUE
	;;

	preclean)
		echo "no generic process for x86, continuing"
		exit $RETURN_CONTINUE
	;;

	clean)
		echo "no generic process for x86, continuing"
		exit $RETURN_CONTINUE
	;;

	setup_bootloader)
		#Time to create a filesystem tree for the ISO at $clst_cdroot_path.
		#We extract the "cdtar" to this directory, which will normally contains a pre-built
		#binary boot-loader/filesystem skeleton for the ISO. 
		
		cdtar=$clst_livecd_cdtar
		[ "$cdtar" = "" ] && die "No livecd/cdtar specified (required)"
		tar xjpvf $cdtar -C $clst_cdroot_path || die "Couldn't extract cdtar $cdtar"
		if [ "$clst_boot_kernel" = "" ]
		then
			echo "No boot/kernel setting defined, exiting."
			exit 1
		fi
		first=""
		for x in $clst_boot_kernel
		do
			if [ "$first" = "" ]
			then
				#grab name of first kernel
				first="$x"
			fi
			if [ ! -e "$clst_binaries_source_path/$x.tar.bz2" ] 
			then
				echo "Can't find kernel tarball at $clst_binaries_source_path/$x.tar.bz2"
				exit 1
			fi
			tar xjvf $clst_binaries_source_path/$x.tar.bz2 -C $clst_cdroot_path/isolinux
			#change kernel name from "kernel" to "gentoo", for example
			mv $clst_cdroot_path/isolinux/kernel $clst_cdroot_path/isolinux/$x
			#change initrd name from "initrd" to "gentoo.igz", for example
			mv $clst_cdroot_path/isolinux/initrd $clst_cdroot_path/isolinux/$x.igz
		done
		icfg=$clst_cdroot_path/isolinux/isolinux.cfg
		echo "default $first" > $icfg
		echo "prompt: 1" >> $icfg
		echo "display: boot.msg" >> $icfg
		echo "F1 boot.msg" >> $icfg
		echo "F2 help.msg" >> $icfg

		for x in $clst_boot_kernel
		do
			echo >> $icfg
			echo "label $x" >> $icfg
			echo "	kernel $x" >> $icfg
			echo "	append initrd=$x.igz root=/dev/ram0 init=/linuxrc loop=/livecd.loop cdroot vga=0x317 splash=silent" >> $icfg
			echo >> $icfg
			echo "label $x-nofb" >> $icfg
			echo "	kernel $x" >> $icfg
			echo "	append initrd=$x.igz root=/dev/ram0 init=/linuxrc loop=/livecd.loop cdroot" >> $icfg
		done
		exit $RETURN_CONTINUE
	;;

	loop)
		echo "no generic process for x86, continuing"
		exit $RETURN_CONTINUE
	;;

	iso_create)
		#this is for the livecd-final target, and calls the proper command to build the iso file
		mkisofs -J -R -l -o ${clst_iso_path} -b isolinux/isolinux.bin -c isolinux/boot.cat \
			-no-emul-boot -boot-load-size 4 -boot-info-table $clst_cdroot_path
		exit $RETURN_GOOD
	;;
esac
exit $RETURN_CONTINUE
