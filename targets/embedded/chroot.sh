#!/bin/bash

source /tmp/chroot-functions.sh

echo "Installing dependencies..."
ROOT=/ run_merge -o "${clst_embedded_packages}"

export ROOT="${clst_root_path}"
mkdir -p "$ROOT"

INSTALL_MASK="${clst_install_mask}" \
	run_merge -1 -O "${clst_embedded_packages}"
