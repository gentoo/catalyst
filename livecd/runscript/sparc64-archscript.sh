# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript/Attic/sparc64-archscript.sh,v 1.2 2004/03/23 07:20:34 zhen Exp $

case $1 in
	kernel)
		genkernel_args=""
		export genkernel_args
	;;

	preclean)
	;;

	clean)
	;;

	bootloader)
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
			if [ ! -e "$clst_chroot_path/tmp/binaries/$x.tar.bz2" ] 
			then
				echo "Can't find kernel tarball at $clst_chroot_path/tmp/binaries/$x.tar.bz2"
				exit 1
			fi
			tar xjvf $clst_chroot_path/tmp/binaries/$x.tar.bz2 -C \
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
			echo -e "\tappend=\"initrd=/boot/$x.igz root=/dev/ram0 init=/linuxrc ${cmdline_opts} cdroot\"" >> $scfg

		done

		echo "image=\"cat /boot/silo.conf\"" >> $scfg
		echo -e "label=\"config\"" >> $scfg
	;;

	cdfs)
	;;

	iso)
		# this is for the livecd-final target, and calls the proper
		# command to build the iso file
		mkisofs -J -R -l -z -o ${2} -G /boot/isofs.b -B ... ${clst_cdroot_path}
	;;
esac
