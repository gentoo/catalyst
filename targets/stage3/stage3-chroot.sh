#!/bin/bash

. /tmp/chroot-functions.sh

## START BUILD
setup_portage

run_emerge "-e system"

rm -f /var/lib/portage/world
touch /var/lib/portage/world

rm -f /var/log/emerge.log /var/log/portage/elog/*
