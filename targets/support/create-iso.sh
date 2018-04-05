#!/bin/bash

source ${clst_shdir}/support/functions.sh
source ${clst_shdir}/support/filesystem-functions.sh

## START RUNSCRIPT

# Check for our CD ISO creation tools
case ${clst_hostarch} in
	alpha)
		cdmaker="genisoimage"
		cdmakerpkg="app-cdr/cdrkit"
		;;
	mips)
   		cdmaker="sgibootcd"
		cdmakerpkg="sys-boot/sgibootcd"
		;;
	*)
		cdmaker="mkisofs"
		cdmakerpkg="app-cdr/cdrkit or app-cdr/cdrtools"
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

if [ "${clst_fstype}" == "zisofs" ]
then
	mkisofs_zisofs_opts="-z"
else
	mkisofs_zisofs_opts=""
fi

#we want to create a sha512sum for every file on the iso so we can verify it
#from genkernel during boot.  Here we make a function to create the sha512sums
isoroot_checksum() {
	echo "Creating checksums for all files included in the iso, please wait..."
	find "${clst_target_path}" -type f ! -name 'isoroot_checksums' ! -name 'isolinux.bin' -exec sha512sum {} + > "${clst_target_path}"/isoroot_checksums
	${clst_sed} -i "s#${clst_target_path}/\?##" "${clst_target_path}"/isoroot_checksums
}

run_mkisofs() {
	[ -n "${clst_livecd_verify}" ] && isoroot_checksum
	echo "Running \"mkisofs ${@}\""
	mkisofs "${@}" || die "Cannot make ISO image"
}

