#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/stage1-chroot.sh,v 1.30 2005/04/04 17:48:33 rocket Exp $
		
. /tmp/chroot-functions.sh
check_portage_version

update_env_settings

setup_gcc

setup_myfeatures
setup_myemergeopts

# setup our environment
export clst_buildpkgs="$(/tmp/build.py)"
export STAGE1_USE="$(portageq envvar STAGE1_USE)"
export USE="-* build ${STAGE1_USE}"
export FEATURES="${clst_myfeatures}"

## START BUILD
run_emerge "--noreplace ${clst_buildpkgs}"
