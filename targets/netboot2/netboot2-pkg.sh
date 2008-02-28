#!/bin/bash

source /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

show_debug

# Setup our environment
export FEATURES="${clst_myfeatures}"

# START BUILD

run_merge ${clst_myemergeopts} ${clst_packages}
