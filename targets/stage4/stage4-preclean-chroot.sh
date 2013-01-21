#!/bin/bash

export RUN_DEFAULT_FUNCS="no"

source /tmp/chroot-functions.sh

update_env_settings
show_debug

if [ -n "${clst_DISTCC}" ]
then
	cleanup_distcc
fi

if [ -n "${clst_ICECREAM}" ]
then
	cleanup_icecream
fi
