#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/Attic/netboot-packages.sh,v 1.4 2005/01/13 22:57:25 wolf31o2 Exp $

portage_version=`/usr/lib/portage/bin/portageq best_version / sys-apps/portage \
	| cut -d/ -f2 | cut -d- -f2,3`
if [ `echo ${portage_version} | cut -d- -f1 | cut -d. -f3` -lt 51 ]
then
	echo "ERROR: Your portage version is too low in your seed stage.  Portage version"
	echo "2.0.51 or greater is required."
	exit 1
fi

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

# setup our environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"
export USE_ORDER="env:conf:defaults"

if [ "${clst_FETCH}" ]
then
	export clst_myemergeopts="${clst_myemergeopts} -f"
fi

# START BUILD
if [ "${clst_VERBOSE}" ]
then
	emerge ${clst_myemergeopts} -vp ${clst_packages}
	sleep 15
fi

emerge ${clst_myemergeopts} ${clst_packages}
