#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/netboot-image.sh,v 1.3 2004/10/11 14:19:30 zhen Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

export USE="-* netboot"

emerge -k -b --nodeps genext2fs || exit 1

if [ -z "${IMAGE_PATH}" ]
then
	echo "IMAGE_PATH not specified !"
	exit 1
fi

# Install the netboot base system
ROOT=${IMAGE_PATH} emerge -k -b --nodeps netboot-base || exit 1

# Handle all strip calls here
function do_strip() {
	strip --strip-unneeded "$@"
}

# Copy libs of a executable in the chroot
function copy_libs() {
	local ldd file="${1}"
	# Figure out what libraries this file needs
	local libs="$(readelf -d "${file}" | grep '(NEEDED)' | awk '{print $NF}')"

	# Check if it's a dynamix exec, bail if it isnt
	[ -z "${libs}" ] && return 0
    
	for lib in ${libs}
	do
		# readelf shows [libblah.so] so we have to trim []
		lib=${lib:1:${#lib}-2}

		# don't scan the lib if it's already been copied over
		[ -e "${IMAGE_PATH}/lib/${lib}" ] && continue

		# ldd changes output format over time
		ldd="$(ldd "${file}" | grep ${lib})"
		set -- ${ldd}
		for ldd in "${@}" NF
		do
			[ "${ldd:0:1}" == "/" ] && break
		done
	
		if [ "${ldd}" == "NF" ]
	then
			echo "copy_lib: could not locate '${lib}'"
	else
			copy_file ${ldd}
	fi
	done
}
function copy_file() {
	local f="${1}"

	if [ ! -e "${f}" ]
	then
		echo "copy_file: File '${f}' not found"
		return 0
	fi

	if [ -L "${f}" ]
	then
		cp -dp "${f}" "${IMAGE_PATH}/lib/"
		local l="$(readlink "${f}")"
		if [ ! -e "${l}" ]
	then
			l="$(dirname "${f}")/${l}"
		fi
		f="${l}"
	fi
	cp "${f}" "${IMAGE_PATH}/lib/"
	do_strip "${IMAGE_PATH}/lib/$(basename "${f}")"
}

# Copy the files needed in the chroot
loader="$(readelf -a ${IMAGE_PATH}/bin/busybox | grep 'ld-.*so' | awk '{print $NF}')"
copy_file ${loader/]}
copy_libs ${IMAGE_PATH}/bin/busybox
for f in "$@" ; do
	copy_libs ${f}
	copy_file ${f}
done

# Copy the kernel modules over
if [ -d ${GK_BINARIES}/lib ] ; then
	cp -r ${GK_BINARIES}/lib ${IMAGE_PATH}/ || exit 1
fi

# Prune portage stuff
cd ${IMAGE_PATH}
rm -r var/db var/cache

# Create the ramdisk
IMAGE_SIZE=$(du -s -k ${IMAGE_PATH} | cut -f1)
IMAGE_SIZE=$((IMAGE_SIZE + 200))
IMAGE_INODES=$(find ${IMAGE_PATH} | wc -l)
IMAGE_INODES=$((IMAGE_INODES + 100))
genext2fs -q -d "${IMAGE_PATH}" -b ${IMAGE_SIZE} -i ${IMAGE_INODES} /initrd || exit 1
gzip -9f /initrd || exit 1
