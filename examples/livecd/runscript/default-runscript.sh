# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/examples/livecd/runscript/Attic/default-runscript.sh,v 1.8 2004/01/20 22:24:39 drobbins Exp $

#return codes to be used by archscript
RETURN_GOOD=0
RETURN_BAD=1
RETURN_CONTINUE=2

die() {
	echo "$1"
	exit $RETURN_BAD
}

case $clst_livecd_cdfstype in
zisofs)
	cmdline_opts="looptype=zisofs loop=/zisofs"
	;;
normal)
	cmdline_opts="looptype=normal loop=/livecd.loop"
	;;
noloop)
	cmdline_opts="looptype=noloop"
	;;
esac
export cmdline_opts

/bin/bash ${clst_livecd_archscript} $*
RET="$?"

[ "${RET}" = "0" ] && exit 0
[ "${RET}" = "1" ] && exit 1
# if $RET is 2, then we continue and run the runscript portion as well.

create_normal_loop()
{
		#We get genkernel-built kernels and initrds in place, create the loopback fs on 
		#$clst_cdroot_path, mount it, copy our bootable filesystem over, umount it, and 
		#we then have a ready-to-burn ISO tree at $clst_cdroot_path.

		echo "Calculating size of loopback filesystem..."
		loopsize=`du -ks $clst_chroot_path | cut -f1`
		[ "$loopsize" = "0" ] && loopsize=1
		#increase the size by 1/3, then divide by 4 to get 4k blocks
#		loopsize=$(( ( $loopsize + ( $loopsize / 2 ) ) / 4  ))
		# Add 4MB for filesystem slop
		loopsize=`expr $loopsize + 4096`
		echo "Creating loopback file..."
		dd if=/dev/zero of=$clst_cdroot_path/livecd.loop bs=1k count=$loopsize || die "livecd.loop creation failure"
		#echo "Calculating number of inodes required for ext2 filesystem..."
		#numnodes=`find $clst_chroot_path | wc -l`
		#numnodes=$(( $numnodes + 200 ))
		mke2fs -m 0 -F -q $clst_cdroot_path/livecd.loop || die "Couldn't create ext2 filesystem"
#		mke2fs -m 0 -F -b 4096 -q $clst_cdroot_path/livecd.loop || die "Couldn't create ext2 filesystem"
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
		return $RETURN_GOOD
}

create_zisofs()
{
	rm -rf ${clst_cdroot_path}/zisofs > /dev/null 2>&1
	echo "Creating zisofs..."
	mkzftree -z 9 -p2 ${clst_chroot_path} ${clst_cdroot_path}/zisofs || die "Could not run mkzftree, did you emerge zisofs"
	return $RETURN_GOOD
}

create_noloop()
{
	echo "Copying files for image (no loop)..."
	cp -a $clst_chroot_path/* $clst_cdroot_path || die "Could not copy files to image (no loop)"
	return $RETURN_GOOD
}

case $1 in
	kernel)
		shift
		numkernels="$1"
		shift
		count=0
		install -d /tmp/binaries
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

	preclean)
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
			rc-update add modules default
			rm -rf /etc/localtime
			cp /usr/share/zoneinfo/GMT /etc/localtime
			echo "livecd" > /etc/hostname
			sed -i -e '/\/dev\/[RBS]*/ s/^/#/' /etc/fstab
			echo "tmpfs		/	tmpfs	defaults	0 0" >> /etc/fstab
			sed -i -e '/dev-state/ s/^/#/' /etc/devfsd.conf
			# END OF SCRIPT TO UPDATE FILESYSTEM
EOF
		[ $? -ne 0 ] && exit $RETURN_BAD
	
		exit $RETURN_GOOD
	;;

	clean)
		find $clst_chroot_path/usr/lib -iname "*.pyc" -exec rm -f {} \;
		exit $RETURN_GOOD
	;;

	bootloader)
		exit $RETURN_GOOD
	;;

	cdfs)
		loopret=1
		if [ "${clst_livecd_cdfstype}" = "normal" ]
		then
			create_normal_loop
			loopret=$?
		elif [ "${clst_livecd_cdfstype}" = "zisofs" ]
		then
			create_zisofs
			loopret=$?
		elif [ "${clst_livecd_cdfstype}" = "noloop" ]
		then
			create_noloop
			loopret=$?
		fi		
		exit $loopret
	;;

	iso)
		exit $RETURN_GOOD
	;;
esac
exit $RETURN_GOOD
