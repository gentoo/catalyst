#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/netboot-image.sh,v 1.4 2005/01/11 15:22:41 zhen Exp $

/usr/sbin/env-update
source /etc/profile

if [ -f /tmp/envscript ]
then
	source /tmp/envscript
	rm -f /tmp/envscript
fi

#IMAGE_PATH=$1
#shift
#TARBALL=$1
#shift

if [ -z "${IMAGE_PATH}" ]
then
	echo "IMAGE_PATH not specified !"
	exit 1
fi

# Install the netboot base system
ROOT=${IMAGE_PATH} emerge -k -b --nodeps netboot-base || exit 1

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

# Copy the kernel modules over
if [ -d ${GK_BINARIES}/lib ] ; then
	cp -r ${GK_BINARIES}/lib ${IMAGE_PATH}/ || exit 1
fi

# Prune portage stuff
cd ${IMAGE_PATH}
rm -r var/db var/cache

# Create the ramdisk
emerge -k -b genext2fs
IMAGE_SIZE=$(du -s -k ${IMAGE_PATH} | cut -f1)
IMAGE_SIZE=$((IMAGE_SIZE + 500))
IMAGE_INODES=$(find ${IMAGE_PATH} | wc -l)
IMAGE_INODES=$((IMAGE_INODES + 100))
genext2fs -q -d "${IMAGE_PATH}" -b ${IMAGE_SIZE} -i ${IMAGE_INODES} /initrd || exit 1
gzip -9f /initrd || exit 1
