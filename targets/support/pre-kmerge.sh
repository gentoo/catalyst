#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

if [ -n "${clst_FETCH}" ]
then
	export clst_myemergeopts="${clst_myemergeopts} -f"
fi

case ${clst_target} in
	livecd*|stage4)
		export USE="livecd"
		run_emerge --oneshot genkernel
		install -d /tmp/kerncache

		# Setup case structure for livecd_type
		case ${clst_livecd_type} in
			gentoo-release-minimal | gentoo-release-universal)
				case ${clst_hostarch} in
					amd64|x86)
						sed -i 's/initramfs_data.cpio.gz /initramfs_data.cpio.gz -r 1024x768 /' /usr/share/genkernel/genkernel
					;;
				esac
			;;
		esac
	;;


	netboot2)
		run_emerge --oneshot genkernel
		install -d /tmp/kerncache

		# Set the netboot builddate/hostname in linuxrc and copy to proper arch
		# directory in genkernel
		sed -e "s/@@MYDATE@@/${clst_netboot2_builddate}/g" \
		    -e "s/@@RELVER@@/${clst_version_stamp}/g" \
			${clst_root_path}usr/share/genkernel/netboot/linuxrc.x \
				> ${clst_root_path}usr/share/genkernel/${clst_hostarch}/linuxrc

		echo ">>> Copying support files to ${clst_root_path} ..."
		cp -pPRf ${clst_root_path}usr/share/genkernel/netboot/misc/* \
			${clst_merge_path}

		echo ">>> Copying busybox config ..."
		cp -f ${clst_root_path}usr/share/genkernel/${clst_hostarch}/nb-busybox.cf \
			${clst_root_path}usr/share/genkernel/${clst_hostarch}/busy-config
	;;
esac
