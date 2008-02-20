#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

show_debug

## START BUILD
setup_portage

echo "Bringing system up to date using profile specific use flags"
run_emerge -u system

echo "Emerging packages using stage4 use flags"

run_emerge "${clst_packages}"
