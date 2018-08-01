#!/bin/bash

if [ "${clst_spec_prefix}" == "livecd" ]
then
	rc-update --all del iptables
	rc-update --all del netmount
	rc-update --all del keymaps
	rc-update --all del serial
	rc-update --all del consolefont
	# We need to add this one, unconditionally
	rc-update add autoconfig default
	[[ -e /etc/init.d/splash ]] && rc-update add splash default
	[[ -e /etc/init.d/fbcondecor ]] && rc-update add fbcondecor default
	[[ -e /etc/init.d/sysklogd ]] && rc-update add sysklogd default
	[[ -e /etc/init.d/metalog ]] && rc-update add metalog default
	[[ -e /etc/init.d/syslog-ng ]] && rc-update add syslog-ng default
	[[ -e /etc/init.d/fixinittab ]] && rc-update add fixinittab default

	# Do some livecd_type specific rc-update changes
	case ${clst_livecd_type} in
		gentoo-gamecd)
			rc-update add spind default
			;;
		gentoo-release-live*)
			rc-update add spind default
			rc-update add xdm default
			;;
		generic-livecd)
			rc-update add spind default
			;;
	esac
fi

# Perform any rcadd then any rcdel
if [ -n "${clst_rcadd}" ] || [ -n "${clst_rcdel}" ]
then
	if [ -n "${clst_rcadd}" ]
	then
		for x in ${clst_rcadd}
		do
			echo "Adding ${x%%|*} to ${x##*|}"
			if [ ! -d /etc/runlevels/${x##*|} ]
			then
				echo "Runlevel ${x##*|} doesn't exist .... creating it"
				mkdir -p "/etc/runlevels/${x##*|}"
			fi
			rc-update add "${x%%|*}" "${x##*|}"
		done
	fi

	if [ -n "${clst_rcdel}" ]
	then
		for x in ${clst_rcdel}
		do
			rc-update del "${x%%|*}" "${x##*|}"
		done
	fi
fi
