#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

## START BUILD
# We need portage to be merged manually with USE="build" set to avoid frying
# our make.conf, otherwise, the system target could take care of it.

setup_portage

run_emerge "-e system"

rm -f /var/lib/portage/world
touch /var/lib/portage/world

rm -f /var/log/emerge.log /var/log/portage/elog/*
