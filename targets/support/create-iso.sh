#!/bin/bash

source ${clst_shdir}/support/functions.sh

## START RUNSCRIPT

# Check for our CD ISO creation tools
case ${clst_hostarch} in
	alpha)
		cdmaker="xorriso"
		cdmakerpkg="dev-libs/libisoburn"
		;;
	mips)
		cdmaker="sgibootcd"
		cdmakerpkg="sys-boot/sgibootcd"
		;;
	ppc*|powerpc*|sparc*)
		cdmaker="grub-mkrescue"
		cdmakerpkg="dev-libs/libisoburn and sys-boot/grub:2"
		;;
	amd64|arm64|ia64|x86|i?86)
		cdmaker="grub-mkrescue"
		# grub-mkrescue requires:
		#  xorriso from libisoburn
		#  mkisofs from cdrtools
		#  mformat from mtools
		cdmakerpkg="sys-fs/mtools, dev-libs/libisoburn, sys-boot/grub:2, and app-cdr/cdrtools"
		;;
	*)
		cdmaker="mkisofs"
		cdmakerpkg="app-cdr/cdrtools"
		;;
esac

[ ! -f /usr/bin/${cdmaker} ] \
   && echo && echo && die \
   "!!! /usr/bin/${cdmaker} is not found.  Have you merged ${cdmakerpkg}?" \
   && echo && echo

# If not volume ID is set, make up a sensible default
if [ -z "${clst_iso_volume_id}" ]
then
	case ${clst_livecd_type} in
		gentoo-*)
			case ${clst_hostarch} in
				alpha)
					clst_iso_volume_id="Gentoo Linux - Alpha"
				;;
				amd64)
					clst_iso_volume_id="Gentoo Linux - AMD64"
				;;
				arm)
					clst_iso_volume_id="Gentoo Linux - ARM"
				;;
				arm64)
					clst_iso_volume_id="Gentoo Linux - ARM64"
				;;
				hppa)
					clst_iso_volume_id="Gentoo Linux - HPPA"
				;;
				ia64)
					clst_iso_volume_id="Gentoo Linux - IA64"
				;;
				m68k)
					clst_iso_volume_id="Gentoo Linux - M68K"
				;;
				mips)
					clst_iso_volume_id="Gentoo Linux - MIPS"
				;;
				ppc*|powerpc*)
					clst_iso_volume_id="Gentoo Linux - PowerPC"
				;;
				s390)
					clst_iso_volume_id="Gentoo Linux - S390"
				;;
				sh)
					clst_iso_volume_id="Gentoo Linux - SH"
				;;
				sparc*)
					clst_iso_volume_id="Gentoo Linux - SPARC"
				;;
				x86)
					clst_iso_volume_id="Gentoo Linux - x86"
				;;
				*)
					clst_iso_volume_id="Catalyst LiveCD"
				;;
				esac
	esac
fi

if [ "${#clst_iso_volume_id}" -gt 32 ]; then
	old_clst_iso_volume_id=${clst_iso_volume_id}
	clst_iso_volume_id="${clst_iso_volume_id:0:32}"
	echo "ISO Volume label is too long, truncating to 32 characters" 1>&2
	echo "old: '${old_clst_iso_volume_id}'" 1>&2
	echo "new: '${clst_iso_volume_id}'" 1>&2
fi

# Generate list of checksums that genkernel can use to verify the contents of
# the ISO
isoroot_checksum() {
	[ -z "${clst_livecd_verify}" ] && return

	echo ">> Creating checksums for all files included in the ISO"

	pushd "${clst_target_path}"
	find -type f -exec b2sum {} + > /tmp/isoroot_b2sums
	popd

	mv /tmp/isoroot_b2sums "${clst_target_path}"/
}

run_mkisofs() {
	isoroot_checksum

	echo "Running \"mkisofs ${@}\""
	mkisofs "${@}" || die "Cannot make ISO image"
}

