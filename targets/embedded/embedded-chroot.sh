#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/embedded-chroot.sh,v 1.12 2005/01/13 22:57:25 wolf31o2 Exp $

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

	USE="-gtk -gnome" emerge --oneshot --nodeps -b -k distcc || exit 1
fi

if [ -n "${clst_PKGCACHE}" ]
then
	export clst_myemergeopts="--usepkg --buildpkg --newuse"
fi

if [ -n "${clst_FETCH}" ]
then
	export clst_myemergeopts="${clst_myemergeopts} -f"
fi

# setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"
export clst_myemergeopts="${clst_myemergeopts} -O"
export USE="${clst_embedded_use}"

if [ ! -d "/tmp/mergeroot" ]
then
	install -d /tmp/mergeroot
fi

## START BUILD
if [ "${clst_VERBOSE}" ]
then
	ROOT=/tmp/mergeroot emerge ${clst_myemergeopts} -vp ${clst_embedded_packages} || exit 1
	sleep 15
fi

ROOT=/tmp/mergeroot emerge ${clst_myemergeopts} ${clst_embedded_packages} || exit 1
