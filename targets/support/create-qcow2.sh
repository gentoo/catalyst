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
: "${clst_qcow2_size:=20GiB}"
: "${clst_qcow2_efisize:=512MiB}"
: "${clst_qcow2_roottype:=xfs}"

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
qemu-img create -f qcow2 "${1}.tmp.qcow2" ${clst_qcow2_size} || die "Cannot create qcow2 file"

# connect the qcow2 file to a network block device
# TODO: find next free device
modprobe -q nbd
mydevice=/dev/nbd0
qemu-nbd -c ${mydevice} -f qcow2 "${1}.tmp.qcow2" || die "Cannot connect qcow2 file to nbd0"

# create a GPT disklabel
parted -s ${mydevice} mklabel gpt || die "Cannot create disklabel"

# create an EFI boot partition
parted -s ${mydevice} -- mkpart efi fat32 1M ${clst_qcow2_efisize} || die "Cannot create EFI partition"
# mark it as EFI boot partition
parted -s ${mydevice} -- type 1 C12A7328-F81F-11D2-BA4B-00A0C93EC93B || die "Cannot set EFI partition UUID"
# note down name
mypartefi=${mydevice}p1

# create the root partition
parted -s ${mydevice} -- mkpart root ${clst_qcow2_roottype} ${clst_qcow2_efisize}GiB -1M || die "Cannot create root partition"
# mark it as generic linux filesystem partition
parted -s ${mydevice} -- type 2 0FC63DAF-8483-4772-8E79-3D69D8477DE4 || die "Cannot set root partition UUID"
# note down name
mypartroot=${mydevice}p2

# re-read the partition table
partprobe ${mydevice} || die "Probing partition table failed"

# make a vfat filesystem in p1
mkfs.fat -F 32 ${mypartefi} || die "Formatting EFI partition failed"

# make an xfs filesystem in p2
mkfs.xfs ${mypartroot} || die "Formatting root partition failed"

# mount things
# we need a mount point- how do we get one?
mymountpoint="${1}.tmp.mnt"
mkdir -p "${mymountpoint}" || die "Could not create root mount point"
mount ${mypartroot} "${mymountpoint}" || die "Could not mount root partition"
mkdir -p "${mymountpoint}"/boot || die "Could not create boot mount point"
mount ${mypartefi} "${mymountpoint}/boot" || die "Could not mount boot partition"

# copy contents in - do we need extra preserve steps? rsync? tar?
cp -a "${clst_target_path}"/* "${mymountpoint}/" || die "Could not copy content into mounted image"

# at this point we have a working system

# create a CONTENTS.gz file
pushd "${mymountpoint}" || die "Could not cd into mountpoint"
find . > "${1}.CONTENTS" || die "Could not list files in mountpoint"
popd || die "Could not cd out of mountpoint"
gzip "${1}.CONTENTS" || die "Could not compress file list"

# note: the following must already have been done by the stage2:
# - rudimentary configuration
# - installation of cloud-init
# - installation of kernel
# - installation of fallback efi loader
# - enabling of services
# luckily efi requires no image magic, just regular files...

# unmount things
umount "${mymountpoint}/boot" || die "Could not unmount boot partition"
umount "${mymountpoint}" || die "Could not unmount root partition"

# disconnect the nbd
qemu-nbd -d ${mydevice} || die "Could not disconnect nbd0"

# rewrite with stream compression
qemu-img convert -c -O qcow2 "${1}.tmp.qcow2" "${1}" || die "Could not compress QCOW2 file"

# clean up
rm "${1}.tmp.qcow2" || die "Could not delete uncompressed QCOW2 file"
rmdir "${mymountpoint}/boot" || die "Could not remove boot mountpoint"
rmdir "${mymountpoint}" || die "Could not remove root mountpoint"

# Finished...
