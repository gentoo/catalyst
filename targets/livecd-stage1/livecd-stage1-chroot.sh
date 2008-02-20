#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

show_debug

## START BUILD
setup_portage

run_emerge "${clst_packages}"
