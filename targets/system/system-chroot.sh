#!/bin/bash

source /tmp/chroot-functions.sh

# Next, we install the package manager
clst_root_path=/ setup_pkgmgr
make_destpath /tmp/stage3root

# Install baselayout first, so we have our directory structure
[ -e /etc/make.conf ] && echo 'USE="${USE} build"' >> /etc/make.conf
run_merge "--oneshot --nodeps baselayout"
sed -i '/^USE="\${USE} build"$/d' /etc/make.conf

# Now, we emerge system
run_merge "system"
