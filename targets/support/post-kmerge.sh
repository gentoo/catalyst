#!/bin/bash

RUN_DEFAULT_FUNCS="no"

source /tmp/chroot-functions.sh

# Only run depscan.sh if modules exist
if [ -n "$(ls /lib/modules)" ]
then
	/sbin/depscan.sh
	find /lib/modules -name modules.dep -exec touch {} \;
fi
