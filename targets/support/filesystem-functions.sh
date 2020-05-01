#!/bin/bash

# Dont forget to update functions.sh  check_looptype
# $1 is the target directory for the filesystem

create_squashfs() {
	echo "Creating squashfs..."
	export loopname="image.squashfs"
	gensquashfs -D "${clst_destpath}" -q ${clst_fsops} "$1/${loopname}" \
		|| die "gensquashfs failed, did you emerge squashfs-tools-ng?"
}

create_jffs2(){
	echo "Creating jffs2..."
	export loopname="image.jffs"
	# fs_check /usr/sbin/mkfs.jffs2 jffs2 sys-fs/mtd
	mkfs.jffs2 --root=${clst_destpath} --output=$1/${loopname} ${clst_fsops} \
		|| die "Could not create a jffs2 filesystem"
}
