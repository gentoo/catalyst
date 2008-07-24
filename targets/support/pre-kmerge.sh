#!/bin/bash

source /tmp/chroot-functions.sh

run_merge --oneshot genkernel
install -d /tmp/kerncache

case ${clst_target} in
	netboot2)
		# Set the netboot builddate/hostname in linuxrc and copy to proper arch
		# directory in genkernel
		sed -e "s/@@MYDATE@@/$(date '+%Y%m%d')/g" \
		    -e "s/@@RELVER@@/${clst_version_stamp}/g" \
			/usr/share/genkernel/netboot/linuxrc.x \
			> /usr/share/genkernel/${clst_hostarch}/linuxrc

		echo ">>> Copying support files to ${clst_root_path} ..."
		cp -pPRf /usr/share/genkernel/netboot/misc/* \
			${clst_merge_path}

		echo ">>> Copying busybox config ..."
		cp -f /tmp/busy-config \
			/usr/share/genkernel/${clst_hostarch}/busy-config
	;;
esac
