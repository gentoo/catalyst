#!/bin/bash

# Trap these signals and kill ourselves if received
# Force ourselves to die if any of these signals are received
# most likely our controlling terminal is gone
trap "echo SIGTERM signal received killing $0 with pid $$;kill -9 $$" SIGTERM
trap "echo SIGHUP signal received killing $0 with pid $$;kill -9 $$" SIGHUP
trap "echo SIGKILL signal received killing $0 with pid $$;kill -9 $$" SIGKILL

#SIGINT interrupt character (usually Ctrl-C)
#	* example: high-level sequence of events
#	* my process (call it "P") is running
#	* user types ctrl-c
#	* kernel recognizes this and generates SIGINT signal
trap "echo SIGINT signal received killing $0 with pid $$;kill -9 $$" SIGINT

# test if CHOST was set on the python side
if [[ -z "${clst_CHOST}" ]] ; then
	# No, it wasn't
	if [[ -z "${clst_chost}" ]] ; then
		# No override was set, so grab CHOST from the profile
		export clst_CHOST=$(portageq envvar CHOST)
	else
		# Set CHOST from the spec override
		export clst_CHOST="${clst_chost}"
	fi
fi

get_libdir() {
	ABI=$(portageq envvar ABI)
	DEFAULT_ABI=$(portageq envvar DEFAULT_ABI)
	LIBDIR_default=$(portageq envvar LIBDIR_default)

	local abi
	if [ $# -gt 0 ]
	then
		abi=${1}
	elif [ -n "${ABI}" ]
	then
		abi=${ABI}
	elif [ -n "${DEFAULT_ABI}" ]
	then
		abi=${DEFAULT_ABI}
	else
		abi="default"
	fi

	local var="LIBDIR_${abi}"
	var=$(portageq envvar ${var})
	echo ${var}
}

setup_features() {
	setup_emerge_opts
	local features=(-news binpkg-multi-instance clean-logs parallel-install)
	export FEATURES="${features[@]}"
	if [ -n "${clst_CCACHE}" ]
	then
		features+=(ccache)
		ROOT=/ run_merge --oneshot --noreplace dev-util/ccache
	fi

	if [ -n "${clst_DISTCC}" ]
	then
		features+=(distcc)
		export DISTCC_HOSTS="${clst_distcc_hosts}"
		[ -e ${clst_make_conf} ] && \
			echo 'USE="${USE} -avahi -gtk -gnome"' >> ${clst_make_conf}
		# We install distcc to / on stage1, then use --noreplace, so we need to
		# have some way to check if we need to reinstall distcc without being
		# able to rely on USE, so we check for the distcc user and force a
		# reinstall if it isn't found.
		if [ "$(getent passwd distcc | cut -d: -f1)" != "distcc" ]
		then
			ROOT=/ run_merge --oneshot sys-devel/distcc
		else
			ROOT=/ run_merge --oneshot --noreplace sys-devel/distcc
		fi
		sed -i '/USE="${USE} -avahi -gtk -gnome"/d' ${clst_make_conf}
		mkdir -p /etc/distcc
		echo "${clst_distcc_hosts}" > /etc/distcc/hosts

		# This sets up automatic cross-distcc-fu according to
		# https://wiki.gentoo.org/wiki/Distcc/Cross-Compiling
		CHOST=$(portageq envvar CHOST)
		cd /usr/lib/distcc/bin
		rm cc gcc g++ c++ 2>/dev/null
		echo -e '#!/bin/bash\nexec /usr/lib/distcc/bin/'${CHOST}'-g${0:$[-2]} "$@"' > ${CHOST}-wrapper
		chmod a+x /usr/lib/distcc/bin/${CHOST}-wrapper
		for i in cc gcc g++ c++; do ln -s ${CHOST}-wrapper ${i}; done
	fi

	if [ -n "${clst_ICECREAM}" ]
	then
		ROOT=/ run_merge --oneshot --noreplace sys-devel/icecream

		# This sets up automatic cross-icecc-fu according to
		# http://www.gentoo-wiki.info/HOWTO_Setup_An_ICECREAM_Compile_Cluster
		CHOST=$(portageq envvar CHOST)
		LIBDIR=$(get_libdir)
		cd /usr/${LIBDIR}/icecc/bin
		rm cc gcc g++ c++ 2>/dev/null
		echo -e '#!/bin/bash\nexec /usr/'${LIBDIR}'/icecc/bin/'${CHOST}'-g${0:$[-2]} "$@"' > ${CHOST}-wrapper
		chmod a+x ${CHOST}-wrapper
		for i in cc gcc g++ c++; do ln -s ${CHOST}-wrapper ${i}; done
		export PATH="/usr/lib/icecc/bin:${PATH}"
		export PREROOTPATH="/usr/lib/icecc/bin"
	fi
	export FEATURES="${features[@]}"
}

setup_emerge_opts() {
	emerge_opts=()
	bootstrap_opts=()

	if [ -n "${clst_VERBOSE}" ]
	then
		emerge_opts+=(--verbose)
		bootstrap_opts+=(-v)
	else
		emerge_opts+=(--quiet)
		bootstrap_opts+=(-q)
	fi
	if [ -n "${clst_FETCH}" ]
	then
		emerge_opts+=(--fetchonly)
		bootstrap_opts+=(-f)
	fi
	if [ -n "${clst_jobs}" ]
	then
		emerge_opts+=(--jobs "${clst_jobs}")
	fi
	if [ -n "${clst_load_average}" ]
	then
		emerge_opts+=(--load-average "${clst_load_average}")
	fi

	if [ -n "${clst_PKGCACHE}" ] && [ -z "${clst_update_seed}" -o "${clst_update_seed}" = "no" ]
	then
		emerge_opts+=(--usepkg --buildpkg --binpkg-respect-use=y --newuse)
		bootstrap_opts+=(-r)
	fi

	export emerge_opts
	export bootstrap_opts
}

setup_binutils(){
	if [ -x /usr/bin/binutils-config ]
	then
		my_binutils=$( cd ${ROOT}/etc/env.d/binutils; ls ${clst_CHOST}-* | head -n 1 )
		if [ -z "${my_binutils}" ]
		then
			my_binutils=1
		fi
		binutils-config ${my_binutils}; update_env_settings
	fi
}

setup_gcc(){
	if [ -x /usr/bin/gcc-config ]
	then
		my_gcc=$( cd ${ROOT}/etc/env.d/gcc; ls ${clst_CHOST}-* | head -n 1 )
		if [ -z "${my_gcc}" ]
		then
			my_gcc=1
		fi
		gcc-config ${my_gcc}; update_env_settings
	fi
}

cleanup_distcc() {
	rm -f /etc/distcc/hosts
	for i in cc gcc c++ g++; do
		rm -f /usr/lib/distcc/bin/${i}
		ln -s /usr/bin/distcc /usr/lib/distcc/bin/${i}
	done
	rm -f /usr/lib/distcc/bin/*-wrapper
}

cleanup_icecream() {
	LIBDIR=$(get_libdir)
	for i in cc gcc c++ g++; do
		rm -f /usr/${LIBDIR}/icecc/bin/${i}
		ln -s /usr/bin/icecc /usr/${LIBDIR}/icecc/bin/${i}
	done
	rm -f /usr/${LIBDIR}/icecc/bin/*-wrapper
}

cleanup_stages() {
	if [ -n "${clst_DISTCC}" ]
	then
		cleanup_distcc
	fi
	if [ -n "${clst_ICECREAM}" ]
	then
		cleanup_icecream
	fi
	case ${clst_target} in
		stage3)
			run_merge --depclean --with-bdeps=y
			;;
		*)
			echo "Skipping depclean operation for ${clst_target}"
			;;
	esac
	case ${clst_target} in
		stage1|stage2|stage3)
			rm -f /var/lib/portage/world
			touch /var/lib/portage/world
			;;
		*)
			echo "Skipping removal of world file for ${clst_target}"
			;;
	esac

	# Remove bindist from use
	sed -i "/USE=\"\${USE} bindist\"/d" "${clst_make_conf}"
	sed -i "/USE=\"bindist\"/d" "${clst_make_conf}"

	rm -f /var/log/emerge.log /var/log/portage/elog/*
}

update_env_settings(){
	[ -x /usr/sbin/env-update ] && /usr/sbin/env-update
	source /etc/profile
	[ -f /tmp/envscript ] && source /tmp/envscript
}

die() {
	echo "$1"
	exit 1
}

run_merge() {
	export EMERGE_WARNING_DELAY=0
	export CLEAN_DELAY=0
	[[ $CONFIG_PROTECT != "-*"* ]] && export CONFIG_PROTECT="-*"

	if [ -n "${clst_VERBOSE}" ]
	then
		echo "ROOT=${ROOT} emerge ${emerge_opts[@]} -pt $@" || exit 1
		ROOT="$ROOT" emerge ${emerge_opts[@]} -pt $@ || exit 3
	fi

	echo "emerge ${emerge_opts[@]} $@" || exit 1

	ROOT="$ROOT" emerge ${emerge_opts[@]} $@ || exit 1
}

show_debug() {
	if [ -n "${clst_DEBUG}" ]
	then
		echo "DEBUG:"
		echo "Profile/target info:"
		echo "Profile inheritance:"
		python -c 'import portage; print(portage.settings.profiles)'
		echo
		# TODO: make this work on non-portage
		emerge --info
		# TODO: grab our entire env
		# <zmedico> to get see the ebuild env you can do something like:
		# `set > /tmp/env_dump.${EBUILD_PHASE}` inside ${clst_port_conf}/bashrc
		# XXX: Also, portageq does *not* source profile.bashrc at any time.
		echo
		echo "BOOTSTRAP_USE:            $(portageq envvar BOOTSTRAP_USE)"
		echo
		echo "USE (profile):         $(portageq envvar USE)"
		echo "FEATURES (profile):    $(portageq envvar FEATURES)"
		echo
		echo "ARCH:                  $(portageq envvar ARCH)"
		echo "CHOST:                 $(portageq envvar CHOST)"
		echo "CFLAGS:                $(portageq envvar CFLAGS)"
		echo
		echo "These should be blank on non-multilib profiles."
		echo "ABI:                   $(portageq envvar ABI)"
		echo "DEFAULT_ABI:           $(portageq envvar DEFAULT_ABI)"
		echo "KERNEL_ABI:            $(portageq envvar KERNEL_ABI)"
		echo "LIBDIR:                $(get_libdir)"
		echo "MULTILIB_ABIS:         $(portageq envvar MULTILIB_ABIS)"
		echo "PROFILE_ARCH:          $(portageq envvar PROFILE_ARCH)"
		echo
	fi
}

readonly locales="
C.UTF-8 UTF-8
"

if [[ ${RUN_DEFAULT_FUNCS} != no ]]
then
	update_env_settings
	setup_features
	show_debug
fi
