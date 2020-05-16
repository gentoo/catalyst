#!/bin/bash

export RUN_DEFAULT_FUNCS="no"

source /tmp/chroot-functions.sh

update_env_settings
show_debug

cleanup_stages

if [ -n "${clst_CCACHE}" ]
then
	run_merge -C dev-util/ccache
fi

if [ -n "${clst_DISTCC}" ]
then
	run_merge -C sys-devel/distcc
fi

if [ -n "${clst_ICECREAM}" ]
then
	run_merge -C sys-devel/icecream
fi
