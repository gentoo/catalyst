#!/bin/bash

source /tmp/chroot-functions.sh

# Setup the environment
export FEATURES="${clst_myfeatures} nodoc noman noinfo -news"

# Set bindist USE flag if clst_BINDIST is set
# The bindist functions have been taken from support/chroot-functions.sh
if [ -e "${clst_make_conf}" ] && [ -n "${clst_BINDIST}" ]; then
	if grep -q ^USE "${clst_make_conf}"; then
		echo "USE=\"\${USE} bindist\"" >> "${clst_make_conf}"
	else
		echo "USE=\"bindist\"" >> "${clst_make_conf}"
	fi
fi



## START BUILD
/usr/portage/scripts/bootstrap.sh ${bootstrap_opts} || exit 1

# Clean-up USE again
sed -i "/USE=\"\${USE} bindist\"/d" "${clst_make_conf}"
sed -i "/USE=\"bindist\"/d" "${clst_make_conf}"
