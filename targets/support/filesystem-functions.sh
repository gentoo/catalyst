# Dont forget to update functions.sh  check_looptype
# $1 is the target directory for the filesystem

create_normal_loop() {
	export source_path="${clst_destpath}"
	export destination_path="$1"
	export loopname="image.loop"

	# We get genkernel-built kernels and initrds in place, create the loopback
	# file system on $clst_target_path, mount it, copy our bootable filesystem
	# over, umount it, and have a ready-to-burn ISO tree at $clst_target_path.

	echo "Calculating size of loopback filesystem..."
	loopsize=`du -ks ${source_path} | cut -f1`
	[ "${loopsize}" = "0" ] && loopsize=1
	# Add 4MB for filesystem slop
	loopsize=`expr ${loopsize} + 4096`
	echo "Creating loopback file..."
	dd if=/dev/zero of=${destination_path}/${loopname} bs=1k count=${loopsize} \
		|| die "${loopname} creation failure"
	mke2fs -m 0 -F -q ${destination_path}/${loopname} \
		|| die "Couldn't create ext2 filesystem"
	install -d ${destination_path}/loopmount
	sync; sync; sleep 3 # Try to work around 2.6.0+ loopback bug
	mount -t ext2 -o loop ${destination_path}/${loopname} \
		${destination_path}/loopmount \
		|| die "Couldn't mount loopback ext2 filesystem"
	sync; sync; sleep 3 # Try to work around 2.6.0+ loopback bug
	echo "cp -pPR ${source_path}/* ${destination_path}/loopmount"
	cp -pPR ${source_path}/* ${destination_path}/loopmount
	[ $? -ne 0 ] && { umount ${destination_path}/${loopname}; \
		die "Couldn't copy files to loopback ext2 filesystem"; }
	umount ${destination_path}/loopmount \
		|| die "Couldn't unmount loopback ext2 filesystem"
	rm -rf ${destination_path}/loopmount
	# Now, $clst_target_path should contain a proper bootable image for our
	# ISO, including boot loader and loopback filesystem.
}

create_zisofs() {
	rm -rf "$1/zisofs" > /dev/null 2>&1
	echo "Creating zisofs..."
	mkzftree -z 9 -p2 "${clst_destpath}" "$1/zisofs" \
		|| die "Could not run mkzftree, did you emerge zisofs"
}

create_noloop() {
	echo "Copying files for image (no loop)..."
	cp -pPR "${clst_destpath}"/* "$1" \
		|| die "Could not copy files to image (no loop)"
}

create_squashfs() {
	echo "Creating squashfs..."
	export loopname="image.squashfs"
	mksquashfs "${clst_destpath}" "$1/${loopname}" ${clst_fsops} -noappend \
		|| die "mksquashfs failed, did you emerge squashfs-tools?"
}

create_jffs() {
	echo "Creating jffs..."
	export loopname="image.jffs"
	# fs_check /usr/sbin/mkfs.jffs jffs sys-fs/mtd
	mkfs.jffs -d ${clst_destpath} -o $1/${loopname} ${clst_fsops} \
		|| die "Could not create a jffs filesystem"
}

create_jffs2(){
	echo "Creating jffs2..."
	export loopname="image.jffs"
	# fs_check /usr/sbin/mkfs.jffs2 jffs2 sys-fs/mtd
	mkfs.jffs2 --root=${clst_destpath} --output=$1/${loopname} ${clst_fsops} \
		|| die "Could not create a jffs2 filesystem"
}

create_cramfs(){
	echo "Creating cramfs..."
	export loopname="image.cramfs"
	#fs_check /sbin/mkcramfs cramfs sys-fs/cramfs
	mkcramfs ${clst_fsops} ${clst_destpath} $1/${loopname} \
		|| die "Could not create a cramfs filesystem"
}

create_cloud_qcow2() {
	export source_path="${clst_destpath}"
	export destination_path="$1"
	export loopname="image.loop"
	export qcow2name="image.loop"

	echo "Preparing disk..."
	# TODO: auto-shrink
	fallocate -l 5G ${destination_path}/${loopname} \
		|| die "${loopname} creation failure"
	( set -e
	parted -s "${destination_path}/${loopname}" mklabel gpt
	parted -s --align=none "${destination_path}/${loopname}" mkpart bios_boot 0 2M
	parted -s --align=none "${destination_path}/${loopname}" mkpart primary 2M 100%
	parted -s "${destination_path}/${loopname}" set 1 boot on
	parted -s "${destination_path}/${loopname}" set 1 bios_grub on
	) || die "Failed to partition new loopback volume"

	BLOCK_DEV=$(losetup -f --show "${TEMP_DIR}/${TEMP_IMAGE}")
	mkfs.ext4 -m 0 -F ${clst_fsops} "${BLOCK_DEV}p2" \
		|| die "Couldn't create ext4 filesystem"

	install -d ${destination_path}/loopmount
	sync; sync; sleep 3 # Try to work around 2.6.0+ loopback bug
	mount -t ext4 -o acl,user_xattr,delalloc "${BLOCK_DEV}p2" \
		${destination_path}/loopmount \
		|| die "Couldn't mount loopback ext4 filesystem"
	sync; sync; sleep 3 # Try to work around 2.6.0+ loopback bug

	echo "Copying content..."
	cp -pPR ${source_path}/* ${destination_path}/loopmount
	[ $? -ne 0 ] && { umount ${destination_path}/${loopname}; \
		die "Couldn't copy files to loopback ext4 filesystem"; }

	echo 'Installing grub...'
	grub2-install "${BLOCK_DEV}" --boot-directory "${destination_path}/loopmount/boot"

	umount ${destination_path}/loopmount \
		|| die "Couldn't unmount loopback ext4 filesystem"
	rmdir -f ${destination_path}/loopmount \
		|| die "Couldn't remove loopmount point"

	# TODO: apply zerofree to the volume
	# TODO: force an fsck on the volumne

	losetup -d "${BLOCK_DEV}" \
		|| die "Failed to delete block device"

	qemu-img convert -c -f raw -O qcow2 \
		${destination_path}/${loopname} \
		${destination_path}/${qcow2name} \
		|| die "Failed to convert loop to qcow2"
	rm -f ${destination_path}/${loopname}

	# Now, $clst_target_path should contain a usable qcow2 image
}
