#!/bin/bash
# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript-support/Attic/pre-kmerge.sh,v 1.1 2004/05/12 21:18:50 zhen Exp $

/usr/sbin/env-update
source /etc/profile

emerge genkernel
install -d /tmp/binaries
rm -f /usr/src/linux
