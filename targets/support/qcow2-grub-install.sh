#!/bin/bash

source /tmp/chroot-functions.sh

case ${clst_hostarch} in
	amd64)
		echo "Installing grub with target x86_64-efi"
		grub-install --no-floppy --efi-directory=/boot --removable --skip-fs-probe --no-nvram --no-bootsector --target=x86_64-efi
		;;
	arm64)
		echo "Installing grub with target arm64-efi"
		grub-install --no-floppy --efi-directory=/boot --removable --skip-fs-probe --no-nvram --no-bootsector --target=arm64-efi
		;;
esac

echo "Creating grub configuration"
grub-mkconfig -o /boot/grub/grub.cfg
