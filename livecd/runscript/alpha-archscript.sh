# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript/Attic/alpha-archscript.sh,v 1.3 2004/05/17 01:44:37 zhen Exp $

case $1 in
	kernel)
	;;

	preclean)
		# Add entries for ttyS0 and ttyS1 to /etc/inittab.
		echo "t0:12345:respawn:/sbin/agetty -L 9600 ttyS0 vt100" >> ${clst_chroot_path}/etc/inittab
		echo "t1:12345:respawn:/sbin/agetty -L 9600 ttyS1 vt100" >> ${clst_chroot_path}/etc/inittab
	;;

	clean)
	;;

	bootloader)
		# Time to create a filesystem tree for the ISO at
		# $clst_cdroot_path. We extract the "cdtar" to this directory,
		# which will normally contains a pre-built binary
		# boot-loader/filesystem skeleton for the ISO. 
		
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
			    $clst_cdroot_path/boot/$x.igz
		done

		acfg=$clst_cdroot_path/etc/aboot.conf
		bctr=0
		for x in $clst_boot_kernel
		do
			echo -n "${bctr}:/boot/$x " >> $acfg
			echo -n "initrd=/boot/$x.igz root=/dev/ram0 " >> $acfg
			echo "init=/linuxrc ${cmdline_opts} cdroot" >> $acfg
			((bctr=$bctr+1))
		done
	;;

	cdfs)
	;;

	iso)
		# this is for the livecd-final target, and calls the proper
		# command to build the iso file
		case ${clst_livecd_cdfstype} in
			zisofs)
				mkisofs -J -R -l -z -o ${2} ${clst_cdroot_path}
			;;
			*)
				mkisofs -J -R -l -o ${2} ${clst_cdroot_path}
			;;
		esac
		isomarkboot ${2} /boot/bootlx
	;;
esac
