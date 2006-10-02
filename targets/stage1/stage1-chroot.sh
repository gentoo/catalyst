#!/bin/bash
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/stage1/stage1-chroot.sh,v 1.43 2006/10/02 20:41:54 wolf31o2 Exp $

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures
setup_myemergeopts

# Setup our environment
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

## START BUILD
run_emerge "--noreplace --oneshot ${clst_buildpkgs}"
rm -f /var/lib/portage/world
touch /var/lib/portage/world

rm -f /var/log/emerge.log
