#!/bin/bash

source ${clst_shdir}/support/functions.sh

# $1 is the destination root

if [[ -n ${clst_cdtar} ]]; then
	extract_cdtar $1
fi

extract_kernels $1/boot

cmdline_opts=()

# Add any additional options
if [ -n "${clst_qcow2_bootargs}" ]
then
	for x in ${clst_qcow2_bootargs}
	do
		cmdline_opts+=(${x})
	done
fi

# Optional memtest setups
memtest_grub() {
  if [[ -e $1/memtest.efi64 ]]; then
    echo 'if [ "x$grub_platform" = xefi ]; then'
    echo '  menuentry "Memtest86+ 64bit UEFI" {'
    echo '    chainloader "/memtest.efi64"'
    echo '  }'
    echo 'fi'
  fi
}

default_append_line=(${cmdline_opts[@]})
default_dracut_append_line=(${clst_qcow2_bootargs})

case ${clst_hostarch} in
	amd64|arm64|ppc64*)
		kern_subdir=/boot
		iacfg=$1/boot/grub/grub.cfg
		mkdir -p $1/boot/grub
		echo 'set default=0' > ${iacfg}
		echo 'set gfxpayload=keep' >> ${iacfg}
		echo 'set timeout=10' >> ${iacfg}
		echo 'insmod all_video' >> ${iacfg}
		echo '' >> ${iacfg}
		for x in ${clst_boot_kernel}
		do
			eval "kernel_console=\$clst_boot_kernel_${x}_console"
			eval "distkernel=\$clst_boot_kernel_${x}_distkernel"

			echo "menuentry 'Boot Gentoo image (kernel: ${x})' --class gnu-linux --class os {"  >> ${iacfg}
			if [ ${distkernel} = "yes" ]
			then
				# FIXME: what can we search for here?
				echo "	search --no-floppy --set=root -l ${clst_iso_volume_id}" >> ${iacfg}
				echo "	linux ${kern_subdir}/${x} ${default_dracut_append_line[@]}" >> ${iacfg}
			else
				echo "	linux ${kern_subdir}/${x} ${default_append_line[@]}" >> ${iacfg}
			fi
			echo "	initrd ${kern_subdir}/${x}.igz" >> ${iacfg}
			echo "}" >> ${iacfg}
			echo "" >> ${iacfg}
		done
		memtest_grub $1 >> ${iacfg}
	;;
esac
exit $?
