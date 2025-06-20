#!/bin/bash

source /tmp/chroot-functions.sh

echo "Setting up grub for also serial console"
cat >> /etc/default/grub <<THISISIT

mydevice="${1}"
enablebios="${2}"
enableefi="${3}"

# Added by catalyst
GRUB_TERMINAL='serial console'
GRUB_SERIAL_COMMAND='serial --speed 115200 --unit=0 --word=8 --parity=no --stop=1'
GRUB_CMDLINE_LINUX="console=ttyS0 console=tty0"
THISISIT

echo "Creating grub configuration"
grub-mkconfig -o /boot/grub/grub.cfg

case ${clst_hostarch} in
	amd64)
		if [[ ${enablebios} == "1" ]]; then
			echo "Installing grub with target i386-pc in ${mydevice}"
			grub-install --target=i386-pc ${mydevice}
		fi
		if [[ ${enableefi} == "1" ]]; then
			echo "Installing grub with target x86_64-efi"
			grub-install --no-floppy --efi-directory=/boot --removable --skip-fs-probe --no-nvram --no-bootsector --target=x86_64-efi
		fi
		;;
	arm64)
		echo "Installing grub with target arm64-efi"
		grub-install --no-floppy --efi-directory=/boot --removable --skip-fs-probe --no-nvram --no-bootsector --target=arm64-efi
		;;
	riscv)
		echo "Installing grub with target riscv64-efi"
		grub-install --no-floppy --efi-directory=/boot --removable --skip-fs-probe --no-nvram --no-bootsector --target=riscv64-efi
		;;
esac
