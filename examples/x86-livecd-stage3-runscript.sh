# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/examples/Attic/x86-livecd-stage3-runscript.sh,v 1.1 2004/01/07 18:46:57 drobbins Exp $

case $1 in
run)
	#probably don't need to run anything in the chroot, but we support it just in case.
	;;
preclean)
	#preclean runs with bind mounts active -- for running any commands inside chroot
	;;
clean)
	#clean runs after the bind mounts have been deactivated, and "livecd-stage3/clean" directories have been wiped.
	;;
cdroot_setup)
	#use this to set up the cdroot ($clst_cdroot_path)
	cdtar=$clst_livecd_stage3_cdtar
	if [ "$cdtar" != "" ]
	then
		tar xpvf $cdtar -C $clst_cdroot_path || die
	fi
	install -d $clst_cdroot_path/isolinux
	if [ "$clst_boot_kernel" = "" ]
	then
		echo "No boot/kernel setting defined, exiting."
		exit 1
	fi
	for x in $clst_boot_kernel
	do
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
	;;
esac
