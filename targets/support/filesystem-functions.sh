# Dont forget to update functions.sh  check_looptype
# $1 is the target directory for the filesystem

create_normal_loop() {
    export source_path="${clst_destpath}"
    export destination_path="$1"
    export loopname="image.loop"

    #We get genkernel-built kernels and initrds in place, create the loopback fs on 
    #$clst_target_path, mount it, copy our bootable filesystem over, umount it, and 
    #we then have a ready-to-burn ISO tree at $clst_target_path.

    echo "Calculating size of loopback filesystem..."
    loopsize=`du -ks ${source_path} | cut -f1`
    [ "${loopsize}" = "0" ] && loopsize=1
    # Add 4MB for filesystem slop
    loopsize=`expr ${loopsize} + 4096`
    echo "Creating loopback file..."
    dd if=/dev/zero of=${destination_path}/${loopname} bs=1k count=${loopsize} || die "${loopname} creation failure"
    mke2fs -m 0 -F -q ${destination_path}/${loopname} || die "Couldn't create ext2 filesystem"
    install -d ${destination_path}/loopmount
    sync; sync; sleep 3 #try to work around 2.6.0+ loopback bug
    mount -t ext2 -o loop ${destination_path}/${loopname} ${destination_path}/loopmount || die "Couldn't mount loopback ext2 filesystem"
    sync; sync; sleep 3 #try to work around 2.6.0+ loopback bug
    echo "cp -a ${source_path}/* ${destination_path}/loopmount"
    cp -a ${source_path}/* ${destination_path}/loopmount 
    [ $? -ne 0 ] && { umount ${destination_path}/${loopname}; die "Couldn't copy files to loopback ext2 filesystem"; }
    umount ${destination_path}/loopmount || die "Couldn't unmount loopback ext2 filesystem"
    rm -rf ${destination_path}/loopmount
    #now, $clst_target_path should contain a proper bootable image for our iso, including
    #boot loader and loopback filesystem.
}



create_zisofs() {
	rm -rf "$1/zisofs" > /dev/null 2>&1
	echo "Creating zisofs..."
	mkzftree -z 9 -p2 "${clst_destpath}" "$1/zisofs" || die "Could not run mkzftree, did you emerge zisofs"

}

create_noloop() {
	echo "Copying files for image (no loop)..."
	cp -a "${clst_destpath}"/* "$1" || die "Could not copy files to image (no loop)"
	
}

create_gcloop() {
	echo "Creating gcloop..."
	export loopname="image.gloop"
	create_normal_loop
	compress_gcloop_ucl -b 131072 -c 10 "$1/livecd.loop" "$1/livecd.gcloop" || die "compress_gcloop_ucl failed, did you emerge gcloop?"
	rm -f "$1/livecd.loop"
	# only a gcloop image should exist in target path
	
}

create_squashfs() {
	echo "Creating squashfs..."
	export loopname="image.squashfs"
	mksquashfs "${clst_destpath}" "$1/${loopname}" ${clst_fs_ops} -noappend || die "mksquashfs failed, did you emerge squashfs-tools?"
	
}

create_jffs() {
	echo "Creating jffs..."
	export loopname="image.jffs"
	#fs_check /usr/sbin/mkfs.jffs jffs sys-fs/mtd
	mkfs.jffs -d ${clst_destpath} -o $1/${loopname} ${clst_fs_ops} || die "Could not create a jffs filesystem"
}

create_jffs2(){
	echo "Creating jffs2..."
	export loopname="image.jffs"
	#fs_check /usr/sbin/mkfs.jffs2 jffs2 sys-fs/mtd
	mkfs.jffs2 --root=${clst_destpath} --output=$1/${loopname} ${clst_fs_ops} || die "Could not create a jffs2 filesystem"
}

create_cramfs(){
	echo "Creating cramfs..."
	export loopname="image.cramfs"
	#fs_check /sbin/mkcramfs cramfs sys-fs/cramfs
	mkcramfs ${clst_fs_ops} ${clst_destpath} $1/${loopname} || die "Could not create a cramfs filesystem"
}
