# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript/Attic/alpha-archscript.sh,v 1.10 2005/03/09 00:22:05 wolf31o2 Exp $

case $1 in
	kernel)
	;;

	preclean)
		# Add entries for ttyS0 and ttyS1 to /etc/inittab.
		echo "t0:12345:respawn:/sbin/agetty -L 9600 ttyS0 vt100" >> ${clst_chroot_path}/etc/inittab
		echo "t1:12345:respawn:/sbin/agetty -L 9600 ttyS1 vt100" >> ${clst_chroot_path}/etc/inittab
	;;

	clean)
	;;

	bootloader)
		# Create a filesystem tree for the ISO at
		# ${clst_cdroot_path}. We extract the "cdtar" to this directory,
		# which will normally contains a pre-built binary
		# boot-loader/filesystem skeleton for the ISO. 
		
		cdtar=${clst_livecd_cdtar}
		[ -z "$cdtar" ] && die "Required key livecd/cdtar not specified, exiting"
		tar xjpvf ${cdtar} -C ${clst_cdroot_path} || die "Couldn't extract cdtar ${cdtar}"
		# Here is where we poke in our identifier
		touch ${clst_cdroot_path}/livecd
		[ -z "${clst_boot_kernel}" ] && die "Required key boot/kernel not specified, exiting"
		
		# unpack the kernel(s) that were built in kmerge.sh
		first=""
		for x in ${clst_boot_kernel}
		do
			kbinary="${clst_chroot_path}/usr/portage/packages/gk_binaries/${x}-${clst_version_stamp}.tar.bz2"
			[ ! -e "${kbinary}" ] && die "Can't find kernel tarball at ${kbinary}"
			
			tar xjvf ${kbinary} -C ${clst_cdroot_path}/boot
			
			# change kernel name from "kernel" to "gentoo", for example
			mv ${clst_cdroot_path}/boot/kernel* ${clst_cdroot_path}/boot/${x}
			
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

		acfg=${clst_cdroot_path}/etc/aboot.conf
		bctr=0
		for x in ${clst_boot_kernel}
		do
			echo -n "${bctr}:/boot/${x} " >> ${acfg}
			echo -n "initrd=/boot/${x}.igz root=/dev/ram0 " >> ${acfg}
			echo "init=/linuxrc ${cmdline_opts} cdroot" >> ${acfg}
			((bctr=${bctr}+1))
		done
	;;

	cdfs)
	;;

	iso)
		# this is for the livecd-final target, and calls the proper
		# command to build the iso file
		case ${clst_livecd_cdfstype} in
			zisofs)
				mkisofs -J -R -l -z -V "${iso_volume_id}" -o ${2} ${clst_cdroot_path}  || die "Cannot make ISO image"
			;;
			*)
				mkisofs -J -R -l -o ${2} ${clst_cdroot_path} || die "Cannot make ISO image"
			;;
		esac
		isomarkboot ${2} /boot/bootlx
	;;
esac
