#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/embedded-chroot.sh,v 1.1 2004/04/12 14:38:26 zhen Exp $

/usr/sbin/env-update
source /etc/profile

if [ -n "${clst_ENVSCRIPT}" ]
then
	source /tmp/envscript
	rm -f /tmp/envscript
fi

if [ -n "${clst_CCACHE}" ]
then
	export clst_myfeatures="${clst_myfeatures} ccache"
	emerge --oneshot --nodeps ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gtk -gnome" emerge --oneshot --nodeps distcc || exit 1
	echo "distcc:x:240:2:distccd:/dev/null:/bin/false" >> /etc/passwd
	/usr/bin/distcc-config --install 2>&1 > /dev/null
	/usr/bin/distccd 2>&1 > /dev/null
fi

if [ -n "${clst_PKGCACHE}" ]
then
	export clst_myemergeopts="--usepkg --buildpkg"
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
ROOT=/tmp/mergeroot emerge ${clst_myemergeopts} ${clst_embedded_packages} || exit 1
