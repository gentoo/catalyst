#!/bin/bash

source /tmp/chroot-functions.sh

## START BUILD
setup_pkgmgr

# Set the bindist USE flag if clst_BINDIST is set
[ -e ${clst_make_conf} ] && [ -n "${clst_BINDIST}" ] && echo "USE=\"${USE} bindist\"" >> ${clst_make_conf}

run_merge --update --deep --newuse "${clst_packages}"

# Clean-up USE again
sed -i "/USE=\"${USE} bindist\"/d" ${clst_make_conf}
