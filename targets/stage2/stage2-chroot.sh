#!/bin/bash

source /tmp/chroot-functions.sh

# Setup the environment
export FEATURES="${clst_myfeatures} nodoc noman noinfo -news"

## START BUILD
${clst_repo_basedir}/${clst_repo_name}/scripts/bootstrap.sh ${bootstrap_opts} || exit 1
