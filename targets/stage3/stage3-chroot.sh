#!/bin/bash

source /tmp/chroot-functions.sh

## START BUILD
setup_pkgmgr

export CONFIG_PROTECT="-* /etc/locale.gen"

echo "$locales" > /etc/locale.gen

run_merge "-e --update --deep --with-bdeps=y @system"

# Replace modified /etc/locale.gen with default
etc-update --automode -5
