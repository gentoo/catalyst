#!/bin/bash
# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/stage1-chroot.sh,v 1.39 2005/12/08 15:16:48 rocket Exp $
	

. /tmp/chroot-functions.sh

check_portage_version

update_env_settings
#setup_gcc

setup_myfeatures
setup_myemergeopts

# setup our environment
export clst_buildpkgs="$(/tmp/build.py)"
export STAGE1_USE="$(portageq envvar STAGE1_USE)"
export USE="-* build ${STAGE1_USE}"
export FEATURES="${clst_myfeatures} nodoc noman noinfo"

## Sanity check profile
if [ -z "${clst_buildpkgs}" ]
then
	   echo "Your profile seems to be broken."
	   echo "Could not build a list of build packages."
	   echo "Double check your /etc/make.profile link and the 'packages' files."
	   exit 1
fi


## Sanity check profile
if [ -z "${clst_buildpkgs}" ]
then
	echo "Your profile seems to be broken."
	echo "Could not build a list of build packages."
	echo "Double check your /etc/make.profile link and the 'packages' files."
	exit 1
fi

## START BUILD
run_emerge "--noreplace ${clst_buildpkgs}"

rm -f /var/log/emerge.log
