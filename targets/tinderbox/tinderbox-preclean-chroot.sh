#!/bin/bash

source /tmp/chroot-functions.sh

if [ -n "${clst_DISTCC}" ]
then
	cleanup_distcc
fi

if [ -n "${clst_ICECREAM}" ]
then
	cleanup_icecream
fi
