#!/bin/bash
# Copyright 1999-2003 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/Attic/stage1-preclean1-chroot.sh,v 1.1 2004/04/12 14:38:26 zhen Exp $

/usr/sbin/env-update
source /etc/profile

if [ -n "${clst_DISTCC}" ]
then
	/bin/killall -9 distccd
	userdel distcc || exit 1
fi
