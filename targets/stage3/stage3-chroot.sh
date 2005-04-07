#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage3/stage3-chroot.sh,v 1.19 2005/04/07 12:24:16 rocket Exp $

. /tmp/chroot-functions.sh
check_portage_version

update_env_settings

setup_myfeatures
setup_myemergeopts


# setup the build environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"
export GRP_STAGE23_USE="$(portageq envvar GRP_STAGE23_USE)"
export USE="-* ${clst_HOSTUSE} ${GRP_STAGE23_USE}"


## START BUILD
# portage needs to be merged manually with USE="build" set to avoid frying our
# make.conf. emerge system could merge it otherwise.

setup_portage

run_emerge "-e system"
