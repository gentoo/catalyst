#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

/usr/sbin/env-update
source /etc/profile

CONFIG_PROTECT="-*" USE="livecd" emerge --oneshot --nodeps -u genkernel 

install -d /usr/portage/packages/gk_binaries

sed -i 's/uchi-hcd/uhci-hcd/' /usr/share/genkernel/x86/modules_load

# Setup case structure for livecd_type
case ${clst_livecd_type} in
	gentoo-release-minimal | gentoo-release-universal)
		sed -i 's/initramfs_data.cpio.gz /initramfs_data.cpio.gz -r 1024x768 /' /usr/share/genkernel/genkernel
	;;
esac

