#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage1/livecd-stage1-chroot.sh,v 1.13 2005/01/26 21:59:40 wolf31o2 Exp $

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
	export clst_emergeopts="--usepkg --buildpkg --newuse"
else
	export clst_emergeopts=""
fi

if [ -n "${clst_FETCH}" ]
then
	export clst_emergeopts="${clst_emergeopts} -f"
fi

## setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"

## START BUILD
USE="build" emerge portage
#turn off auto-use:
export USE_ORDER="env:pkg:conf:defaults"	

if [ "${clst_VERBOSE}" ]
then
	emerge ${clst_emergeopts} -vp ${clst_packages}
	sleep 15
fi

portage_version=`/usr/lib/portage/bin/portageq best_version / sys-apps/portage \
	| cut -d/ -f2 | cut -d- -f2,3`

if [ `echo ${portage_version} | cut -d- -f1 | cut -d. -f3` -ge 51 ] &&
	[ `echo ${portage_version} | cut -d- -f2 | cut -dr -f2` -ge 4 ]
then
	emerge ${clst_emergeopts} ${clst_packages}
else
	for packages in ${clst_packages}; do
		emerge ${clst_emergeopts} ${packages}
	done
fi
