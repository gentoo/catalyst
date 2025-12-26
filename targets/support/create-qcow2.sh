#!/bin/bash

source ${clst_shdir}/support/functions.sh

## START RUNSCRIPT

# Supported host architectures: all that do UEFI boot and support the tools
# Script parameters:
#  - ${1}  output qcow2 file

#
# Configuration parameters:
# All sizes are in forms as understood by parted: use MiB, GiB, ... or M, G, ...
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

mymountpoint="${1}.tmp.mnt"
myqcow2="${1}"

# TODO: find next free device
modprobe -q nbd
mydevice=/dev/nbd0

# This script requires slightly more stringent cleanup in case of errors
# from the moment on when the nbd was set up...
qcow2die() {
	echo "Something went wrong: $@"
	echo "Cleaning up..."

	# here we just ignore errors
	umount -R "${mymountpoint}/proc"
	umount -R "${mymountpoint}/sys"
	umount -R "${mymountpoint}/dev"
	umount -R "${mymountpoint}/run"

	umount "${mydevice}p1"
	umount "${mydevice}p2"
	qemu-nbd -d "${mydevice}"

	die "Caught error: $@"
}

# We need a means to execute a script inside the qcow with filesystems mounted
# Which means reproducing half of catalyst here.
exec_in_qcow2() {
	local file_name=$(basename ${1})

	# prepare qcow2 for chrooting
	mount --types proc /proc "${mymountpoint}/proc"
	mount --rbind /sys "${mymountpoint}/sys"
	mount --make-rslave "${mymountpoint}/sys"
	mount --rbind /dev "${mymountpoint}/dev"
	mount --make-rslave "${mymountpoint}/dev"
	mount --bind /run "${mymountpoint}/run"
	mount --make-slave "${mymountpoint}/run"

	# copy_to_chroot ${1}
	cp -pPR "${1}" "${mymountpoint}/tmp" || qcow2die
        # copy_to_chroot ${clst_shdir}/support/chroot-functions.sh
        cp -pPR "${clst_shdir}/support/chroot-functions.sh" "${mymountpoint}/tmp" || qcow2die

        # Ensure the file has the executable bit set
        chmod +x "${mymountpoint}/tmp/${file_name}" || qcow2die

	# Copy binary interpreter
	if [[ -n "${clst_interpreter}" ]] ; then
		echo "clst_interpreter is \"${clst_interpreter}\""
		for myfile in ${clst_interpreter} ; do
			cp -pv "${myfile}" "${mymountpoint}/${myfile}" || qcow2die
		done
	fi

        echo "Running ${file_name} in qcow2:"
        echo "    ${clst_CHROOT} ${mymountpoint} /tmp/${file_name}"
        ${clst_CHROOT} "${mymountpoint}" "/tmp/${file_name}" || qcow2die

	# Remove binary interpreter
	if [[ -n "${clst_interpreter}" ]] ; then
		for myfile in ${clst_interpreter} ; do
			rm -v "${mymountpoint}/${myfile}" || qcow2die
		done
	fi

        rm -f "${mymountpoint}/tmp/${file_name}" || qcow2die
        rm -f "${mymountpoint}/tmp/chroot-functions.sh" || qcow2die

	# cleanup qcow2 dir
	umount -R "${mymountpoint}/proc" || qcow2die
	umount -R "${mymountpoint}/sys" || qcow2die
	umount -R "${mymountpoint}/dev" || qcow2die
	umount -R "${mymountpoint}/run" || qcow2die
}


echo "Creating a new qcow2 disk image file ${myqcow2}.tmp.qcow2 with size ${clst_qcow2_size/%iB/}"
qemu-img create -f qcow2 "${myqcow2}.tmp.qcow2" ${clst_qcow2_size/%iB/} || die "Cannot create qcow2 file"

echo "Connecting the qcow2 file to network block device ${mydevice}"
qemu-nbd -c ${mydevice} -f qcow2 "${myqcow2}.tmp.qcow2" || die "Cannot connect qcow2 file to nbd0"

echo "Waiting 5s to ensure device ${mydevice} is set up"
sleep 5s

echo "Creating a GPT disklabel"
parted -s ${mydevice} mklabel gpt 2>&1 || qcow2die "Cannot create disklabel"

echo "Creating an EFI boot partition"
parted -s ${mydevice} -- mkpart gentooefi fat32 1M ${clst_qcow2_efisize} || qcow2die "Cannot create EFI partition"
# mark it as EFI boot partition
parted -s ${mydevice} -- type 1 C12A7328-F81F-11D2-BA4B-00A0C93EC93B || qcow2die "Cannot set EFI partition UUID"
# note down name
mypartefi=${mydevice}p1

