# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/examples/livecd/runscript/Attic/default-runscript.sh,v 1.1 2004/01/15 00:25:56 brad_mssw Exp $

# Section has been handled, do not execute additional scripts
RETURN_GOOD=0
# An error has occurred
RETURN_BAD=1

die() {
	echo "$1"
	exit $RETURN_BAD
}

#Here is how the livecd runscript works:

# livecd-stage2 begins. The "run" part of this script is executed, which is used to build
# kernels and copy any needed binaries to /tmp/binaries. The arguments passed to this 
# runscript are "run <numkernels> <kname1> <ksource1> <kname2> <ksource2> ...". For example,
# the args might be "run 2 gentoo =sys-kernel/gentoo-dev-sources-2.6.1 smp 
# =sys-kernel/foo-sources-2.4.24". The kernel configs for each kernel can be found already
# copied to /var/tmp/<kname>.config.

# livecd-stage2 ends.
# livecd-stage3 begins.

# runscript: preclean executes (with bind mounts still mounted)
# catalyst: do livecd/unmerge (with bind mounts still mounted)
# catalyst: bind mounts unmounted
# catalyst: do livecd/empty
# catalyst: do livecd/delete
# runscript: livecd/clean
# runscript: cdroot_setup

# livecd-stage3 completes.

case $1 in
	kernbuild)
		shift
		numkernels="$1"
		shift
		count=0
		while [ $count -lt $numkernels ]
		do
			clst_kname="$1"
			shift
			clst_ksource="$1"
			shift
			$clst_CHROOT $clst_chroot_path /bin/bash << EOF
				# SCRIPT TO BUILD EACH KERNEL. THIS GETS EXECUTED IN CHROOT
				env-update
				source /etc/profile
				export CONFIG_PROTECT="-*"
				emerge genkernel
				rm -f /usr/src/linux
				export USE="-* build"
				if [ -n "${clst_PKGCACHE}" ]
				then
					emerge --usepkg --buildpkg --noreplace $clst_ksource || exit 1
				else
					emerge --noreplace $clst_ksource || exit 1
				fi
				genkernel --kerneldir=/usr/src/linux --kernel-config=/var/tmp/$clst_kname.config --minkernpackage=/tmp/binaries/$clst_kname.tar.bz2 all || exit 1
				emerge -C genkernel $clst_ksource
				# END OF SCRIPT TO BUILD EACH KERNEL
			EOF
			[ $? -ne 0 ] && exit $RETURN_BAD
			count=$(( $count + 1 ))
		done
		exit $RETURN_GOOD
	;;

	setupfs)
		$clst_CHROOT $clst_chroot_path /bin/bash << EOF
			# SCRIPT TO UPDATE FILESYSTEM SPECIFIC FOR LIVECD. THIS GETS EXECUTED IN CHROOT
			env-update
			source /etc/profile
			rc-update del iptables default
			rc-update del netmount default
			rc-update add hotplug default
			rc-update add kudzu default
			rc-update del keymaps
			rc-update del consolefont
			rc-update add metalog default
			rm -rf /etc/localtime
			cp /usr/share/zoneinfo/GMT /etc/localtime
			echo "livecd" > /etc/hostname
			sed -i -e 's:^/dev/[RBS]*::' /etc/fstab
			sed -i -e '/dev-state/ s/^/#/' /etc/devfsd.conf
			# END OF SCRIPT TO UPDATE FILESYSTEM
		EOF
		[ $? -ne 0 ] && exit $RETURN_BAD
	
		exit $RETURN_GOOD
	;;

	preclean)
		#preclean runs with bind mounts active -- for running any commands inside chroot.
		#The chroot environment has not been trimmed in any way, so you still have a full
		#environment.
		# This below doesn't seem to get honored
		#$clst_CHROOT $clst_chroot_path /bin/bash << EOF
		#	echo "CDBOOT=1" >> /etc/rc.conf
		#EOF
		#[ $? -ne 0 ] && exit $RETURN_BAD
		exit $RETURN_GOOD
	;;

	clean)
		#livecd/unmerge, bind-unmount, and livecd/{empty,delete,prune}
		#have already executed at this point. You now have the opportunity to perform
		#any additional cleaning steps that may be required.

		find $clst_chroot_path/usr/lib -iname "*.pyc" -exec rm -f {} \;
		exit $RETURN_GOOD
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
		for x in $clst_boot_kernel
		do
			echo >> $icfg
			echo "label $x" >> $icfg
			echo "	kernel $x" >> $icfg
			echo "	append initrd=$x.igz root=/dev/ram0 init=/linuxrc loop=/livecd.loop cdroot" >> $icfg
		done
		exit $RETURN_GOOD
	;;

	loop)
		#We get genkernel-built kernels and initrds in place, create the loopback fs on 
		#$clst_cdroot_path, mount it, copy our bootable filesystem over, umount it, and 
		#we then have a ready-to-burn ISO tree at $clst_cdroot_path.

		echo "Calculating size of loopback filesystem..."
		loopsize=`du -ks $clst_chroot_path | cut -f1`
		[ "$loopsize" = "0" ] && loopsize=1
		#increase the size by 1/3, then divide by 4 to get 4k blocks
		loopsize=$(( ( $loopsize + ( $loopsize / 2 ) ) / 4  ))
		echo "Creating loopback file..."
		dd if=/dev/zero of=$clst_cdroot_path/livecd.loop bs=4k count=$loopsize || die "livecd.loop creation failure"
		#echo "Calculating number of inodes required for ext2 filesystem..."
		#numnodes=`find $clst_chroot_path | wc -l`
		#numnodes=$(( $numnodes + 200 ))
		mke2fs -m 0 -F -b 4096 -q $clst_cdroot_path/livecd.loop || die "Couldn't create ext2 filesystem"
		install -d $clst_cdroot_path/loopmount
		sync; sync; sleep 3 #try to work around 2.6.0+ loopback bug
		mount -t ext2 -o loop $clst_cdroot_path/livecd.loop $clst_cdroot_path/loopmount || die "Couldn't mount loopback ext2 filesystem"
		sync; sync; sleep 3 #try to work around 2.6.0+ loopback bug
		echo "cp -a $clst_chroot_path/* $clst_cdroot_path/loopmount"
		cp -a $clst_chroot_path/* $clst_cdroot_path/loopmount 

		[ $? -ne 0 ] && { umount $clst_cdroot_path/loopmount; die "Couldn't copy files to loopback ext2 filesystem"; }
		umount $clst_cdroot_path/loopmount || die "Couldn't unmount loopback ext2 filesystem"
		rm -rf $clst_cdroot_path/loopmount
		#now, $clst_cdroot_path should contain a proper bootable image for our iso, including
		#boot loader and loopback filesystem.
		exit $RETURN_GOOD
	;;

	iso_create)
		#this is for the livecd-final target, and calls the proper command to build the iso file
		mkisofs -J -R -l -o ${clst_iso_path} -b isolinux/isolinux.bin -c isolinux/boot.cat \
			-no-emul-boot -boot-load-size 4 -boot-info-table $clst_cdroot_path
	;;
esac
exit $RETURN_GOOD
