#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/stage3-chroot.sh,v 1.17 2005/01/28 18:37:23 wolf31o2 Exp $

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

if [ -n "${clst_CCACHE}" ]
then
	export clst_myfeatures="${clst_myfeatures} ccache"
	emerge --oneshot --nodeps -b -k ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then   
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gnome -gtk" emerge --oneshot --nodeps -b -k distcc || exit 1
fi

if [ -n "${clst_PKGCACHE}" ]
then
	export clst_myemergeopts="${clst_myemergeopts} --usepkg --buildpkg --newuse"
fi

if [ -n "${clst_FETCH}" ]
then
	export clst_myemergeopts="${clst_myemergeopts} -f"
fi

GRP_STAGE23_USE="$(portageq envvar GRP_STAGE23_USE)"

# setup the build environment
export FEATURES="${clst_myfeatures}"
export USE="-* ${clst_HOSTUSE} ${GRP_STAGE23_USE}"
export CONFIG_PROTECT="-*"

## START BUILD
# portage needs to be merged manually with USE="build" set to avoid frying our
# make.conf. emerge system could merge it otherwise.
USE="build" emerge portage

if [ -n "${clst_VERBOSE}" ]
then
	emerge -e ${clst_myemergeopts} -vp system || exit 1
	echo "Press any key within 15 seconds to pause the build..."
	read -s -t 15 -n 1
	if [ $? -eq 0 ]
	then
		echo "Press any key to continue..."
		read -s -n 1
	fi
fi

emerge -e ${clst_myemergeopts} system || exit 1
