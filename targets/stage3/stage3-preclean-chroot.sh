#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/stage3-preclean-chroot.sh,v 1.2 2004/04/14 00:17:59 zhen Exp $

/usr/sbin/env-update
source /etc/profile

export CONFIG_PROTECT="-*"

if [ -n "${clst_CCACHE}" ]
then
	emerge -C dev-util/ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then
	pkill -signal 9 -U 7980
	emerge -C sys-devel/distcc || exit 1
	userdel distcc || exit 1
fi
