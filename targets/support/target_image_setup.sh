#!/bin/bash

source ${clst_shdir}/support/functions.sh
source ${clst_shdir}/support/filesystem-functions.sh

# Make the directory if it doesnt exist
mkdir -p $1

loopret=1
case ${clst_fstype} in
	squashfs)
		create_squashfs $1
		loopret=$?
	;;
	jffs2)
		create_jffs2 $1
		loopret=$?
	;;
esac

if [ ${loopret} = "1" ]
then
	die "Filesystem not setup"
fi
exit $loopret
