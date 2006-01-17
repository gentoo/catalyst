#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage2/stage2-preclean-chroot.sh,v 1.10 2006/01/17 19:30:45 wolf31o2 Exp $

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

cleanup_distcc

rm -f /var/log/emerge.log
