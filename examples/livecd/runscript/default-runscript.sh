# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/examples/livecd/runscript/Attic/default-runscript.sh,v 1.17 2004/02/25 19:22:36 brad_mssw Exp $

#return codes to be used by archscript

die() {
	echo "$1"
	exit 1
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
squashfs)
	cmdline_opts="looptype=squashfs loop=/livecd.squashfs"
	;;
gcloop)
	cmdline_opts="looptype=gcloop loop=/livecd.gcloop"
	;;
esac

source ${clst_livecd_archscript}

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
}

create_zisofs()
{
	rm -rf "${clst_cdroot_path}/zisofs" > /dev/null 2>&1
	echo "Creating zisofs..."
	mkzftree -z 9 -p2 "${clst_chroot_path}" "${clst_cdroot_path}/zisofs" || die "Could not run mkzftree, did you emerge zisofs"
}

create_noloop()
{
	echo "Copying files for image (no loop)..."
	cp -a "${clst_chroot_path}/*" "${clst_cdroot_path}" || die "Could not copy files to image (no loop)"
}

create_gcloop()
{
	create_normal_loop
	compress_gcloop_ucl -b 131072 -c 10 "${clst_cdroot_path}/livecd.loop" "${clst_cdroot_path}/livecd.gcloop" || die "compress_gcloop_ucl failed, did you emerge gcloop?"
	rm -f "${clst_cdroot_path}/livecd.loop"
	# only a gcloop image should exist in cdroot path
}

create_squashfs()
{
	echo "Creating squashfs..."
	mksquashfs -noappend "${clst_chroot_path}" "${clst_cdroot_path}/livecd.squashfs" || die "mksquashfs failed, did you emerge squashfs?"
}

case $1 in
	kernel)
		shift
		numkernels="$1"
		shift
		$clst_CHROOT $clst_chroot_path /bin/bash << EOF
		env-update
		source /etc/profile
		export CONFIG_PROTECT="-*"
		[ -n "${clst_ENVSCRIPT}" ] && source /tmp/envscript
		emerge genkernel
		install -d /tmp/binaries
EOF
	[ $? -ne 0 ] && exit 1
		count=0
		while [ $count -lt $numkernels ]
		do
			clst_kname="$1"
			shift
			clst_ksource="$1"
			shift
			clst_kextversion="$1"
			shift
			$clst_CHROOT $clst_chroot_path /bin/bash << EOF
				die() {
					echo "$1"
					exit 1
				}
				# Script to build each kernel, kernel-related packages 
				source /etc/profile
				[ -n "${clst_ENVSCRIPT}" ] && source /tmp/envscript
				rm -f /usr/src/linux
				[ -e /var/tmp/$clst_kname.use ] && export USE="\$( cat /var/tmp/$clst_kname.use )" || unset USE
				# Don't use pkgcache here, as the kernel source may get emerge with different USE variables
				# (and thus different patches enabled/disabled.) Also, there's no real benefit in using the
				# pkgcache for kernel source ebuilds.
				emerge $clst_ksource || exit 1
				[ ! -e /usr/src/linux ] && die "Can't find required directory /usr/src/linux"
				#if catalyst has set NULL_VALUE, extraversion wasn't specified so we skip this part
				if [ "$clst_kextversion" != "NULL_VALUE" ]
				then
					# Append Extraversion
					sed -i -e "s:EXTRAVERSION \(=.*\):EXTRAVERSION \1-${clst_kextversion}:" /usr/src/linux/Makefile
				fi
				if [ -n "${clst_CCACHE}" ]
				then
					#enable ccache for genkernel
					export PATH="/usr/lib/ccache/bin:\${PATH}"
				fi
				genkernel ${genkernel_args} --kerneldir=/usr/src/linux --kernel-config=/var/tmp/$clst_kname.config --minkernpackage=/tmp/binaries/$clst_kname.tar.bz2 all || exit 1
				#now we merge any kernel-dependent packages
				if [ -e /var/tmp/$clst_kname.packages ]
				then
					for x in \$( cat /var/tmp/$clst_kname.packages )
					do
						# we don't want to use the pkgcache for these since the results
						# are kernel-dependent.
						echo DEBUG emerge "\$x"
						USE="-X" emerge "\$x"
					done
				fi
				cd /usr/src
				rm -rf linux*
				#now the unmerge... (wipe db entry)
				emerge -C $clst_ksource
				unset USE
EOF
			[ $? -ne 0 ] && exit 1 
			count=$(( $count + 1 ))
		done
		$clst_CHROOT $clst_chroot_path /bin/bash << EOF
			#cleanup steps
			source /etc/profile
			emerge -C genkernel 
			/sbin/depscan.sh
			find /lib/modules -name modules.dep -exec touch {} \;
EOF
	[ $? -ne 0 ] && exit 1
	;;

	preclean)
		$clst_CHROOT $clst_chroot_path /bin/bash << EOF
			# SCRIPT TO UPDATE FILESYSTEM SPECIFIC FOR LIVECD. THIS GETS EXECUTED IN CHROOT
			env-update
			source /etc/profile
			rc-update del iptables default
			rc-update del netmount default
#			rc-update add hotplug default
#			rc-update add kudzu default
			rc-update add autoconfig default
			rc-update del keymaps
			rc-update del consolefont
			rc-update add metalog default
			rc-update add modules default
			[ -e /etc/init.d/bootsplash ] && rc-update add bootsplash default
			rm -rf /etc/localtime
			cp /usr/share/zoneinfo/GMT /etc/localtime
			echo "livecd" > /etc/hostname
			sed -i -e '/\/dev\/[RBS]*/ s/^/#/' /etc/fstab
			echo "tmpfs		/	tmpfs	defaults	0 0" >> /etc/fstab
			sed -i -e '/dev-state/ s/^/#/' /etc/devfsd.conf
			# END OF SCRIPT TO UPDATE FILESYSTEM
EOF
		[ $? -ne 0 ] && exit 1 
	;;

	clean)
		find $clst_chroot_path/usr/lib -iname "*.pyc" -exec rm -f {} \;
	;;

	bootloader)
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
		elif [ "${clst_livecd_cdfstype}" = "gcloop" ]
		then
			create_gcloop
			loopret=$?
		elif [ "${clst_livecd_cdfstype}" = "squashfs" ]
		then
			create_squashfs
			loopret=$?
		fi		
		exit $loopret
	;;

	iso)
	;;
esac
exit 0 
