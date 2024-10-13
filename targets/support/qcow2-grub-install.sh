#!/bin/bash

source /tmp/chroot-functions.sh

echo "Installing grub with target x86_64-efi"
grub-install --no-floppy --efi-directory=/boot --removable --skip-fs-probe --no-nvram --no-bootsector --target=x86_64-efi

echo "Creating grub configuration"
grub-mkconfig -o /boot/grub/grub.cfg
