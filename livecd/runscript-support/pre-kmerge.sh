#!/bin/bash
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/pre-kmerge.sh,v 1.4 2004/10/12 18:01:22 zhen Exp $

/usr/sbin/env-update
source /etc/profile

if [ ! -e "/usr/bin/genkernel" ]
then
	emerge -k -b genkernel
fi

install -d /usr/portage/packages/gk_binaries
rm -f /usr/src/linux
