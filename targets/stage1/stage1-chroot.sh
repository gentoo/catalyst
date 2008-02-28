#!/bin/bash

# We do this first, so we know our package list for --debug
export clst_buildpkgs="$(/tmp/build.py)"

source /tmp/chroot-functions.sh

# Setup our environment
export STAGE1_USE="$(portageq envvar STAGE1_USE)"
export USE="-* bindist build ${STAGE1_USE}"
export FEATURES="${clst_myfeatures} nodoc noman noinfo"

## Sanity check profile
if [ -z "${clst_buildpkgs}" ]
then
	echo "Your profile seems to be broken."
	echo "Could not build a list of build packages."
	echo "Double check your /etc/make.profile link and the 'packages' files."
	exit 1
fi

## START BUILD
clst_root_path=/ setup_pkgmgr

USE="-build" run_merge "--oneshot --nodeps virtual/baselayout"

USE="-* bindist build ${STAGE1_USE} ${HOSTUSE}" run_merge "--noreplace --oneshot --newuse ${clst_buildpkgs}"
