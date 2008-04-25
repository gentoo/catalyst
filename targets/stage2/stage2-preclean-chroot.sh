#!/bin/bash

export RUN_DEFAULT_FUNCS="no"

source /tmp/chroot-functions.sh

# Since we didn't run the default functions, we call a couple here.
update_env_settings
setup_myfeatures

cleanup_stages

if [ -n "${clst_CCACHE}" ]
then
	run_merge -C dev-util/ccache || exit 1
fi

if [ -n "${clst_DISTCC}" ]
then
	run_merge -C sys-devel/distcc || exit 1
fi

if [ -n "${clst_ICECREAM}" ]
then
	run_merge -C sys-devel/icecream || exit 1
fi
