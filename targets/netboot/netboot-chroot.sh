#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/netboot-chroot.sh,v 1.1 2005/04/04 17:50:30 rocket Exp $
. /tmp/chroot-functions.sh

update_env_settings

check_portage_version
setup_myfeatures
setup_myemergeopts

# setup our environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"
export USE_ORDER="env:pkg:conf:defaults"

# START BUILD

run_emerge ${clst_myemergeopts} ${clst_packages}
