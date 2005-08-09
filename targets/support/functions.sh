# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
copy_to_chroot(){
	local file_name=$(basename ${1})
	local dest_dir=${clst_chroot_path}${2}
	if [ "${2}" != "" ]
	then
		echo "copying ${file_name} to ${dest_dir}"
		mkdir -p ${dest_dir}
		cp -a ${1} ${dest_dir}
		chmod 755 ${dest_dir}/${file_name}
	else
		echo "copying ${file_name} to ${clst_chroot_path}/tmp"
		mkdir -p ${chroot_path}/tmp
		cp -a ${1} ${clst_chroot_path}/tmp
		chmod 755 ${clst_chroot_path}/tmp/${file_name}
	fi

}

delete_from_chroot(){
	echo "removing ${clst_chroot_path}${1} from the chroot"
	rm -f ${clst_chroot_path}${1}
}

exec_in_chroot(){
# Takes the full path to the source file as its argument
# copies the file to the /tmp directory of the chroot
# and executes it.
		
	local file_name=$(basename ${1})
	local subdir=${2#/}

	if [ "${subdir}" != "" ]
	then
		copy_to_chroot ${1} ${subdir}/tmp/
		chroot_path=${clst_chroot_path}${subdir}
		copy_to_chroot ${clst_sharedir}/targets/support/chroot-functions.sh ${subdir}/tmp/
		echo "Running ${file_name} in chroot ${chroot_path}" 
		${clst_CHROOT} ${chroot_path} ${subdir}/tmp/${file_name} || exit 1
	else
		copy_to_chroot ${1} tmp/
		chroot_path=${clst_chroot_path}
		copy_to_chroot ${clst_sharedir}/targets/support/chroot-functions.sh tmp/
		echo "Running ${file_name} in chroot ${chroot_path}" 
		${clst_CHROOT} ${chroot_path}/ tmp/${file_name} || exit 1
	fi

	rm -f ${chroot_path}/tmp/${file_name}
	if [ "${subdir}" != "" ]
	then
		delete_from_chroot ${subdir}/tmp/${file_name}
		delete_from_chroot ${subdir}/tmp/chroot-functions.sh
	else
		delete_from_chroot tmp/chroot-functions.sh
		delete_from_chroot tmp/${file_name}
	fi

}

#return codes
die() {
	echo "$1"
	exit 1
}

extract_cdtar() {
	# Create a filesystem tree for the ISO at
        # $clst_target_path. We extract the "cdtar" to this directory,
	# which will normally contains a pre-built binary
	# boot-loader/filesystem skeleton for the ISO.

	cdtar=${clst_cdtar}
	[ -z "${cdtar}" ] && die "Required key cdtar not defined, exiting"
	tar xjpf ${cdtar} -C $1 || die "Couldn't extract cdtar ${cdtar}"
}

extract_kernels() {
	# extract multiple kernels
	#$1 = Destination
	#${clst_target_path}/kernel is often a good choice for ${1}

	# Takes the relative desination dir for the kernel as an arguement
	# i.e boot or isolinux
       [ -z "$clst_boot_kernel" ] && die "Required key boot/kernel not defined, exiting"
	# install the kernels built in kmerge.sh
	for x in ${clst_boot_kernel}
	do

		first=${first:-""}
		kbinary="${clst_chroot_path}/usr/portage/packages/gk_binaries/${x}-kernel-initrd-${clst_version_stamp}.tar.bz2"
		if [ -z "${first}" ]
		then
			# grab name of first kernel
			export first="${x}"
		fi
		
		[ ! -e "${kbinary}" ] && die "Can't find kernel tarball at ${kbinary}"
		mkdir -p ${1}/
		tar xjf ${kbinary} -C ${1}/ 

		
		
		# change config name from "config-*" to "gentoo", for example
		#mv ${1}/config-* ${1}/${x}-config
		rm ${1}/config-* 
		
		# change kernel name from "kernel" to "gentoo", for example
		mv ${1}/kernel-* ${1}/${x}

		# change initrd name from "initrd" to "gentoo.igz", for example
		if [ -e ${1}/initrd-* ]
		then 
			mv ${1}/initrd-* ${1}/${x}.igz
		fi

		if [ -e ${1}/initramfs-* ]
		then 
			mv ${1}/initramfs-* ${1}/${x}.igz
		fi
	done
}

extract_modules() {
	#$1 = Destination
	#$2 = kname	
	kmodules="${clst_chroot_path}/usr/portage/packages/gk_binaries/${2}-modules-${clst_version_stamp}.tar.bz2"
		
	[ ! -e "${kmodules}" ] && die "Can't find kernel modules tarball at ${kmodules}"
	mkdir -p ${1}/
	tar xjf ${kmodules} -C ${1} lib
}
extract_kernel() {
	#$1 = Destination
	#$2 = kname	
	
	kbinary="${clst_chroot_path}/usr/portage/packages/gk_binaries/${2}-kernel-initrd-${clst_version_stamp}.tar.bz2"
	[ ! -e "${kbinary}" ] && die "Can't find kernel tarball at ${kbinary}"
	mkdir -p ${1}/
	tar xjf ${kbinary} -C ${1}/
	# change config name from "config-*" to "gentoo", for example
	#mv ${1}/config-* ${1}/${2}-config
	rm ${1}/config-*

	# change kernel name from "kernel" to "gentoo", for example
	mv ${1}/kernel-* ${1}/${2}
	
	# change initrd name from "initrd" to "gentoo.igz", for example
	if [ -e ${1}/initrd-* ]
	then
		mv ${1}/initrd-* ${1}/${2}.igz
	fi
	
	# change initramfs name from "initramfs" to "gentoo.igz", for example
	if [ -e ${1}/initramfs-* ]
	then
	    mv ${1}/initramfs-* ${1}/${2}.igz
	fi
}

check_dev_manager(){
	# figure out what device manager we are using and handle it accordingly
	if [ "${clst_livecd_devmanager}" == "devfs" ]
	then
		cmdline_opts="${cmdline_opts} noudev devfs"
	elif [ "${clst_livecd_devmanager}" == "devfs" ]
	then
		cmdline_opts="${cmdline_opts} udev nodevfs"
	fi
}

check_bootargs(){
	# Add any additional options
	if [ -z "${clst_livecd_bootargs}" ]
	then
		for x in ${clst_livecd_bootargs}
		do
			cmdline_opts="${cmdline_opts} ${x}"
		done
	fi
}

check_filesystem_type(){
	case ${clst_fstype} in
       	normal)
		cmdline_opts="${cmdline_opts} looptype=normal loop=/image.loop"
	        ;;
	zisofs)
		cmdline_opts="${cmdline_opts} looptype=zisofs loop=/zisofs"
		;;
	noloop)
		;;
	gcloop)
		cmdline_opts="${cmdline_opts} looptype=gcloop loop=/image.gcloop"
		;;
	squashfs)
		cmdline_opts="${cmdline_opts} looptype=squashfs loop=/image.squashfs"
		;;
	jffs)
		cmdline_opts="${cmdline_opts} looptype=jffs loop=/image.jffs"
		;;
	jffs2)
		cmdline_opts="${cmdline_opts} looptype=jffs2 loop=/image.jffs2"
		;;
	cramfs)
		cmdline_opts="${cmdline_opts} looptype=cramfs loop=/image.cramfs"
		;;
	esac
}																														
