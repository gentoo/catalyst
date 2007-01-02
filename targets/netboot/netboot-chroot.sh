#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures
setup_myemergeopts

# Setup our environment
export FEATURES="${clst_myfeatures}"

# START BUILD

run_emerge ${clst_myemergeopts} ${clst_packages}
