# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/livecd/runscript/Attic/ppc-archscript.sh,v 1.5 2004/10/15 02:40:00 zhen Exp $

case $1 in
	kernel)
	;;

	preclean)
	;;

	clean)
	;;

	bootloader)
		# PPC requirements: 
		# -----------------
		# The specs indicate the kernels to be build. We need to put
		# those kernels and the corresponding initrd.img.gz(s) in the
		# /boot directory. This directory contains a message boot.msg 
		# containing some info to be displayed on boot, a configuration
		# (yaboot.conf) specifying the boot options (kernel/initrd 
		# combinations). The boot directory also contains a file called
		# yaboot, which normally gets copied from the live environment.
		# For now we supply a prebuilt file, prebuilt configuration 
		# and prebuilt boot message. This can be enhanced later on
		# but the following suffices for now:
		
		cdtar=${clst_livecd_cdtar}
		[ -z "${cdtar}" ] && die "Required key livecd/cdtar not defined, exiting"
		tar xjpvf ${cdtar} -C ${clst_cdroot_path} || die "Couldn't extract cdtar ${cdtar}"
		
		[ -z "${clst_boot_kernel}" ] && die "Required key boot/kernel not defined, exiting."
		
		first=""
		for x in ${clst_boot_kernel}
		do
			kbinary="${clst_chroot_path}/usr/portage/packages/gk_binaries/${x}-${clst_version_stamp}.tar.bz2"
			if [ -z "${first}" ]
			then
				# grab name of first kernel
				first="${x}"
			fi
			[ ! -e "${kbinary}" ] && die  "Can't find kernel tarball at ${kbinary}"
			tar xjvf ${kbinary} -C ${clst_cdroot_path}/boot
			
			# change kernel name from "kernel" to "gentoo", for example
			mv ${clst_cdroot_path}/boot/kernel* ${clst_cdroot_path}/boot/${x}
			
			# change initrd name from "initrd" to "gentoo.igz", for example
			mv ${clst_cdroot_path}/boot/initrd* ${clst_cdroot_path}/boot/initrd.img.gz
		done
	;;

	cdfs)
	;;

	iso)
		# The name of the iso should be retrieved from the specs. For now, asssume GentooPPC_2004.0
		mkisofs -J -r -netatalk -hfs -probe -map boot/map.hfs -part -no-desktop -hfs-volid GentooPPC_2004.0 -hfs-bless ./boot -o ${2} ${clst_cdroot_path}
	;;
esac
