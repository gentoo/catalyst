#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/grp/grp-preclean-chroot.sh,v 1.8 2005/07/05 21:53:41 wolf31o2 Exp $


. /tmp/chroot-functions.sh
update_env_settings

gconftool-2 --shutdown
