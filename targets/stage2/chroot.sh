#!/bin/bash

source /tmp/chroot-functions.sh

# Setup the environment
export FEATURES="${FEATURES} nodoc noman noinfo -news"
export CONFIG_PROTECT="-* /etc/locale.gen"

echo "$locales" > /etc/locale.gen

## START BUILD
${clst_repo_basedir}/${clst_repo_name}/scripts/bootstrap.sh ${bootstrap_opts[@]} || exit 1

# Replace modified /etc/locale.gen with default
etc-update --automode -5
