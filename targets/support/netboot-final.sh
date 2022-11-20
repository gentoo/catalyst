#!/bin/bash

source ${clst_shdir}/support/functions.sh

extract_kernels ${clst_target_path}/boot

# Move kernel binaries to ${clst_target_path}/kernels, and
# move everything else to ${clst_target_path}/kernels/misc
mkdir -p ${clst_target_path}/kernels/misc

for x in ${clst_boot_kernel}; do
	mv ${clst_target_path}/boot/${x} ${clst_target_path}/kernels
	mv ${clst_target_path}/boot/${x}.igz ${clst_target_path}/kernels/misc
	mv ${clst_target_path}/boot/System-${x}.map ${clst_target_path}/kernels/misc
done

rm -f ${clst_target_path}/boot/gentoo-config
rmdir ${clst_target_path}/boot

# Any post-processing necessary for each architecture can be done here.  This
# may include things like sparc's elftoaout, x86's PXE boot, etc.
case ${clst_hostarch} in
	parisc)
		# Only one kernel should be there
		kname=${clst_boot_kernel[0]}
		rm -f ${clst_target_path}/${kname}-hppa.lif

		palo \
			-k ${clst_target_path}/kernels/${kname} \
			-r ${clst_target_path}/kernels/misc/${kname}.igz \
			-s ${clst_target_path}/${kname}-hppa.lif \
			-f /dev/null \
			-b /usr/share/palo/iplboot \
			-c "0/vmlinux initrd=0/ramdisk" \
			|| exit 1

		;;
	sparc*)
		if [[ ${clst_hostarch} == sparc ]]; then
			piggyback=piggyback
		else
			piggyback=piggyback64
		fi
		for x in ${clst_boot_kernel}; do
			elftoaout ${clst_target_path}/kernels/${x} -o ${clst_target_path}/${x}-a.out
			${piggyback} ${clst_target_path}/${x}-a.out ${clst_target_path}/kernels/misc/System-${x}.map ${clst_target_path}/kernels/misc/${x}.igz
		done
		;;
	*)
		echo "Netboot support for ${clst_hostarch} is unimplemented"
		exit 1
	;;
esac
exit $?
