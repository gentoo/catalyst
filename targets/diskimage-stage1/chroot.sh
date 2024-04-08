#!/bin/bash

source /tmp/chroot-functions.sh

run_merge --update --deep --newuse "${clst_packages}"
