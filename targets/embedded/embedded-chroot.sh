#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/embedded-chroot.sh,v 1.11 2005/01/11 14:10:19 wolf31o2 Exp $

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
