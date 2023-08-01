#!/bin/bash

RUN_DEFAULT_FUNCS="yes"

source /tmp/chroot-functions.sh

run_merge --oneshot sys-kernel/dracut
