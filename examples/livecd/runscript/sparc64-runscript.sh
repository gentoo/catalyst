# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/examples/livecd/runscript/Attic/sparc64-runscript.sh,v 1.1 2004/01/19 04:01:48 weeve Exp $

# Section has been handled, do not execute additional scripts
RETURN_GOOD=0
# An error has occurred
RETURN_BAD=1
# This script executed properly, continue with additional scripts
RETURN_CONTINUE=2

die() {
	echo "$1"
	exit $RETURN_BAD
}

case $1 in
	kernbuild)
		echo "no generic process for sparc64, continuing"
		exit $RETURN_CONTINUE
	;;

	setupfs)
		echo "no generic process for sparc64, continuing"
		exit $RETURN_CONTINUE
	;;

	preclean)
		echo "no generic process for sparc64, continuing"
		exit 2
	;;

	clean)
		echo "no generic process for sparc64, continuing"
		exit $RETURN_CONTINUE
	;;

	setup_bootloader)
		# LOOPTYPE should be exported from default runscript, we use
		# it to determine kernel args
		if [ "${LOOPTYPE}" = "zisofs" ]
		then
			loop_opts="looptype=zisofs loop=/zisofs"
		elif [ "${LOOPTYPE}" = "normal" ]
		then
			loop_opts="looptype=normal loop=/livecd.loop"
		elif [ "${LOOPTYPE}" = "noloop" ]
		then
			# no loop at all wanted, just a raw copy on a cd
			loop_opts="looptype=noloop"
		fi

		# Time to create a filesystem tree for the ISO at
		# $clst_cdroot_path. We extract the "cdtar" to this directory,
		# which will normally contains a pre-built binary
		# boot-loader/filesystem skeleton for the ISO. 
		
		cdtar=$clst_livecd_cdtar
		[ "$cdtar" = "" ] && die "No livecd/cdtar specified (required)"
		tar xjpvf $cdtar -C $clst_cdroot_path || die \
		    "Couldn't extract cdtar $cdtar"
		if [ "$clst_boot_kernel" = "" ]
		then
			echo "No boot/kernel setting defined, exiting."
			exit 1
		fi
		first=""
		for x in $clst_boot_kernel
		do
			if [ "$first" = "" ]
			then
				#grab name of first kernel
				first="$x"
			fi
			if [ ! -e "$clst_binaries_source_path/$x.tar.bz2" ] 
			then
				echo "Can't find kernel tarball at $clst_binaries_source_path/$x.tar.bz2"
				exit 1
			fi
			tar xjvf $clst_binaries_source_path/$x.tar.bz2 -C \
			    $clst_cdroot_path/boot
			# change kernel name from "kernel" to "gentoo", for
			# example
			mv $clst_cdroot_path/boot/kernel \
			    $clst_cdroot_path/boot/$x
			# change initrd name from "initrd" to "gentoo.igz",
			# for example
			mv $clst_cdroot_path/boot/initrd \
			    $clst_cdroot_path/boot/$x.igz
		done
		scfg=$clst_cdroot_path/boot/silo.conf
		kmsg=$clst_cdroot_path/boot/kernels.msg
		hmsg=$clst_cdroot_path/boot/help.msg
		echo "default=\"$first\"" > $scfg
		echo "timeout=\"150\"" >> $scfg
		echo "message=\"/boot/boot.msg\"" >> $scfg

		echo "Available kernels:" > $kmsg
		echo "TEST HELP MESSAGE" > $hmsg

		for x in $clst_boot_kernel
		do
			echo >> $icfg
			echo "image=\"/boot/$x\"" >> $scfg
			echo -e "\tlabel=\"$x\"" >> $scfg
			echo -e "\tappend=\"initrd=/boot/$x.igz root=/dev/ram0 init=/linuxrc ${loop_opts} cdroot\"" >> $scfg

		done

		echo "image=\"cat /boot/silo.conf\"" >> $scfg
		echo -e "label=\"config\"" >> $scfg
		exit $RETURN_CONTINUE
	;;

	loop)
		echo "no generic process for sparc64, continuing"
		exit $RETURN_CONTINUE
	;;

	iso_create)
		# this is for the livecd-final target, and calls the proper
		# command to build the iso file
		mkisofs -J -R -l -o ${clst_iso_path} -G /boot/isofs.b -B ... \
		    $clst_cdroot_path
		exit $RETURN_GOOD
	;;
esac
exit $RETURN_CONTINUE
