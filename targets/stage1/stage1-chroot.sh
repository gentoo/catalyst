#!/bin/bash

. /tmp/chroot-functions.sh

# Setup our environment
export clst_buildpkgs="$(/tmp/build.py)"
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
clst_root_path=/ setup_portage

USE="-build" run_emerge "--oneshot --nodeps virtual/baselayout"

USE="-* bindist build ${STAGE1_USE} ${HOSTUSE}" run_emerge "--noreplace --oneshot ${clst_buildpkgs}"
