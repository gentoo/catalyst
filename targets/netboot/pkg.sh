#!/bin/bash

source /tmp/chroot-functions.sh

update_env_settings

setup_features

show_debug

# START BUILD

ROOT="$ROOT" run_merge ${clst_packages}
