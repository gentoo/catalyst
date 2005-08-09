#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/stage3-preclean-chroot.sh,v 1.7 2005/08/09 19:02:31 rocket Exp $

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

rm -f /var/log/emerge.log
