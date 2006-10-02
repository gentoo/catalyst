#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/embedded-preclean-chroot.sh,v 1.9 2006/10/02 20:25:25 wolf31o2 Exp $

. /tmp/chroot-functions.sh
update_env_settings

cleanup_distcc
