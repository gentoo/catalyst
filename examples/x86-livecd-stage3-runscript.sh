# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/examples/Attic/x86-livecd-stage3-runscript.sh,v 1.2 2004/01/09 01:12:25 drobbins Exp $

die() {
	echo "$1"
	exit 1
}

case $1 in
run)
	#for running anything inside the chroot before the cleaning begins. This would normally
	#be done during the build of the livecd-stage2 target, but we support doing stuff here
	#too (although it should be avoided when possible.)
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	echo "CDBOOT=1" >> /etc/rc.conf
EOF
	[ $? -ne 0 ] && exit 1
;;
preclean)
	#preclean runs with bind mounts active -- for running any commands inside chroot
	$clst_CHROOT $clst_chroot_path /bin/bash << EOF
	emerge -C gcc binutils
EOF
	[ $? -ne 0 ] && exit 1
;;
clean)
	#clean runs after the bind mounts have been deactivated and and "livecd-stage3/clean"
	#directories have been wiped. This is where you should run commands that wipe out
	#things like static libraries, or other things that can't be cleaned up using the
	#"livecd-stage3/clean" variable in the spec file (which is used to wipe out directory
	#trees.)
	find $clst_chroot_path/usr/lib -iname "*.a" -exec rm -f {} \;
	;;
cdroot_setup)
	#use this to set up the cdroot ($clst_cdroot_path). This directory is meant to contain
	#a filesystem tree of what will be burned to the CD. We extract the "cdtar" to this
	#directory, which will normally contain a pre-built binary boot-loader and a filesystem
	#skeleton for the ISO.
	
	cdtar=$clst_livecd_stage3_cdtar
	[ "$cdtar" = "" ] && die "No livecd-stage3/cdtar specified (required)"
	tar xpvf $cdtar -C $clst_cdroot_path || die "Couldn't extract cdtar $cdtar"
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
		if [ ! -e "$clst_source_path/$x.tar.bz2" ] 
		then
			echo "Can't find kernel tarball at $clst_source_path/$x.tar.bz2"
			exit 1
		fi
		tar xjvf $clst_source_path/$x.tar.bz2 -C $clst_cdroot_path/isolinux
		#change kernel name from "kernel" to "gentoo", for example
		mv $clst_cdroot_path/isolinux/kernel $clst_cdroot_path/isolinux/$x
		#change initrd name from "initrd" to "gentoo.igz", for example
		mv $clst_cdroot_path/isolinux/initrd $clst_cdroot_path/isolinux/$x.igz
	done
	icfg=$clst_cdroot_path/isolinux/isolinux.cfg
	echo "default $first" > $icfg
	for x in $clst_boot_kernel
	do
		echo >> $icfg
		echo "label $x" >> $icfg
		echo "	kernel $x" >> $icfg
		echo "	append initrd=$x.igz root=/dev/ram0 init=/linuxrc" >> $icfg
	done
	#OK, now we need to prepare the loopback filesystem that we'll be booting. This is
	#tricky.
	echo "Calculating size of loopback filesystem..."
	loopsize=`du -ks $clst_cdroot_path`
	#increase the size by 1/4, then divide by 4 to get 4k blocks
	loopsize=$(( ( $loopsize + ( $loopsize /4 ) ) / 4 ) ))
	echo "Creating loopback file..."
	dd if=/dev/zero of=$clst_cdroot_path/livecd.loop bs=4k count=$loopsize || die "livecd.loop creation failure"
	echo "Calculating number of inodes required for ext2 filesystem..."
	numnodes=`find $clst_chroot_path | wc -l`
	numnodes=$(( $numnodes + 200 ))
	mke2fs -F -b 4096 -m 0 -N $numnodes -q $clst_cdroot_path/livecd.loop || die "Couldn't create ext2 filesystem"
	#some error handling should probably be added here for handling the loopback mount cleanup
	install -d $clst_cdroot_path/loopmount
	mount -t ext2 -o loop $clst_cdroot_path/livecd.loop || die "Couldn't mount loopback ext2 filesystem"
	cp -a $clst_chroot_path/* $clst_cdroot_path/loopmount
	[ $? -ne 0 ] && ( umount $clst_cdroot_path/loopmount; die "Couldn't copy files to loopback ext2 filesystem" )
	umount $clst_cdroot_path/loopmount || die "Couldn't unmount loopback ext2 filesystem"
	rm -rf $clst_cdroot_path/loopmount
	#now, $clst_cdroot_path should contain a proper bootable image for our iso, including
	#boot loader and loopback filesystem.
	;;
iso_create)
	#this is for the livecd-final target, and calls the proper command to build the iso file
	mkisofs -J -R -l -o ${clst_iso_path} -b isolinux/isolinux.bin -c isolinux/boot.cat \
	-no-emul-boot -boot-load-size 4 -boot-info-table $clst_cdroot_path
	;;
esac
