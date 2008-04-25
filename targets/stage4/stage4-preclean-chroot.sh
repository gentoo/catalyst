#!/bin/bash

export RUN_DEFAULT_FUNCS="no"

source /tmp/chroot-functions.sh

# Since we didn't run the default functions, we call a couple here.
update_env_settings
setup_myfeatures

if [ -n "${clst_DISTCC}" ]
then
	cleanup_distcc
fi

if [ -n "${clst_ICECREAM}" ]
then
	cleanup_icecream
fi
