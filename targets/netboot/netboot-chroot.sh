#!/bin/bash

. /tmp/chroot-functions.sh

# START BUILD
run_emerge "${clst_packages}"
