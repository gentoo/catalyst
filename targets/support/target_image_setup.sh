#!/bin/bash

source ${clst_shdir}/support/functions.sh

mkdir -p "${1}"

echo "Creating ${clst_fstype} filesystem"
case ${clst_fstype} in
	squashfs)
		gensquashfs -D "${clst_destpath}" -q ${clst_fsops} "${1}/image.squashfs" \
			|| die "Failed to create squashfs filesystem"
	;;
	jffs2)
		mkfs.jffs2 --root="${clst_destpath}" --output="${1}/image.jffs" "${clst_fsops}" \
			|| die "Failed to create jffs2 filesystem"
	;;
esac
