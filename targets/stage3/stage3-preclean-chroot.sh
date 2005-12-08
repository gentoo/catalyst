#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/stage3-preclean-chroot.sh,v 1.8 2005/12/08 15:16:48 rocket Exp $

. /tmp/chroot-functions.sh
update_env_settings

if [ -n "${clst_CCACHE}" ]
then
	run_emerge -C dev-util/ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then
	run_emerge -C sys-devel/distcc || exit 1
fi

rm -f /var/log/emerge.log
