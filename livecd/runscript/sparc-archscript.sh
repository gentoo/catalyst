# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript/Attic/sparc-archscript.sh,v 1.8 2005/01/28 20:53:39 wolf31o2 Exp $

case $1 in
	kernel)
	;;

	preclean)
	;;

	clean)
	;;

	bootloader)
		# Create a filesystem tree for the ISO at
		# $clst_cdroot_path. We extract the "cdtar" to this directory,
		# which will normally contains a pre-built binary
		# boot-loader/filesystem skeleton for the ISO. 
		
		cdtar=${clst_livecd_cdtar}
		[ -z "$cdtar" ] && die "Required key livecd/cdtar not defined, exiting"
		tar xjpvf ${cdtar} -C ${clst_cdroot_path} || die "Couldn't extract cdtar ${cdtar}"
		
		[ -z "$clst_boot_kernel" ] && die "Required key boot/kernel not defined, exiting"
		
		# install the kernels built in kmerge.sh
		first=""
		for x in ${clst_boot_kernel}
		do
			kbinary="${clst_chroot_path}/usr/portage/packages/gk_binaries/${x}-${clst_version_stamp}.tar.bz2"	
			
			if [ -z "${first}" ]
			then
				# grab name of first kernel
				first="${x}"
			fi
			
			[ ! -e "${kbinary}" ] && die "Can't find kernel tarball at ${kbinary}"
			tar xjvf ${kbinary} -C ${clst_cdroot_path}/boot
			
			# change kernel name from "kernel" to "gentoo", for example
			mv ${clst_cdroot_path}/boot/kernel-* ${clst_cdroot_path}/boot/${x}
			
			# change initrd name from "initrd" to "gentoo.igz", for example
			mv ${clst_cdroot_path}/boot/initrd* ${clst_cdroot_path}/boot/${x}.igz
		done

		# figure out what device manager we are using and handle it accordingly
		if [ "${clst_livecd_devmanager}" == "udev" ]
		then
			cmdline_opts="${cmdline_opts} udev nodevfs"
		else
			cmdline_opts="${cmdline_opts} noudev devfs"
		fi
		
		scfg=${clst_cdroot_path}/boot/silo.conf
		echo "default=\"help\"" > ${scfg}
		echo "message=\"/boot/boot.msg\"" >> ${scfg}

		for x in ${clst_boot_kernel}
		do
			echo >> ${icfg}
			echo "image=\"/boot/${x}\"" >> ${scfg}
			echo -e "\tlabel=\"${x}\"" >> ${scfg}
			echo -e "\tappend=\"initrd=/boot/${x}.igz root=/dev/ram0 init=/linuxrc ${cmdline_opts} cdroot\"" >> ${scfg}

		done

		echo "image=\"cat /boot/silo.conf\"" >> ${scfg}
		echo -e "label=\"config\"" >> ${scfg}
		echo "image=\"cat /boot/video.msg\"" >> ${scfg}
		echo -e "label=\"video\"" >> ${scfg}
		echo "image=\"cat /boot/help.msg\"" >> ${scfg}
		echo -e "label=\"help\"" >> ${scfg}
	;;

	cdfs)
	;;

	iso)
		# this is for the livecd-final target, and calls the proper
		# command to build the iso file
		mkisofs -J -R -l -o ${2} -G ${clst_cdroot_path}/boot/isofs.b -B ... ${clst_cdroot_path}  || die "Cannot make ISO image"
	;;
esac
