# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/examples/livecd/runscript/Attic/default-runscript.sh,v 1.5 2004/01/17 18:37:24 brad_mssw Exp $

# Section has been handled, do not execute additional scripts
RETURN_GOOD=0
# An error has occurred
RETURN_BAD=1
# Should continue
RETURN_CONTINUE=2

# Set default looptype to zisofs
if [ "${LOOPTYPE}" == "" ]
then
	LOOPTYPE="zisofs"
fi

export LOOPTYPE

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

if [ "${ARCH_RUNSCRIPT}" == "" -o ! -f "${ARCH_RUNSCRIPT}" ]
then
	die "ARCH_RUNSCRIPT NOT DEFINED OR NOT FOUND"
fi

${ARCH_RUNSCRIPT} $*
RET="$?"

if [ "${RET}" != "${RETURN_CONTINUE}" ]
then
	if [ "${RET}" -eq "0" ]
	then
		echo "${ARCH_RUNSCRIPT} finished successfully, don\'t have to run default commands"
		exit 0
	else
		echo "${ARCH_RUNSCRIPT} errored out, not continuing"
		exit 1
	fi
else
	echo "${ARCH_RUNSCRIPT} finished successfully, running default commands"
fi

create_normal_loop()
{
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
		exit $RETURN_GOOD
	;;

	loop)
		loopret=1
		if [ "${LOOPTYPE}" = "normal" ]
		then
			create_normal_loop
			loopret=$?
		elif [ "${LOOPTYPE}" = "zisofs" ]
		then
			create_zisofs
			loopret=$?
		elif [ "${LOOPTYPE}" = "noloop" ]
		then
			create_noloop
			loopret=$?
		fi		
		exit $loopret
	;;

	iso_create)
		#this is for the livecd-final target, and calls the proper command to build the iso file
		exit $RETURN_GOOD
	;;
esac
exit $RETURN_GOOD
