#!/bin/bash

source /tmp/chroot-functions.sh

# If the user enabled PRESERVE_LIBS in options, tell portage to preserve them.
[ -n "${clst_PRESERVE_LIBS}" ] && FEATURES="${clst_myfeatures} preserve-libs"
if [ "${clst_livecd_depclean}" = "keepbdeps" ]; then
	run_merge --depclean --with-bdeps=y
else
	run_merge --depclean --with-bdeps=n
fi

exit 0
