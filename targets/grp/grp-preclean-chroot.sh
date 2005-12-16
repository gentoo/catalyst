#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/grp-preclean-chroot.sh,v 1.9 2005/12/16 19:14:46 wolf31o2 Exp $

. /tmp/chroot-functions.sh
update_env_settings

gconftool-2 --shutdown
