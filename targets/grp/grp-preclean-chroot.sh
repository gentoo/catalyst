#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/grp-preclean-chroot.sh,v 1.2 2004/04/14 14:27:38 zhen Exp $

/usr/sbin/env-update
source /etc/profile

if [ -n "${clst_DISTCC}" ]
then
	pkill -signal 9 -U 7980
	userdel distcc || exit 1
fi
