#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/netboot-chroot.sh,v 1.5 2005/12/19 15:03:25 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures
setup_myemergeopts

# Setup our environment
export FEATURES="${clst_myfeatures}"
export USE_ORDER="env:pkg:conf:defaults"

# START BUILD

run_emerge ${clst_myemergeopts} ${clst_packages}
