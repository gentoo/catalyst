#!/bin/bash

source /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

show_debug

# START BUILD

run_merge ${clst_packages}
