#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/embedded/embedded-chroot.sh,v 1.22 2006/10/02 20:41:54 wolf31o2 Exp $

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

run_emerge "${clst_myemergeopts}" -o "${clst_embedded_packages}"

#export clst_myemergeopts="${clst_myemergeopts} -B"
#run_emerge "${clst_embedded_packages}"

export clst_root_path=${DESTROOT}
export clst_myemergeopts="${clst_myemergeopts} -1 -O"
export INSTALL_MASK="${clst_install_mask}" 

run_emerge "${clst_embedded_packages}"
