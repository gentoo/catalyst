# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript/Attic/default-runscript.sh,v 1.15 2004/07/13 15:15:22 zhen Exp $

#return codes to be used by archscript
die() {
	echo "$1"
	exit 1
}

case ${clst_livecd_cdfstype} in
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

create_normal_loop() {

		#We get genkernel-built kernels and initrds in place, create the loopback fs on 
		#$clst_cdroot_path, mount it, copy our bootable filesystem over, umount it, and 
		#we then have a ready-to-burn ISO tree at $clst_cdroot_path.

		echo "Calculating size of loopback filesystem..."
		loopsize=`du -ks ${clst_chroot_path} | cut -f1`
		[ "${loopsize}" = "0" ] && loopsize=1
		# Add 4MB for filesystem slop
		loopsize=`expr ${loopsize} + 4096`
		echo "Creating loopback file..."
		dd if=/dev/zero of=${clst_cdroot_path}/livecd.loop bs=1k count=${loopsize} || die "livecd.loop creation failure"
		mke2fs -m 0 -F -q ${clst_cdroot_path}/livecd.loop || die "Couldn't create ext2 filesystem"
		install -d ${clst_cdroot_path}/loopmount
		sync; sync; sleep 3 #try to work around 2.6.0+ loopback bug
		mount -t ext2 -o loop ${clst_cdroot_path}/livecd.loop ${clst_cdroot_path}/loopmount || die "Couldn't mount loopback ext2 filesystem"
		sync; sync; sleep 3 #try to work around 2.6.0+ loopback bug
		echo "cp -a ${clst_chroot_path}/* ${clst_cdroot_path}/loopmount"
		cp -a ${clst_chroot_path}/* ${clst_cdroot_path}/loopmount 

		[ $? -ne 0 ] && { umount ${clst_cdroot_path}/loopmount; die "Couldn't copy files to loopback ext2 filesystem"; }
		umount ${clst_cdroot_path}/loopmount || die "Couldn't unmount loopback ext2 filesystem"
		rm -rf ${clst_cdroot_path}/loopmount
		#now, $clst_cdroot_path should contain a proper bootable image for our iso, including
		#boot loader and loopback filesystem.
}

create_zisofs() {

	rm -rf "${clst_cdroot_path}/zisofs" > /dev/null 2>&1
	echo "Creating zisofs..."
	mkzftree -z 9 -p2 "${clst_chroot_path}" "${clst_cdroot_path}/zisofs" || die "Could not run mkzftree, did you emerge zisofs"

}

create_noloop() {

	echo "Copying files for image (no loop)..."
	cp -a "${clst_chroot_path}"/* "${clst_cdroot_path}" || die "Could not copy files to image (no loop)"
	
}

create_gcloop() {
	create_normal_loop
	compress_gcloop_ucl -b 131072 -c 10 "${clst_cdroot_path}/livecd.loop" "${clst_cdroot_path}/livecd.gcloop" || die "compress_gcloop_ucl failed, did you emerge gcloop?"
	rm -f "${clst_cdroot_path}/livecd.loop"
	# only a gcloop image should exist in cdroot path
	
}

create_squashfs() {
	echo "Creating squashfs..."
	mksquashfs "${clst_chroot_path}" "${clst_cdroot_path}/livecd.squashfs" -noappend || die "mksquashfs failed, did you emerge squashfs-utils?"
	
}

## START RUNSCRIPT

case $1 in
	kernel)
		shift
		numkernels="$1"
		shift
		
		# setup genkernel and do any pre-kernel merge opts
		cp -a ${clst_sharedir}/livecd/runscript-support/pre-kmerge.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/pre-kmerge.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/pre-kmerge.sh

		# the kernel merge process is done in a chroot
		cp -a ${clst_sharedir}/livecd/runscript-support/kmerge.sh ${clst_chroot_path}/tmp
		count=0
		while [ ${count} -lt ${numkernels} ]
		do
			export clst_kname="$1"
			shift
			export clst_ksource="$1"
			shift
			export clst_kextversion="$1"
			shift
		${clst_CHROOT} ${clst_chroot_path} /tmp/kmerge.sh || exit 1
		count=$(( ${count} + 1 ))
		done
		rm -f ${clst_chroot_path}/tmp/kmerge.sh
	
		# clean up genkernel and do any post-kernel merge opts
		cp -a ${clst_sharedir}/livecd/runscript-support/post-kmerge.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/post-kmerge.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/post-kmerge.sh
		;;

	preclean)
		# overwrite /etc/init.d/local in the livecd root
		rm -f ${clst_chroot_path}/etc/init.d/local
		cp -a ${clst_sharedir}/livecd/files/livecd-rclocal ${clst_chroot_path}/etc/init.d/local
		
		# move over the motd (if applicable)
		if [ -n "${clst_livecd_motd}" ]
		then
			cp -a ${clst_livecd_motd} ${clst_chroot_path}/etc/motd
		fi
		
		# now, finalize and tweak the livecd fs (inside of the chroot)
		cp ${clst_sharedir}/livecd/runscript-support/livecdfs-update.sh ${clst_chroot_path}/tmp
		${clst_CHROOT} ${clst_chroot_path} /tmp/livecdfs-update.sh || exit 1
		rm -f ${clst_chroot_path}/tmp/livecdfs-update.sh
		
		# if the user has their own fs update script, execute it
		if [ -n "${clst_livecd_fsscript}" ]
		then
			cp ${clst_livecd_fsscript} ${clst_chroot_path}/tmp/fsscript.sh
			chmod 755 ${clst_chroot_path}/tmp/fsscript.sh
			${clst_CHROOT} ${clst_chroot_path} /tmp/fsscript.sh || exit 1
			rm -f ${clst_chroot_path}/tmp/fsscript.sh
		fi
		;;

	clean)
		find ${clst_chroot_path}/usr/lib -iname "*.pyc" -exec rm -f {} \;
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
