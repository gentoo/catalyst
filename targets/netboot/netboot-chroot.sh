#!/bin/bash

source /tmp/chroot-functions.sh

# START BUILD
run_emerge "${clst_packages}"
