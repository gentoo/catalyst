#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/Attic/netboot-packages.sh,v 1.2 2004/10/11 14:19:30 zhen Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

# setup our environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"
export USE_ORDER="env:conf:defaults"	

# START BUILD
if [ "${clst_VERBOSE}" ]
then
	emerge ${clst_myemergeopts} -vp ${clst_packages}
	sleep 15
fi

emerge ${clst_myemergeopts} ${clst_packages}
