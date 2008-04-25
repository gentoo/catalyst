#!/bin/bash

export RUN_DEFAULT_FUNCS="no"

source /tmp/chroot-functions.sh

# Since we didn't run the default functions, we call a couple here.
update_env_settings
setup_myfeatures

# Now, some finishing touches to initialize gcc-config....
unset ROOT

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
