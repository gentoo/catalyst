#!/bin/bash

source ${clst_shdir}/support/functions.sh

## START RUNSCRIPT

# Supported host architectures: all that do UEFI boot and support the tools
# Script parameters:
#  - ${1}  output qcow2 file

#
# Configuration parameters:
#  (All sizes are in forms as understood by parted and qemu-img)
#  - clst_qcow2_size      (internal) size of the qcow2 image (default 20GiB)
#  - clst_qcow2_efisize   size of the EFI boot partition (default 512MiB)
#  - clst_qcow2_roottype  type of the root partition (default xfs)
#
export clst_qcow2_size=20GiB
export clst_qcow2_efisize=512MiB
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
# mark it as EFI boot partition
parted -s /dev/nbd0 -- type 1 C12A7328-F81F-11D2-BA4B-00A0C93EC93B || die "Cannot set EFI partition UUID"
# note down name
mypartefi=/dev/nbd0p1

# create the root partition
parted -s /dev/nbd0 -- mkpart root ${clst_qcow2_roottype} ${clst_qcow2_efisize}GiB -1M || die "Cannot create root partition"
# mark it as generic linux filesystem partition
parted -s /dev/nbd0 -- type 2 0FC63DAF-8483-4772-8E79-3D69D8477DE4 || die "Cannot set root partition UUID"
# note down name
mypartroot=/dev/nbd0p2

# re-read the partition table
partprobe /dev/nbd0 || die "Probing partition table failed"

# make a vfat filesystem in p1
mkfs.fat -F 32 ${mypartefi} || die "Formatting EFI partition failed"

# make an xfs filesystem in p2
mkfs.xfs ${mypartroot} || die "Formatting root partition failed"

# mount things
# we need a mount point- how do we get one?
mymountpoint=/tmp/bla
mkdir -p "${mymountpoint}" || die "Could not create root mount point"
mount /dev/nbd0p2 "${mymountpoint}" || die "Could not mount root partition"
mkdir -p "${mymountpoint}"/boot || die "Could not create boot mount point"
mount /dev/nbd0p1 "${mymountpoint}/boot" || die "Could not mount boot partition"

# copy contents in
cp -a "${clst_target_path}"/* "${my_mountpoint}/"

# at this point we have a working system

# note: the following must already have been done by the stage2:
# - rudimentary configuration
# - installation of cloud-init
# - installation of kernel
# - installation of fallback efi loader
# luckily efi requires no image magic, just regular files...

# unmount things
umount "${mymountpoint}/boot" || die "Could not unmount boot partition"
umount "${mymountpoint}" || die "Could not unmount root partition"

# disconnect the nbd
qemu-nbd -d /dev/nbd0 || die "Could not disconnect nbd0"

# Finished...