# Here we actually create the ISO images for each architecture
case ${clst_hostarch} in
	alpha)
		echo ">> genisoimage --alpha-boot=boot/bootlx -R -l -J ${mkisofs_zisofs_opts} -V \"${clst_iso_volume_id}\" -o ${1} ${clst_target_path}"
		genisoimage --alpha-boot=boot/bootlx -R -l -J ${mkisofs_zisofs_opts} -V "${clst_iso_volume_id}" -o "${1}" "${clst_target_path}" || die "Cannot make ISO image"
	;;
	arm)
	;;
	hppa)
		echo ">> Running mkisofs to create iso image...."
		run_mkisofs -R -l -J ${mkisofs_zisofs_opts} -V "${clst_iso_volume_id}" -o "${1}" "${clst_target_path}"/
		pushd "${clst_target_path}/"
		palo -f boot/palo.conf -C "${1}"
		popd
	;;
	ia64)
		if [ ! -e "${clst_target_path}/gentoo.efimg" ]
		then
			iaSizeTemp=$(du -sk "${clst_target_path}/boot" 2>/dev/null)
			iaSizeB=$(echo ${iaSizeTemp} | cut '-d ' -f1)
			iaSize=$((${iaSizeB}+32)) # Add slack

			dd if=/dev/zero of="${clst_target_path}/gentoo.efimg" bs=1k \
				count=${iaSize}
			mkfs.vfat -F 16 -n GENTOO "${clst_target_path}/gentoo.efimg"

			mkdir "${clst_target_path}/gentoo.efimg.mountPoint"
			mount -t vfat -o loop "${clst_target_path}/gentoo.efimg" \
				"${clst_target_path}/gentoo.efimg.mountPoint"

			echo '>> Populating EFI image...'
			cp -rv "${clst_target_path}"/boot/* \
				"${clst_target_path}/gentoo.efimg.mountPoint"

			umount "${clst_target_path}/gentoo.efimg.mountPoint"
			rmdir "${clst_target_path}/gentoo.efimg.mountPoint"
		else
			echo ">> Found populated EFI image at \
				${clst_target_path}/gentoo.efimg"
		fi
		echo '>> Removing /boot...'
		rm -rf "${clst_target_path}/boot"

		echo ">> Running mkisofs to create iso image...."
		run_mkisofs -R -l -b gentoo.efimg -c boot.cat -no-emul-boot -J ${mkisofs_zisofs_opts} -V "${clst_iso_volume_id}" -o "${1}" "${clst_target_path}"/
	;;
	mips)
		case ${clst_fstype} in
			squashfs)
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
			*) die "SGI LiveCD(s) only support the 'squashfs' fstype!"	;;
		esac
	;;
	ppc*|powerpc*)
		if [ -f "${clst_target_path}/ppc/bootinfo.txt" ]
		then
			echo "bootinfo.txt found .. updating it"
			${clst_sed} -i -e \
			's#^<description>.*</description>$#<description>'"${clst_iso_volume_id}"'</description>#' \
			"${clst_target_path}/ppc/bootinfo.txt"
			${clst_sed} -i -e \
			's#^<os-name>.*</os-name>$#<os-name>'"${clst_iso_volume_id}"'</os-name>#' \
			"${clst_target_path}/ppc/bootinfo.txt"
		fi

		flags=( -r -U -chrp-boot )
		echo ">> Running mkisofs to create iso image...."
		if [[ ${clst_subarch} == *le ]]
		then
			flags+=(
				-v -T -l -cache-inodes
			)
		else
			flags+=(
				-netatalk -hfs -probe -map "${clst_target_path}"/boot/map.hfs
				-part -no-desktop -hfs-volid "${clst_iso_volume_id}" -hfs-bless "${clst_target_path}"/boot -hide-hfs
				"zisofs" -hide-hfs "stages" -hide-hfs "distfiles" -hide-hfs "snapshots" -J ${mkisofs_zisofs_opts}
			)
		fi
		run_mkisofs "${flags[@]}" \
			-V "${clst_iso_volume_id}" -o "${1}" "${clst_target_path}"
	;;
	sparc*)
		# Old silo (<=1.2.6) requires a specially built mkisofs
		# We try to autodetect this in a simple way, said mkisofs
		# should be in the cdtar, otherwise use the new style.
		if [ -x "${clst_target_path}/boot/mkisofs.sparc.fu" ]
		then
			mv "${clst_target_path}/boot/mkisofs.sparc.fu" /tmp
			echo "Running mkisofs.sparc.fu to create iso image...."
			echo "/tmp/mkisofs.sparc.fu ${mkisofs_zisofs_opts} -o ${1} -D -r -pad -quiet -S 'boot/cd.b' -B '/boot/second.b' -s '/boot/silo.conf' -V \"${clst_iso_volume_id}\" ${clst_target_path}/"
			/tmp/mkisofs.sparc.fu ${mkisofs_zisofs_opts} -o "${1}" -D -r -pad -quiet -S 'boot/cd.b' -B '/boot/second.b' -s '/boot/silo.conf' -V "${clst_iso_volume_id}" "${clst_target_path}"/ || die "Cannot make ISO image"
			rm /tmp/mkisofs.sparc.fu
		else
			echo "Running mkisofs to create iso image...."
			run_mkisofs -J -R -l ${mkisofs_zisofs_opts} -V "${clst_iso_volume_id}" -o "${1}" -G "${clst_target_path}/boot/isofs.b" -B ... "${clst_target_path}"/
		fi

	;;
	x86|amd64)
		# detect if an EFI bootloader is desired
		if 	[ -d "${clst_target_path}/boot/efi" ] || \
			[ -d "${clst_target_path}/boot/EFI" ] || \
			[ -e "${clst_target_path}/gentoo.efimg" ]
		then
			if [ -e "${clst_target_path}/gentoo.efimg" ]
			then
				echo "Found prepared EFI boot image at \
					${clst_target_path}/gentoo.efimg"
				# /boot must exist and be empty for later logic
				echo "Removing /boot contents"
				rm -rf "${clst_target_path}"/boot
				mkdir -p "${clst_target_path}"/boot
			else
				echo "Preparing EFI boot image"
				# prepare gentoo.efimg from clst_target_path /boot/EFI dir
				iaSizeTemp=$(du -sk "${clst_target_path}/boot/EFI" 2>/dev/null)
				iaSizeB=$(echo ${iaSizeTemp} | cut '-d ' -f1)
				iaSize=$((${iaSizeB}+32)) # Add slack
				echo "Creating loopback file of size ${iaSize}kB"
				dd if=/dev/zero of="${clst_target_path}/gentoo.efimg" bs=1k \
					count=${iaSize}
				echo "Formatting loopback file with FAT16 FS"
				mkfs.vfat -F 16 -n GENTOO "${clst_target_path}/gentoo.efimg"

				mkdir "${clst_target_path}/gentoo.efimg.mountPoint"
				echo "Mounting FAT16 loopback file"
				mount -t vfat -o loop "${clst_target_path}/gentoo.efimg" \
					"${clst_target_path}/gentoo.efimg.mountPoint"

				echo "Populating EFI image file from ${clst_target_path}/boot/EFI"
				cp -rv "${clst_target_path}"/boot/EFI/ \
					"${clst_target_path}/gentoo.efimg.mountPoint"

				umount "${clst_target_path}/gentoo.efimg.mountPoint"
				rmdir "${clst_target_path}/gentoo.efimg.mountPoint"

				echo "Removing /boot contents"
				rm -rf "${clst_target_path}"/boot
				mkdir -p "${clst_target_path}"/boot
			fi
		fi

		if [ -e "${clst_target_path}/isolinux/isolinux.bin" ]
		then
			echo "** Found ISOLINUX bootloader"
			if [ -d "${clst_target_path}/boot" ]
			then
				if [ -n "$(ls ${clst_target_path}/boot)" ]
				# have stray files in /boot, assume ISOLINUX only
				then
					echo "** boot dir not empty, moving files to isolinux/ then removing it"
					mv "${clst_target_path}"/boot/* "${clst_target_path}/isolinux"
					rm -r "${clst_target_path}/boot"
					echo "Creating ISO using ISOLINUX bootloader"
					run_mkisofs -J -R -l ${mkisofs_zisofs_opts} -V "${clst_iso_volume_id}" -o "${1}" -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table "${clst_target_path}"/
					isohybrid "${1}"
				elif [ -e "${clst_target_path}/gentoo.efimg" ]
				# have BIOS isolinux, plus an EFI loader image
				then
					echo "Creating ISO using both ISOLINUX and EFI bootloader"
					run_mkisofs -J -R -l ${mkisofs_zisofs_opts} -V "${clst_iso_volume_id}" -o "${1}" -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -eltorito-alt-boot -eltorito-platform efi -b gentoo.efimg -no-emul-boot -z "${clst_target_path}"/
					isohybrid --uefi "${1}"
				fi
			else
				echo "Creating ISO using ISOLINUX bootloader"
				run_mkisofs -J -R -l ${mkisofs_zisofs_opts} -V "${clst_iso_volume_id}" -o "${1}" -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table "${clst_target_path}"/
				isohybrid "${1}"
			fi
		elif [ -e "${clst_target_path}/boot/grub/stage2_eltorito" ]
		then
			echo "Creating ISO using GRUB bootloader"
			run_mkisofs -J -R -l ${mkisofs_zisofs_opts} -V "${clst_iso_volume_id}" -o "${1}" -b boot/grub/stage2_eltorito -c boot/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table "${clst_target_path}"/
		elif [ -e "${clst_target_path}/gentoo.efimg" ]
		then
			echo 'Creating ISO using EFI bootloader'
			run_mkisofs -J -R -l ${mkisofs_zisofs_opts} -V "${clst_iso_volume_id}" -o "${1}" -b gentoo.efimg -c boot.cat -no-emul-boot "${clst_target_path}"/
		else
			run_mkisofs -J -R -l ${mkisofs_zisofs_opts} -V "${clst_iso_volume_id}" -o "${1}" "${clst_target_path}"/
		fi
	;;
esac
exit  $?
