#!/bin/bash

source /tmp/chroot-functions.sh

run_merge --oneshot genkernel
install -d /tmp/kerncache
