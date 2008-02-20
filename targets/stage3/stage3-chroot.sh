#!/bin/bash

. /tmp/chroot-functions.sh

## START BUILD
setup_portage

run_emerge "-e system"
