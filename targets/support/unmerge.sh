#!/bin/bash

source /tmp/chroot-functions.sh

FEATURES="${clst_myfeatures} preserve-libs"
run_merge -C ${clst_packages}

exit 0
