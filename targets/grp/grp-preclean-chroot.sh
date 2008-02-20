#!/bin/bash

source /tmp/chroot-functions.sh

cleanup_stages

gconftool-2 --shutdown
