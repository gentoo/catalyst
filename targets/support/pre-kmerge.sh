#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

/usr/sbin/env-update
source /etc/profile



#if [ "${clst_AUTORESUME}" = "1" -a -e /tmp/.clst_genkernel -a -e "/usr/bin/genkernel" ]
#then
#    echo "Autoresume point found not emerging genkernel"
#else
#    emerge --oneshot --nodeps -b -k genkernel && touch /tmp/.clst_genkernel || exit 1
#fi

CONFIG_PROTECT="-*" USE="livecd" emerge --oneshot --nodeps -u genkernel 

install -d /usr/portage/packages/gk_binaries

sed -i 's/uchi-hcd/uhci-hcd/' /usr/share/genkernel/x86/modules_load

if [ "${clst_livecd_type}" = "gentoo-release-minimal" -o \
        "${clst_livecd_type}" = "gentoo-release-universal" ]; then
               sed -i 's/initramfs_data.cpio.gz /initramfs_data.cpio.gz -r 1024x768 /'\
               /usr/share/genkernel/genkernel
fi
