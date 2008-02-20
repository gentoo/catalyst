#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

show_debug

setup_portage

## START BUILD

run_emerge "-e system"

rm -f /var/lib/portage/world
touch /var/lib/portage/world

rm -f /var/log/emerge.log /var/log/portage/elog/*
