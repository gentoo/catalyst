#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2

. /tmp/chroot-functions.sh

check_portage_version
update_env_settings

setup_myfeatures
setup_myemergeopts

## setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"

## START BUILD
setup_portage
#turn off auto-use:
export USE_ORDER="env:pkg:conf:defaults"	

run_emerge "${clst_packages}"
