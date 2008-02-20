#!/bin/bash

source /tmp/chroot-functions.sh

## START BUILD
setup_portage

run_emerge "${clst_packages}"
