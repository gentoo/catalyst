#!/bin/bash

source ${clst_shdir}/support/functions.sh

mkdir -p "${1}"

echo "Creating ${clst_fstype} filesystem"
case ${clst_fstype} in
	squashfs)
		gensquashfs -k -D "${clst_stage_path}" -q ${clst_fsops} "${1}/image.squashfs" \
			|| die "Failed to create squashfs filesystem"
	;;
	jffs2)
		mkfs.jffs2 --root="${clst_stage_path}" --output="${1}/image.jffs" "${clst_fsops}" \
			|| die "Failed to create jffs2 filesystem"
	;;
esac
