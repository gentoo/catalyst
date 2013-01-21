copy_to_chroot() {
	local src_file=$1
	local dest_dir=${clst_chroot_path}${2:-/tmp}
	mkdir -p ${dest_dir}
	echo "copying ${src_file##*/} to ${dest_dir}"
	cp -pPR "${src_file}" "${dest_dir}"/
}

delete_from_chroot(){
	if [ -e ${clst_chroot_path}${1} ]
	then
		echo "removing ${clst_chroot_path}${1} from the chroot"
		rm -f ${clst_chroot_path}${1}
	fi
}

exec_in_chroot(){
# Takes the full path to the source file as its argument
# copies the file to the /tmp directory of the chroot
# and executes it.
	local file_name=$(basename ${1})
	local subdir=${2}
	local destdir=".${subdir}/tmp"

	echo "Copying ${file_name} to ${destdir}"
	copy_to_chroot ${1} ${destdir}
	copy_to_chroot ${clst_sharedir}/targets/support/chroot-functions.sh \
		${destdir}

	chroot_path=${clst_chroot_path}${subdir}

	echo "Ensure the file has the executable bit set"
	chmod +x ${chroot_path}/${destdir}/${file_name}

	echo "Running ${file_name} in chroot ${chroot_path}"
	${clst_CHROOT} ${chroot_path} ${destdir}/${file_name} || exit 1

	delete_from_chroot ${destdir}/${file_name}
	delete_from_chroot ${destdir}/chroot-functions.sh
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
	if [ -z "${cdtar}" ]
	then
		echo "No cdtar specified. Skipping."
	else
		tar -I lbzip2 -xpf ${cdtar} -C $1 || die "Couldn't extract cdtar ${cdtar}"
	fi
}

extract_kernels() {
	# extract multiple kernels
	# $1 = Destination
	# ${clst_target_path}/kernel is often a good choice for ${1}

	# Takes the relative desination dir for the kernel as an arguement
	# i.e boot or isolinux
	[ -z "$clst_boot_kernel" ] && \
		die "Required key boot/kernel not defined, exiting"
	# install the kernels built in kmerge.sh
	for x in ${clst_boot_kernel}
	do
		first=${first:-""}
		kbinary="${clst_chroot_path}/tmp/kerncache/${x}-kernel-initrd-${clst_version_stamp}.tar.bz2"
		if [ -z "${first}" ]
		then
			# grab name of first kernel
			export first="${x}"
		fi

		[ ! -e "${kbinary}" ] && die "Can't find kernel tarball at ${kbinary}"
		mkdir -p ${1}/
		tar -I lbzip2 -xf ${kbinary} -C ${1}/

		# change config name from "config-*" to "gentoo", for example
		#mv ${1}/config-* ${1}/${x}-config
		rm ${1}/config-*

		# change kernel name from "kernel" to "gentoo", for example
		if [ -e ${1}/kernel-* ]
		then
			mv ${1}/kernel-* ${1}/${x}
		fi

		# change kernel name from "kernelz" to "gentoo", for example
		if [ -e ${1}/kernelz-* ]
		then
			mv ${1}/kernelz-* ${1}/${x}
		fi

		# change initrd name from "initrd" to "gentoo.igz", for example
		if [ -e ${1}/initrd-* ]
		then
			mv ${1}/initrd-* ${1}/${x}.igz
		fi

		if [ -e ${1}/initramfs-* ]
		then
			mv ${1}/initramfs-* ${1}/${x}.igz
		fi

		if [ -e ${1}/System.map-* ]
		then
			mv ${1}/System.map-* ${1}/System-${x}.map
		fi
	done
}

extract_modules() {
	# $1 = Destination
	# $2 = kname
	kmodules="${clst_chroot_path}/tmp/kerncache/${2}-modules-${clst_version_stamp}.tar.bz2"

	if [ -f "${kmodules}" ]
	then
		mkdir -p ${1}/
		tar -I lbzip2 -xf ${kmodules} --strip-components 1 -C ${1}/lib lib
	else
		echo "Can't find kernel modules tarball at ${kmodules}.  Skipping...."
	fi
}
extract_kernel() {
	# $1 = Destination
	# $2 = kname

	kbinary="${clst_chroot_path}/tmp/kerncache/${2}-kernel-initrd-${clst_version_stamp}.tar.bz2"
	[ ! -e "${kbinary}" ] && die "Can't find kernel tarball at ${kbinary}"
	mkdir -p ${1}/
	tar -I lbzip2 -xf ${kbinary} -C ${1}/
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

check_bootargs(){
	# Add any additional options
	if [ -n "${clst_livecd_bootargs}" ]
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

run_crossdev() {
	crossdev ${clst_CHOST}
}
