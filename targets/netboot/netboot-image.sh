#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/netboot-image.sh,v 1.2 2004/10/06 16:00:09 zhen Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

IMAGE_PATH=$1
shift
TARBALL=$1
shift

if [ -z "${IMAGE_PATH}" ]
then
	echo "IMAGE_PATH not specified !"
	exit 1
fi

# Required directories
mkdir -vp ${IMAGE_PATH}/bin
mkdir -vp ${IMAGE_PATH}/dev
mkdir -vp ${IMAGE_PATH}/etc
mkdir -vp ${IMAGE_PATH}/mnt/gentoo
mkdir -vp ${IMAGE_PATH}/proc
mkdir -vp ${IMAGE_PATH}/var/log

# Copy libs of a executable in the chroot
function copy_libs() {

	# Check if it's a dynamix exec
	ldd ${1} > /dev/null 2>&1 || return
    
	for lib in `ldd ${1} | awk '{ print $3 }'`
	do
		if [ -e ${lib} ]
		then
			if [ ! -e ${IMAGE_PATH}/${lib} ]
			then
				copy_file ${lib}
				[ -e "${IMAGE_PATH}/${lib}" ] && strip -R .comment -R .note ${IMAGE_PATH}/${lib} || echo "WARNING : Cannot strip lib ${IMAGE_PATH}/${lib} !"
			fi
		else
			echo "WARNING : Some library was not found for ${lib} !"
		fi
	done

}

function copy_symlink() {

	STACK=${2}
	[ "${STACK}" = "" ] && STACK=16 || STACK=$((${STACK} - 1 ))

	if [ ${STACK} -le 0 ] 
	then
		echo "WARNING : ${TARGET} : too many levels of symbolic links !"
		return
	fi

	[ ! -e ${IMAGE_PATH}/`dirname ${1}` ] && mkdir -p ${IMAGE_PATH}/`dirname ${1}`
	[ ! -e ${IMAGE_PATH}/${1} ] && cp -vfdp ${1} ${IMAGE_PATH}/${1}
	
	TARGET=`readlink -f ${1}`
	if [ -h ${TARGET} ]
	then
		copy_symlink ${TARGET} ${STACK}
	else
		copy_file ${TARGET}
	fi

}

function copy_file() {

	f="${1}"

	if [ ! -e "${f}" ]
	then
		echo "WARNING : File not found : ${f}"
		continue
	fi

	[ ! -e ${IMAGE_PATH}/`dirname ${f}` ] && mkdir -p ${IMAGE_PATH}/`dirname ${f}`
	[ ! -e ${IMAGE_PATH}/${f} ] && cp -vfdp ${f} ${IMAGE_PATH}/${f}
	if [ -x ${f} -a ! -h ${f} ]
	then
		copy_libs ${f}
		strip -R .comment -R .note ${IMAGE_PATH}/${f} > /dev/null 2>&1
	elif [ -h ${f} ]
	then
		copy_symlink ${f}
	fi
}

# Copy the files needed in the chroot
copy_libs ${IMAGE_PATH}/bin/busybox

FILES="${@}"
for f in ${FILES}
do
	copy_file ${f}
done

# Copy the kernel modules
[ ! -e ${IMAGE_PATH}/lib ]  && mkdir -p ${IMAGE_PATH}/lib
cp -Rv /lib/modules ${IMAGE_PATH}/lib
#find ${IMAGE_PATH}/lib -name \*.o -o -name \*.ko | xargs strip -R .comment -R .note

# Extract the base tarball
tar xjvf ${TARBALL} -C ${IMAGE_PATH}/

# Unpack the kernel
tar xjvf ${GK_BINARIES}/kernel.tar.bz2 -C /
mv -f /kernel-2.* /kernel

# Create the ramdisk
IMAGE_SIZE=`du -s ${IMAGE_PATH} | awk '{ print $1 }'`

dd if=/dev/zero of=/ramdisk bs=1k count=$((IMAGE_SIZE + 500))

yes | mke2fs /ramdisk

mkdir /ramdisk-loop
mount -o loop ramdisk ramdisk-loop
cp -R ${IMAGE_PATH}/* /ramdisk-loop
umount /ramdisk-loop
rmdir /ramdisk-loop
