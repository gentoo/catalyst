#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/Attic/netboot-busybox.sh,v 1.3 2004/10/11 14:19:30 zhen Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

# setup our environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"
export USE_ORDER="env:conf:defaults"	

# Use the catalyst config
export USE="savedconfig netboot"
ROOT=${IMAGE_PATH} emerge --nodeps ${clst_myemergeopts} busybox || exit 1
