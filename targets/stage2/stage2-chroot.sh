#!/bin/sh
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/stage2-chroot.sh,v 1.3 2004/06/04 14:03:46 zhen Exp $

/usr/sbin/env-update
source /etc/profile

if [ -f /tmp/envscript ]
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

	USE="-gnome -gtk" emerge --oneshot --nodeps distcc || exit 1
	/usr/bin/distcc-config --install 2>&1 > /dev/null
	/usr/bin/distccd 2>&1 > /dev/null
fi
										
if [ -n "${clst_PKGCACHE}" ]
then
	export EMERGE_OPTS="--usepkg --buildpkg"
fi

grep GRP_STAGE23_USE /etc/make.profile/make.defaults > /tmp/stage23
source /tmp/stage23
rm -f /tmp/stage23

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
