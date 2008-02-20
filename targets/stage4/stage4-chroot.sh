#!/bin/bash

source /tmp/chroot-functions.sh

## START BUILD
setup_portage

echo "Bringing system up to date using profile specific use flags"
run_emerge -u system

echo "Emerging packages using stage4 use flags"

run_emerge "${clst_packages}"
