#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/stage3-preclean-chroot.sh,v 1.6 2005/07/05 21:53:41 wolf31o2 Exp $

. /tmp/chroot-functions.sh
update_env_settings

export CONFIG_PROTECT="-*"

if [ -n "${clst_CCACHE}" ]
then
	emerge -C dev-util/ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then
	emerge -C sys-devel/distcc || exit 1
fi
