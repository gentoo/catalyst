#!/bin/bash
# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/targets/netboot/netboot-combine.sh,v 1.2 2005/01/11 15:22:41 zhen Exp $

/usr/sbin/env-update
source /etc/profile

[ -f /tmp/envscript ] && source /tmp/envscript

# First install the boot package that we need
booter=""
case ${clst_mainarch} in
	alpha)	booter="";;
	arm)	booter="";;
	hppa)	booter=palo;;
	sparc*)	booter=sparc-utils;;
	x86)	booter=netboot;;
	*)		exit 1;;
esac
if [ ! -z "${booter}" ] ; then
	emerge -k -b ${booter} || exit 1
fi

# Then generate the netboot image ! :D
case ${clst_mainarch} in
	alpha)
		make \
			-C /usr/src/linux \
			INITRD=/initrd.gz \
			HPATH="/usr/src/linux/include" \
			vmlinux bootpfile \
			|| exit 1
		cp /usr/src/linux/arch/alpha/boot/bootpfile /netboot.alpha || exit 1
		;;
	arm)
		cp /kernel /netboot.arm || exit 1
		cat /initrd.gz >> /netboot.arm || exit 1
		#make \
		#	-C /usr/src/linux \
		#	INITRD=/initrd.gz \
		#	bootpImage \
		#	|| exit 1
		;;
	hppa)
		# We have to remove the previous image because the file is considered
		# as a tape by palo and then not truncated but rewritten.
		rm -f /netboot.hppa
		
		palo \
			-k /kernel \
			-r /initrd.gz \
			-s /netboot.hppa \
			-f foo \
			-b /usr/share/palo/iplboot \
			-c "0/vmlinux root=/dev/ram0 initrd=/initrd" \
			|| exit 1
		;;
	sparc*)
		elftoaout -o /netboot.${clst_mainarch} /usr/src/linux/vmlinux
		piggy=${clst_mainarch/sparc/piggyback}
		${piggy} /netboot.${clst_mainarch} /usr/src/linux/System.map initrd.gz
		;;
	x86)
		mknbi-linux \
			-k /kernel \
			-r /initrd.gz \
			-o /netboot.x86 \
			-x \
			-a "root=/dev/ram0 initrd=/initrd" \
			|| exit 1
		;;
	*)	exit 1;;
esac
