#!/bin/bash

copy_to_chroot() {
	local src="${1}"
	local dst="${clst_chroot_path}/${2:-/tmp}"
	cp -pPR "${src}" "${dst}"
}

delete_from_chroot() {
	rm -f "${clst_chroot_path}/${1}"
}

# Takes the full path to the source file as its argument
# copies the file to the /tmp directory of the chroot
# and executes it.
exec_in_chroot() {
	local file_name=$(basename ${1})

	copy_to_chroot ${1}
	shift
	copy_to_chroot ${clst_shdir}/support/chroot-functions.sh

	# Ensure the file has the executable bit set
	chmod +x ${clst_chroot_path}/tmp/${file_name}

	echo "Running ${file_name} in chroot:"
	echo "    ${clst_CHROOT} ${clst_chroot_path} /tmp/${file_name}"
	${clst_CHROOT} "${clst_chroot_path}" "/tmp/${file_name}" "${@}" || exit 1

	delete_from_chroot /tmp/${file_name}
	delete_from_chroot /tmp/chroot-functions.sh
}

die() {
	echo "$1"
	exit 1
}

extract_cdtar() {
	# Create a filesystem tree for the ISO at
	# $clst_target_path. We extract the "cdtar" to this directory,
	# which will normally contains a pre-built binary
	# boot-loader/filesystem skeleton for the ISO.
	tar -I lbzip2 -xpf ${clst_cdtar} -C $1 || die "Couldn't extract cdtar ${cdtar}"
}

extract_kernels() {
	# extract multiple kernels
	# $1 = Destination
	# ${clst_target_path}/kernel is often a good choice for ${1}

	# Takes the relative desination dir for the kernel as an arguement
	# i.e boot
	[ -z "$clst_boot_kernel" ] && \
		die "Required key boot/kernel not defined, exiting"
	# install the kernels built in kmerge.sh
	for x in ${clst_boot_kernel}
	do
		first=${first:-""}
		kbinary="${clst_chroot_path}/tmp/kerncache/${x}-kernel-initrd-${clst_version_stamp}.tar.bz2"
		if [ -z "${first}" ]
		then
			# grab name of first kernel
			export first="${x}"
		fi

		[ ! -e "${kbinary}" ] && die "Can't find kernel tarball at ${kbinary}"
		mkdir -p ${1}/
		tar -I lbzip2 -xf ${kbinary} -C ${1}/

		# change config name from "config-*" to "gentoo-config", for example
		mv ${1}/config-* ${1}/${x}-config

		# change kernel name from "kernel" to "gentoo", for example
		if [ -e ${1}/kernel-* ]
		then
			mv ${1}/kernel-* ${1}/${x}
		fi
		if [ -e ${1}/kernelz-* ]
		then
			mv ${1}/kernelz-* ${1}/${x}
		fi
		if [ -e ${1}/vmlinuz-* ]
		then
			mv ${1}/vmlinuz-* ${1}/${x}
		fi
		if [ -e ${1}/vmlinux-* ]
		then
			mv ${1}/vmlinux-* ${1}/${x}
		fi

		# change initrd name from "initrd" to "gentoo.igz", for example
		if [ -e ${1}/initrd-* ]
		then
			mv ${1}/initrd-* ${1}/${x}.igz
		fi
		if [ -e ${1}/initramfs-* ]
		then
			mv ${1}/initramfs-* ${1}/${x}.igz
		fi

		# rename "System.map" to "System-gentoo.map", for example
		if [ -e ${1}/System.map-* ]
		then
			mv ${1}/System.map-* ${1}/System-${x}.map
		fi
	done
}

extract_modules() {
	# $1 = Destination
	# $2 = kname
	kmodules="${clst_chroot_path}/tmp/kerncache/${2}-modules-${clst_version_stamp}.tar.bz2"

	if [ -f "${kmodules}" ]
	then
		mkdir -p ${1}/
		tar -I lbzip2 -xf ${kmodules} --strip-components 1 -C ${1}/lib lib
	else
		echo "Can't find kernel modules tarball at ${kmodules}.  Skipping...."
	fi
}
