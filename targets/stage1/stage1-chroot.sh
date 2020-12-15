#!/bin/bash

source /tmp/chroot-functions.sh

# We do this first, so we know our package list for --debug
buildpkgs=($(/tmp/build.py))

## Sanity check profile
if [[ ${#buildpkgs[@]} -eq 0 ]]; then
	echo "Your profile seems to be broken."
	echo "Could not build a list of build packages."
	echo "Double check your ${clst_port_conf}/make.profile link and the 'packages' files."
	exit 1
fi

# Setup our environment
[ -n "${clst_BINDIST}" ] && BINDIST="bindist"
BOOTSTRAP_USE="$(portageq envvar BOOTSTRAP_USE)"

FEATURES="${clst_myfeatures} nodoc noman noinfo -news"

# We need to ensure the base stage3 has USE="bindist"
# if BINDIST is set to avoid issues with openssl / openssh
[ -e ${clst_make_conf} ] && echo "USE=\"${BINDIST} ${USE}\"" >> ${clst_make_conf}

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

# Clear USE
[ -e ${clst_make_conf} ] && ${clst_sed} -i -e "/^USE=\"${BINDIST} ${USE}\"/d" ${clst_make_conf}
make_destpath /tmp/stage1root

## START BUILD
# First, we drop in a known-good baselayout
[ -e ${clst_make_conf} ] && echo "USE=\"${USE} -build\"" >> ${clst_make_conf}
run_merge "--oneshot --nodeps sys-apps/baselayout"
${clst_sed} -i "/USE=\"${USE} -build\"/d" ${clst_make_conf}

echo "$locales" > /etc/locale.gen
for etc in /etc "${clst_root_path}"/etc; do
	echo "LANG=C.UTF8" > ${etc}/env.d/02locale
done
update_env_settings

# Now, we install our packages
if [ -e ${clst_make_conf} ]; then
	echo "CATALYST_USE=\"-* build ${BINDIST} ${clst_CATALYST_USE}\"" >> ${clst_make_conf}
	echo "USE=\"\${CATALYST_USE} ${USE} ${BOOTSTRAP_USE} ${clst_HOSTUSE}\"" >> ${clst_make_conf}

	for useexpand in ${clst_HOSTUSEEXPAND}; do
		x="clst_${useexpand}"
		echo "${useexpand}=\"${!x}\"" \
		>> ${clst_make_conf}
	done
fi

run_merge "--oneshot ${buildpkgs[@]}"

# TODO: Drop this when locale-gen in stable glibc supports ROOT.
#
# locale-gen does not support the ROOT variable, and as such glibc simply does
# not run locale-gen when ROOT is set. Since we've set LANG, we need to run
# locale-gen explicitly.
if [ -x "$(command -v locale-gen)" ]; then
	locale-gen --destdir "${clst_root_path}"/ || die "locale-gen failed"
fi

# Why are we removing these? Don't we need them for final make.conf?
for useexpand in ${clst_HOSTUSEEXPAND}; do
	x="clst_${useexpand}"
	${clst_sed} -i "/${useexpand}=\"${!x}\"/d" \
	${clst_make_conf}
done

# Clear USE
[ -e ${clst_make_conf} ] && ${clst_sed} -i -e "/^CATALYST_USE/d" ${clst_make_conf}
[ -e ${clst_make_conf} ] && ${clst_sed} -i -e "/^USE=\"/s/\${CATALYST_USE} ${USE} ${BOOTSTRAP_USE}//" ${clst_make_conf}
