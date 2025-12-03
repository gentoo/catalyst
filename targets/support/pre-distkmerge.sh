#!/bin/bash

RUN_DEFAULT_FUNCS="yes"

source /tmp/chroot-functions.sh

# Disable chroot check in installkernel
touch /etc/kernel/install.d/05-check-chroot.install

run_merge --oneshot sys-kernel/dracut
