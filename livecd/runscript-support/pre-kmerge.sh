#!/bin/bash
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/pre-kmerge.sh,v 1.3 2004/09/08 15:58:12 zhen Exp $

/usr/sbin/env-update
source /etc/profile

emerge -k -b genkernel
install -d /usr/portage/packages/gk_binaries
rm -f /usr/src/linux
