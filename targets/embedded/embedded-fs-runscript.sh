#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

die() {
	echo "$1"
	exit 1
}

# 1 = mkfs path, 2 = fs name, 3 = pkg name
fs_check() {
    if [ ! -e ${1} ]; then
	die "You must install ${3} in order to produce ${2} images"
    fi
}

case $1 in
    jffs)
	fs_check /usr/sbin/mkfs.jffs jffs sys-fs/mtd
	mkfs.jffs -d ${root_fs_path} -o ${clst_image_path}/root.img \
	    ${clst_embedded_fsops} || die "Could not create a jffs filesystem"
	;;
    jffs2)
	fs_check /usr/sbin/mkfs.jffs2 jffs2 sys-fs/mtd
	mkfs.jffs2 --root=${root_fs_path} --output=${clst_image_path}/root.img\
	    ${clst_embedded_fsops} || die "Could not create a jffs2 filesystem"
	;;

    cramfs)
	fs_check /sbin/mkcramfs cramfs sys-fs/cramfs
	mkcramfs ${clst_embedded_fsops} ${root_fs_path} \
	    ${clst_image_path}/root.img || die "Could not create a cramfs filesystem"
	;;

    squashfs)
	fs_check /usr/sbin/mksquashfs squashfs sys-fs/squashfs-tools
	mksquashfs ${root_fs_path} ${clst_image_path}/root.img \
	    ${clst_embedded_fsops} || die "Could not create a squashfs filesystem"
	;;
    *)
	;;
esac