# Here we actually create the ISO images for each architecture
case ${clst_hostarch} in
	alpha)
		isoroot_checksum

		echo ">> xorriso -as genisofs -alpha-boot boot/bootlx -R -l -J -V \"${clst_iso_volume_id}\" -o \"${1}\" \"${clst_target_path}\""
		xorriso -as genisofs -alpha-boot boot/bootlx -R -l -J -V "${clst_iso_volume_id}" -o "${1}" "${clst_target_path}" || die "Cannot make ISO image"
	;;
	arm)
	;;
	hppa)
		echo ">> Running mkisofs to create iso image...."
		run_mkisofs -R -l -J -V "${clst_iso_volume_id}" -o "${1}" "${clst_target_path}"/
		pushd "${clst_target_path}/"
		palo -f boot/palo.conf -C "${1}"
		popd
	;;
	mips)
		if [[ ${clst_fstype} != squashfs ]]; then
			die "SGI LiveCD(s) only support the 'squashfs' fstype!"
		fi

		# $clst_target_path/[kernels|arcload] already exists, create loopback and sgibootcd
		[ ! -d "${clst_target_path}/loopback" ] && mkdir "${clst_target_path}/loopback"
		[ ! -d "${clst_target_path}/sgibootcd" ] && mkdir "${clst_target_path}/sgibootcd"

		# Setup variables
		[ -f "${clst_target_path}/livecd" ] && rm -f "${clst_target_path}/livecd"
		img="${clst_target_path}/loopback/image.squashfs"
		knl="${clst_target_path}/kernels"
		arc="${clst_target_path}/arcload"
		cfg="${clst_target_path}/sgibootcd/sgibootcd.cfg"
		echo "" > "${cfg}"

		# If the image file exists in $clst_target_path, move it to the loopback dir
		[ -e "${clst_target_path}/image.squashfs" ] \
			&& mv -f "${clst_target_path}/image.squashfs" "${clst_target_path}/loopback"

		# An sgibootcd config is essentially a collection of commandline params
		# stored in a text file.  We could pass these on the command line, but it's
		# far easier to generate a config file and pass it to sgibootcd versus using a
		# ton of commandline params.
		#
		# f=	indicates files to go into DVH (disk volume header) in an SGI disklabel
		#	    format: f=</path/to/file>@<DVH name>
		# p0=	the first partition holds the LiveCD rootfs image
		#	    format: p0=</path/to/image>
		# p8=	the eighth partition is the DVH partition
		# p10=	the tenth partition is the disk volume partition
		#	    format: p8= is always "#dvh" and p10= is always "#volume"

		# Add the kernels to the sgibootcd config
		for x in ${clst_boot_kernel}; do
			echo -e "f=${knl}/${x}@${x}" >> ${cfg}
		done

		# Next, the bootloader binaries and config
		echo -e "f=${arc}/sash64@sash64" >> ${cfg}
		echo -e "f=${arc}/sashARCS@sashARCS" >> ${cfg}
		echo -e "f=${arc}/arc.cf@arc.cf" >> ${cfg}

		# Next, the Loopback Image
		echo -e "p0=${img}" >> ${cfg}

		# Finally, the required SGI Partitions (dvh, volume)
		echo -e "p8=#dvh" >> ${cfg}
		echo -e "p10=#volume" >> ${cfg}

		# All done; feed the config to sgibootcd and end up with an image
		# c=	the config file
		# o=	output image (burnable to CD; readable by fdisk)
		/usr/bin/sgibootcd c=${cfg} o=${clst_iso}
	;;
	amd64|arm64|ia64|ppc*|powerpc*|sparc*|x86|i?86)
		isoroot_checksum

		extra_opts=("-joliet" "-iso-level" "3")
		case ${clst_hostarch} in
		sparc*) extra_opts+=("--sparc-boot") ;;
		esac

		echo ">> Running grub-mkrescue to create iso image...."
		grub-mkrescue -volid "${clst_iso_volume_id}" "${extra_opts[@]}" -o "${1}" "${clst_target_path}"
	;;
esac
exit  $?
