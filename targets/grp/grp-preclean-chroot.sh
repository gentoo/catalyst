#!/bin/bash

. /tmp/chroot-functions.sh
update_env_settings
cleanup_distcc

gconftool-2 --shutdown
