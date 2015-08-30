#!/bin/bash

source /tmp/chroot-functions.sh

# We do this first, so we know our package list for --debug
export clst_buildpkgs="$(/tmp/build.py)"

# Setup our environment
BOOTSTRAP_USE="$(portageq envvar BOOTSTRAP_USE)"
[ -n "${clst_BINDIST}" ] && BINDIST="bindist"
BOOTSTRAP_USE="${BOOTSTRAP_USE} ${BINDIST}"

FEATURES="${clst_myfeatures} nodoc noman noinfo -news"

## Sanity check profile
if [ -z "${clst_buildpkgs}" ]
then
	echo "Your profile seems to be broken."
	echo "Could not build a list of build packages."
	echo "Double check your ${clst_port_conf}/make.profile link and the 'packages' files."
	exit 1
fi

## Setup seed pkgmgr to ensure latest
clst_root_path=/ setup_pkgmgr "build"

# Update stage3
if [ -n "${clst_update_seed}" ]; then
	if [ "${clst_update_seed}" == "yes" ]; then
		echo "Updating seed stage..."
		if [ -n "${clst_update_seed_command}" ]; then
			clst_root_path=/ run_merge "--buildpkg=n ${clst_update_seed_command}"
		else
			clst_root_path=/ run_merge "--update --deep --newuse --complete-graph --rebuild-if-new-ver gcc"
		fi
	elif [ "${clst_update_seed}" != "no" ]; then
		echo "Invalid setting for update_seed: ${clst_update_seed}"
		exit 1
	fi

	# reset emerge options for the target
	clst_update_seed=no setup_myemergeopts
else
	echo "Skipping seed stage update..."
fi

make_destpath /tmp/stage1root

## START BUILD
# First, we drop in a known-good baselayout
[ -e ${clst_make_conf} ] && echo "USE=\"${USE} -build\"" >> ${clst_make_conf}
run_merge "--oneshot --nodeps sys-apps/baselayout"
sed -i "/USE=\"${USE} -build\"/d" ${clst_make_conf}

# Now, we install our packages
if [ -e ${clst_make_conf} ]; then
	echo "USE=\"-* build ${BOOTSTRAP_USE} ${clst_HOSTUSE}\"" >> ${clst_make_conf}
	for useexpand in ${clst_HOSTUSEEXPAND}; do
		x="clst_${useexpand}"
		echo "${useexpand}=\"${!x}\"" \
		>> ${clst_make_conf}
	done
fi

run_merge "--oneshot ${clst_buildpkgs}"
sed -i "/USE=\"-* build ${BOOTSTRAP_USE} ${clst_HOSTUSE}\"/d" \
	${clst_make_conf}
for useexpand in ${clst_HOSTUSEEXPAND}; do
	x="clst_${useexpand}"
	sed -i "/${useexpand}=\"${!x}\"/d" \
	${clst_make_conf}
done
