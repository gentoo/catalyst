#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/embedded-chroot.sh,v 1.14 2005/04/04 17:48:33 rocket Exp $

. /tmp/chroot-functions.sh

check_portage_version

update_env_settings

setup_myfeatures
setup_myemergeopts


# setup the environment
export FEATURES="${clst_myfeatures}"
export CONFIG_PROTECT="-*"
export clst_myemergeopts="${clst_myemergeopts} -O"
export USE="${clst_embedded_use}"

## START BUILD

run_emerge "${clst_embedded_packages}"
