#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot2/netboot2-pkg.sh,v 1.2 2006/10/02 20:41:54 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures
setup_myemergeopts

# Setup our environment
export FEATURES="${clst_myfeatures}"
export USE_ORDER="env:pkg:conf:defaults"

# START BUILD

run_emerge ${clst_myemergeopts} ${clst_packages}
