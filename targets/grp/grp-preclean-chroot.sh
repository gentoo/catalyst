#!/bin/bash

. /tmp/chroot-functions.sh

cleanup_stages

gconftool-2 --shutdown
