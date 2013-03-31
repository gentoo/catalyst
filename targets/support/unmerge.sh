#!/bin/bash

source /tmp/chroot-functions.sh

# If the user enabled PRESERVE_LIBS in options, tell portage to preserve them.
[ -n "${clst_PRESERVE_LIBS}" ] && FEATURES="${clst_myfeatures} preserve-libs"
run_merge -C ${clst_packages}

exit 0
