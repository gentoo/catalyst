#!/bin/bash

. /tmp/chroot-functions.sh

update_env_settings

setup_myfeatures

# Setup the environment
export DESTROOT="${clst_root_path}"
export clst_root_path="/"

echo "Installing dependencies into ${DESTROOT}..."
run_emerge -o "${clst_embedded_packages}"

export clst_root_path="${DESTROOT}"
export INSTALL_MASK="${clst_install_mask}" 

run_emerge -1 -O "${clst_embedded_packages}"
