#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

. /tmp/chroot-functions.sh

update_env_settings

case ${clst_target} in
	livecd*)
		export USE="livecd"
		run_emerge --oneshot genkernel
		install -d /usr/portage/packages/gk_binaries

		# Setup case structure for livecd_type
		case ${clst_livecd_type} in
			gentoo-release-minimal | gentoo-release-universal)
				case ${clst_mainarch} in
					amd64|x86)
						sed -i 's/initramfs_data.cpio.gz /initramfs_data.cpio.gz -r 1024x768 /' /usr/share/genkernel/genkernel
					;;
				esac
			;;
		esac
	;;


	netboot2)
		run_emerge --oneshot genkernel
		install -d /usr/portage/packages/gk_binaries

		# Set the netboot builddate/hostname in linuxrc & copy to proper arch directory in genkernel
		sed -e "s/@@MYDATE@@/${clst_netboot2_builddate}/g" \
		    -e "s/@@RELVER@@/${clst_version_stamp}/g" \
			${clst_root_path}usr/share/genkernel/netboot/linuxrc.x \
				> ${clst_root_path}usr/share/genkernel/${clst_mainarch}/linuxrc

		echo ">>> Copying support files to ${clst_root_path} ..."
		cp -af ${clst_root_path}usr/share/genkernel/netboot/misc/* ${clst_merge_path}

		echo ">>> Copying busybox config ..."
		cp -f ${clst_netboot2_busybox_config} /usr/share/genkernel/${clst_mainarch}/busy-config
	;;
esac
