#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/embedded-chroot.sh,v 1.20 2005/12/16 19:08:59 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures
setup_myemergeopts


# Setup the environment
export FEATURES="${clst_myfeatures}"
#export clst_myemergeopts="${clst_myemergeopts} -O"
export USE="${clst_use}"
export DESTROOT=${clst_root_path}
export clst_root_path=/
## START BUILD

run_emerge "${clst_myemergeopts}" -o "${clst_embedded_packages}"

#export clst_myemergeopts="${clst_myemergeopts} -B"
#run_emerge "${clst_embedded_packages}"

export clst_root_path=${DESTROOT}
export clst_myemergeopts="${clst_myemergeopts} -1 -O"
export INSTALL_MASK="${clst_install_mask}" 
run_emerge "${clst_embedded_packages}"
