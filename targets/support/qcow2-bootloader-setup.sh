#!/bin/bash

source ${clst_shdir}/support/functions.sh

# $1 would be the the destination root for an iso
# ${clst_stage_path} is where the stage can be found

cmdline_opts=()
my_bootdir="${clst_stage_path}/boot"

# Add any additional options
if [ -n "${clst_diskimage_bootargs}" ]
then
	for x in ${clst_diskimage_bootargs}
	do
		cmdline_opts+=(${x})
	done
fi

