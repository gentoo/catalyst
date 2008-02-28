#!/bin/bash

source /tmp/chroot-functions.sh

## START BUILD
setup_pkgmgr

echo "Bringing system up to date using profile specific use flags"
run_merge -u system

echo "Emerging packages using stage4 use flags"

run_merge "${clst_packages}"
