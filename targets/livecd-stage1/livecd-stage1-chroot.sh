#!/bin/bash

source /tmp/chroot-functions.sh

## START BUILD
setup_pkgmgr

run_emerge "${clst_packages}"
