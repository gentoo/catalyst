#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/pre-kmerge.sh,v 1.7 2004/11/02 23:23:16 wolf31o2 Exp $

/usr/sbin/env-update
source /etc/profile

if [ ! -e "/usr/bin/genkernel" ]
then
	emerge -k -b genkernel
fi

install -d /usr/portage/packages/gk_binaries
rm -f /usr/src/linux

sed -i 's/uchi-hcd/uhci-hcd/' /usr/share/genkernel/x86/modules_load
sed -i 's/initramfs_data.cpio.gz /initramfs_data.cpio.gz -r 1024x768 /' /usr/share/genkernel/genkernel
