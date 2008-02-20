#!/bin/bash

source /tmp/chroot-functions.sh

run_emerge -C ${clst_packages}

exit 0
