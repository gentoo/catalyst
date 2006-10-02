#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/livecd-stage1/livecd-stage1-chroot.sh,v 1.24 2006/10/02 20:41:54 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures
setup_myemergeopts

# Setup the environment

export FEATURES="${clst_myfeatures}"

## START BUILD
setup_portage

# Turn off auto-use:
export USE_ORDER="env:pkg:conf:defaults"	
export USE="${clst_use}"

run_emerge "${clst_packages}"
