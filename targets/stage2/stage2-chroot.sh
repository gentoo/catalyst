#!/bin/sh
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/stage2-chroot.sh,v 1.10 2005/01/11 14:10:19 wolf31o2 Exp $

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
fi
										
if [ -n "${clst_PKGCACHE}" ]
then
	export bootstrap_opts="-r"
fi

if [ -n "${clst_FETCH}" ]
then
	export bootstrap_opts="-f"
fi

GRP_STAGE23_USE="$(portageq envvar GRP_STAGE23_USE)"


## setup the environment
export FEATURES="${clst_myfeatures}"

## START BUILD
/usr/portage/scripts/bootstrap.sh ${bootstrap_opts} || exit 1
