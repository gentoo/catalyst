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
export clst_qcow2_size=20
export clst_qcow2_swapsize=0
export clst_qcow2_efisize=0.5
export clst_qcow2_roottype=xfs

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
qemu-nbd -c /dev/nbd0 -f qcow2 ${1} || die "Cannot connect qcow2 file to nbd0"

# create a GPT disklabel
parted -s /dev/nbd0 mklabel gpt || die "Cannot create disklabel"

# create an EFI boot partition
parted -s /dev/nbd0 -- mkpart efi fat32 1M {clst_qcow2_efisize}GiB || die "Cannot create EFI partition"
# mark it as such

# if requested, create a swap partition
# mark it as such

# fill the rest of the image with the root partition
parted -s /dev/nbd0 -- mkpart root ${clst_qcow2_roottype} ${clst_qcow2_efisize}GiB -1M || die "Cannot create root partition"
# mark it as such

# re-read the partition table
partprobe /dev/nbd0 || die "Probing partition table failed"

# make a vfat filesystem in p1
mkfs.fat -F 32 /dev/nbd0p1 || die "Formatting EFI partition failed"

# make a swap signature in p2

# make a xfs filesystem in p3 (or p2 if no swap)
mkfs.xfs /dev/nbd0p2 || die "Formatting root partition failed"

# mount things
# we need a mount point- how do we get one?
my_mountpoint=/tmp/bla
mkdir -p "${my_mountpoint}" || die "Could not create mount point"
mount /dev/nbd0p2 "${my_mountpoint}" || die "Could not mount root partition"
mount /dev/nbd0p1 "${my_mountpoint}/boot" || die "Could not mount boot partition"

# copy contents in
cp -a "${clst_target_path}"/* "${my_mountpoint}/"

# at this point we have a rudimentary working system
# now we need to follow the handbook and do some basic configuration
# (locale, timezone, ssh) - though most of it will be done by cloud-init


# now let's install an efi loader inside
# bootctl --no-variables --graceful install

# unmount things
umount "${my_mountpoint}/boot" || die "Could not unmount boot partition"
umount "${my_mountpoint}" || die "Could not unmount root partition"

# disconnect the nbd
qemu-nbd -d /dev/nbd0 || die "Could not disconnect nbd0"

# Finished...
