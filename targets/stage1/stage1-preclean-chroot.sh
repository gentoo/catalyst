#!/bin/bash

export ROOT=/tmp/stage1root
export RUN_DEFAULT_FUNCS="no"

source /tmp/chroot-functions.sh

update_env_settings
show_debug

# Now, some finishing touches to initialize gcc-config....
setup_gcc
setup_binutils

# Stage1 is not going to have anything in zoneinfo, so save our Factory timezone
if [ -d /usr/share/zoneinfo ]
then
	rm -f /etc/localtime
	cp /usr/share/zoneinfo/Factory /etc/localtime
else
	echo UTC > /etc/TZ
fi

cleanup_stages
