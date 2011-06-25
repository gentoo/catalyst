#!/bin/bash

# We do this first, so we know our package list for --debug
export clst_buildpkgs="$(/tmp/build.py)"

source /tmp/chroot-functions.sh

# Setup our environment
STAGE1_USE="$(portageq envvar STAGE1_USE)"
FEATURES="${clst_myfeatures} nodoc noman noinfo -news"

## Sanity check profile
if [ -z "${clst_buildpkgs}" ]
then
	echo "Your profile seems to be broken."
	echo "Could not build a list of build packages."
	echo "Double check your /etc/make.profile link and the 'packages' files."
	exit 1
fi

## START BUILD
# First, we drop in a known-good baselayout
[ -e /etc/make.conf ] && \
	echo 'USE="${USE} -build"' >> /etc/make.conf
run_merge "--oneshot --nodeps sys-apps/baselayout"
sed -i '/USE="${USE} -build"/d' /etc/make.conf

# Next, we install the package manager
clst_root_path=/ setup_pkgmgr
make_destpath /tmp/stage1root

# Now, we install our packages
[ -e /etc/make.conf ] && \
	echo "USE=\"-* bindist build ${STAGE1_USE} ${clst_HOSTUSE}\"" \
	>> /etc/make.conf
run_merge "--oneshot ${clst_buildpkgs}"
sed -i "/USE=\"-* bindist build ${STAGE1_USE} ${clst_HOSTUSE}\"/d" \
	/etc/make.conf
