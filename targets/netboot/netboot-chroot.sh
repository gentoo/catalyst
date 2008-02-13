#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

# START BUILD
run_emerge "${clst_packages}"
