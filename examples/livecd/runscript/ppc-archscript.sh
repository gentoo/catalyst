# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/examples/livecd/runscript/Attic/ppc-archscript.sh,v 1.1 2004/02/25 19:10:06 pvdabeel Exp $

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
		
		cdtar=$clst_livecd_cdtar
		[ "$cdtar" = "" ] && die "No livecd/cdtar specified (required)"
		tar xjpvf $cdtar -C $clst_cdroot_path || die \
		    "Couldn't extract cdtar $cdtar"
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
			if [ ! -e "$clst_chroot_path/tmp/binaries/$x.tar.bz2" ] 
			then
				echo "Can't find kernel tarball at $clst_chroot_path/tmp/binaries/$x.tar.bz2"
				exit 1
			fi
			tar xjvf $clst_chroot_path/tmp/binaries/$x.tar.bz2 -C \
			    $clst_cdroot_path/boot
			# change kernel name from "kernel" to "gentoo", for
			# example
			mv $clst_cdroot_path/boot/kernel \
			    $clst_cdroot_path/boot/$x
			# change initrd name from "initrd" to "gentoo.igz",
			# for example
			mv $clst_cdroot_path/boot/initrd \
			    $clst_cdroot_path/boot/initrd.img.gz
		done
	;;

	cdfs)
	;;

	iso)
		# The name of the iso should be retrieved from the specs. For now, asssume GentooPPC_2004.0
		mkisofs -J -r -netatalk -hfs -probe -map boot/map.hfs -part -no-desktop -hfs-volid GentooPPC_2004.0 -hfs-bless ./boot -o ${clst_iso_path} ${clst_cdroot_path}
	;;
esac
