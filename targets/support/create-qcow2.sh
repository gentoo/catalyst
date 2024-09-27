#!/bin/bash

source ${clst_shdir}/support/functions.sh

## START RUNSCRIPT

# Supported host architectures: all that do UEFI boot and support the tools
# Script parameters:
#  - ${1}  output qcow2 file

#
# Configuration parameters:
#  - clst_qcow2_size      (internal) size of the qcow2 image (GByte, default 20)
#  - clst_qcow2_swapsize  size of the swap partition (GByte, default 0 = no partition)
#  - clst_qcow2_efisize   size of the EFI boot partition (GByte, default 0.5)
#  - clst_qcow2_roottype  type of the root partition (default xfs)
#

#
# We only support one set of tools, based on
#  - mkfs.vfat    ( sys-fs/dosfstools , for the EFI partition )
#  - mkfs.xfs     ( sys-fs/xfsprogs , this might actually be configurable )
#  - parted       ( sys-block/parted , for partitioning )
#  - qemu-nbd     ( app-emulation/qemu , for accessing a qcow2 image file as device )
#  - qemu-img     ( app-emulation/qemu , for creating a qcow2 image file )
#
# Let's assume these are deps of catalyst and thus present.
#


# create a new qcow2 disk image file
qemu-img create -f qcow2 ${1} ${clst_qcow2_size}G || die "Cannot create qcow2 file"

# connect the qcow2 file to a network block device
# TODO: find next free device
modprobe -q nbd
qemu-nbd -c /dev/nbd0 -f qcow2 ${1} || die "Cannot connect qcow2 file to nbd"

# create a GPT disklabel
parted /dev/nbd0 mklabel gpt

# create an EFI boot partition

# if requested, create a swap partition

# fill the rest of the image with the root partition

# re-read the partition table
partprobe /dev/nbd0

# make a vfat filesystem in p1
# /dev/nbd0p1

# make a swap signature in p2

# make a xxx filesystem in p3 (or p2 if no swap)

# mount things

# copy contents in

# at this point we have a rudimentary working system
# now we need to follow the handbook and do basic configuration
# (locale, timezone, ssh)








# old stuff



# Here we actually create the ISO images for each architecture
case ${clst_hostarch} in
	amd64|arm64|ia64|ppc*|powerpc*|sparc*|x86|i?86)
		isoroot_checksum

		extra_opts=("-joliet" "-iso-level" "3")
		case ${clst_hostarch} in
		sparc*) extra_opts+=("--sparc-boot") ;;
		esac

		echo ">> Running grub-mkrescue to create iso image...."
		grub-mkrescue --mbr-force-bootable -volid "${clst_iso_volume_id}" "${extra_opts[@]}" -o "${1}" "${clst_target_path}"
	;;
esac
exit  $?