echo "Creating the root partition"
parted -s ${mydevice} -- mkpart gentooroot ${clst_qcow2_roottype} ${clst_qcow2_efisize}GiB -1M || qcow2die "Cannot create root partition"
# mark it as generic linux filesystem partition
parted -s ${mydevice} -- type 2 0FC63DAF-8483-4772-8E79-3D69D8477DE4 || qcow2die "Cannot set root partition UUID"
# note down name
mypartroot=${mydevice}p2

echo "Re-reading the partition table"
partprobe ${mydevice} || qcow2die "Probing partition table failed"

echo "Printing the partition table"
parted -s ${mydevice} -- print || qcow2die "Printing the partition table failed"

echo "Waiting 5s to ensure the partition device nodes exist"
sleep 5s

echo "Making a vfat filesystem in p1"
mkfs.fat -v -F 32 -n gentooefi ${mypartefi} || qcow2die "Formatting EFI partition failed"

echo "Making an xfs filesystem in p2"
# nrext64=0 is needed for compatibility with 5.15 kernels
mkfs.xfs -i nrext64=0 -L gentooroot ${mypartroot} || qcow2die "Formatting root partition failed"

echo "Printing blkid output"
blkid ${mydevice}* || qcow2die "blkid failed"

echo "Mounting things at ${mymountpoint}"
mkdir -p "${mymountpoint}" || qcow2die "Could not create root mount point"
mount ${mypartroot} "${mymountpoint}" || qcow2die "Could not mount root partition"
mkdir -p "${mymountpoint}"/boot || qcow2die "Could not create boot mount point"
mount ${mypartefi} "${mymountpoint}/boot" || qcow2die "Could not mount boot partition"

# copy contents in; the source is the stage dir and not any "iso content"
echo "Copying files into the mounted directories from ${clst_stage_path}"
cp -a "${clst_stage_path}"/* "${mymountpoint}/" || qcow2die "Could not copy content into mounted image"

echo "Adding FEATURES=binpkg-request-signature to make.conf"
echo '# Ensure that binary package signatures are verified' >> "${mymountpoint}/etc/portage/make.conf" || qcow2die "Could not modify make.conf"
echo 'FEATURES="binpkg-request-signature"' >> "${mymountpoint}/etc/portage/make.conf" || qcow2die "Could not modify make.conf"

echo "Setting machine-id to empty"
# We are already running systemd-firstboot in a previous step, so we don't want to run it again.
# The documented behaviour for an empty machine-id is that systemd generates a new one and commits
# it on first boot, but otherwise treats the system as already initialized.
rm -f "${mymountpoint}/etc/machine-id"
touch "${mymountpoint}/etc/machine-id" || qcow2die "Could not set machine-id to empty"

# now we can chroot in and install grub
exec_in_qcow2 "${clst_shdir}/support/qcow2-grub-install.sh"

echo "Generating /etc/fstab"
cat > "${mymountpoint}/etc/fstab" <<END
# /etc/fstab: static file system information.
#
# See the manpage fstab(5) for more information.
#
# <fs>                  <mountpoint>    <type>          <opts>          <dump/pass>

LABEL=gentooroot            /               xfs              noatime,rw   0 1
LABEL=gentooefi             /boot           vfat             defaults     1 2

END

echo "Creating a CONTENTS file ${myqcow2}.CONTENTS"
pushd "${mymountpoint}/" &> /dev/null || qcow2die "Could not cd into mountpoint"
ls -laR > "${myqcow2}.CONTENTS"       || qcow2die "Could not create CONTENTS file"
popd &> /dev/null                     || qcow2die "Could not cd out of mountpoint"

echo "Compressing the CONTENTS file"
gzip "${myqcow2}.CONTENTS"      || qcow2die "Could not compress the CONTENTS file"

echo "Unmounting things"
umount "${mymountpoint}/boot" || qcow2die "Could not unmount boot partition"
umount "${mymountpoint}" || qcow2die "Could not unmount root partition"

echo "Disconnecting ${mydevice}"
qemu-nbd -d ${mydevice} || qcow2die "Could not disconnect ${mydevice}"

echo "Rewriting the qcow2 file with stream compression to ${myqcow2}"
qemu-img convert -c -O qcow2 "${myqcow2}.tmp.qcow2" "${myqcow2}" || qcow2die "Could not compress QCOW2 file"

echo "Cleaning up"
rm "${myqcow2}.tmp.qcow2" || qcow2die "Could not delete uncompressed QCOW2 file"
rmdir "${mymountpoint}" || qcow2die "Could not remove mountpoint"

# Finished...
