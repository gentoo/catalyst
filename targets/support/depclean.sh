#!/bin/bash

source /tmp/chroot-functions.sh

if [ "${clst_livecd_depclean}" = "keepbdeps" ]; then
	run_merge --depclean --with-bdeps=y
else
	run_merge --depclean --with-bdeps=n
fi

exit 0
