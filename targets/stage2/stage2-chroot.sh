#!/bin/sh
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/stage2-chroot.sh,v 1.5 2004/08/02 23:23:34 zhen Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

if [ -n "${clst_CCACHE}" ]
then
	export clst_myfeatures="${clst_myfeatures} ccache"
	emerge -b -k --oneshot --nodeps ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then
	export clst_myfeatures="${clst_myfeatures} distcc"
	export DISTCC_HOSTS="${clst_distcc_hosts}"

	USE="-gnome -gtk" emerge -b -k --oneshot --nodeps distcc || exit 1
	/usr/bin/distcc-config --install 2>&1 > /dev/null
	/usr/bin/distccd 2>&1 > /dev/null
fi
										
if [ -n "${clst_PKGCACHE}" ]
then
	export EMERGE_OPTS="--usepkg --buildpkg"
fi

GRP_STAGE23_USE="$(source /etc/make.profile/make.defaults ; echo ${GRP_STAGE23_USE})"

if [ -f /usr/portage/profiles/${clst_profile}/parent ]
then
	export clst_bootstrap="bootstrap-cascade.sh"
else
	export clst_bootstrap=bootstrap.sh
fi

## setup the environment
export FEATURES="${clst_myfeatures}"

## START BUILD
/usr/portage/scripts/${clst_bootstrap} || exit 1
