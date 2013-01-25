#!/bin/bash

source /tmp/chroot-functions.sh

# We do this first, so we know our package list for --debug
export clst_buildpkgs="$(/tmp/build.py)"

# Setup our environment
BOOTSTRAP_USE="$(portageq envvar BOOTSTRAP_USE)"
[ -n "${clst_BINDIST}" ] && BOOTSTRAP_USE="${BOOTSTRAP_USE} bindist"

FEATURES="${clst_myfeatures} nodoc noman noinfo -news"

## Sanity check profile
if [ -z "${clst_buildpkgs}" ]
then
	echo "Your profile seems to be broken."
	echo "Could not build a list of build packages."
	echo "Double check your /etc/portage/make.profile link and the 'packages' files."
	exit 1
fi

## Setup seed pkgmgr to ensure latest
clst_root_path=/ setup_pkgmgr

# Update stage3
if [ -n "${clst_update_seed}" ]; then
	if [ "${clst_update_seed}" == "yes" ]; then
		echo "Updating seed stage..."
		if [ -n "${clst_update_seed_command}" ]; then
			clst_root_path=/ run_merge "${clst_update_seed_command}"
		else
			clst_root_path=/ run_merge "--update --deep --newuse --onlydeps gcc"
		fi
	elif [ "${clst_update_seed}" != "no" ]; then
		echo "Invalid setting for update_seed: ${clst_update_seed}"
		exit 1
	fi
else
	echo "Skipping seed stage update..."
fi

make_destpath /tmp/stage1root

## START BUILD
# First, we drop in a known-good baselayout
[ -e /etc/portage/make.conf ] && \
	echo 'USE="${USE} -build"' >> /etc/portage/make.conf
run_merge "--oneshot --nodeps sys-apps/baselayout"

sed -i '/USE="${USE} -build"/d' /etc/portage/make.conf

# Now, we install our packages
[ -e /etc/portage/make.conf ] && \
	echo "USE=\"-* build ${BOOTSTRAP_USE} ${clst_HOSTUSE}\"" \
	>> /etc/portage/make.conf
run_merge "--oneshot ${clst_buildpkgs}"
sed -i "/USE=\"-* build ${BOOTSTRAP_USE} ${clst_HOSTUSE}\"/d" \
	/etc/portage/make.conf
