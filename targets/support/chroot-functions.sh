#!/bin/bash

# Set the profile
eselect profile set ${clst_target_profile}

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

check_genkernel_version() {
	local version parts=() major minor

	version=$(genkernel --version)
	if [[ -z ${version} ]] ; then
		echo "ERROR: Could not detect genkernel version!"
		exit 1
	fi
	printf 'Genkernel version '%s' found ... ' "${version}"

	IFS='.' read -a parts <<<"${version}"
	major=${parts[0]}
	minor=${parts[1]}
	if [[ ${major} -gt 3 || ( ${major} -eq 3 && ${minor} -ge 3 ) ]] ; then
		echo "OK"
	else
		echo "FAIL"
		echo "ERROR: Your genkernel version is too low in your seed stage."
		echo "       genkernel version 3.3.0 or greater is required."
		exit 1
	fi
}

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
	export features="-news binpkg-multi-instance clean-logs parallel-install"
	export FEATURES="${features}"
	if [ -n "${clst_CCACHE}" ]
	then
		export features="${features} ccache"
		clst_root_path=/ run_merge --oneshot --noreplace dev-util/ccache || exit 1
	fi

	if [ -n "${clst_DISTCC}" ]
	then
		export features="${features} distcc"
		export DISTCC_HOSTS="${clst_distcc_hosts}"
		[ -e ${clst_make_conf} ] && \
			echo 'USE="${USE} -avahi -gtk -gnome"' >> ${clst_make_conf}
		# We install distcc to / on stage1, then use --noreplace, so we need to
		# have some way to check if we need to reinstall distcc without being
		# able to rely on USE, so we check for the distcc user and force a
		# reinstall if it isn't found.
		if [ "$(getent passwd distcc | cut -d: -f1)" != "distcc" ]
		then
			clst_root_path=/ run_merge --oneshot sys-devel/distcc || exit 1
		else
			clst_root_path=/ run_merge --oneshot --noreplace sys-devel/distcc || exit 1
		fi
		sed -i '/USE="${USE} -avahi -gtk -gnome"/d' ${clst_make_conf}
		mkdir -p /etc/distcc
		echo "${clst_distcc_hosts}" > /etc/distcc/hosts

		# This sets up automatic cross-distcc-fu according to
		# https://wiki.gentoo.org/wiki/Distcc/Cross-Compiling
		CHOST=$(portageq envvar CHOST)
		LIBDIR=$(get_libdir)
		cd /usr/${LIBDIR}/distcc/bin
		rm cc gcc g++ c++ 2>/dev/null
		echo -e '#!/bin/bash\nexec /usr/'${LIBDIR}'/distcc/bin/'${CHOST}'-g${0:$[-2]} "$@"' > ${CHOST}-wrapper
		chmod a+x /usr/${LIBDIR}/distcc/bin/${CHOST}-wrapper
		for i in cc gcc g++ c++; do ln -s ${CHOST}-wrapper ${i}; done
	fi

	if [ -n "${clst_ICECREAM}" ]
	then
		clst_root_path=/ run_merge --oneshot --noreplace sys-devel/icecream || exit 1

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
	export FEATURES="${features}"
}

setup_emerge_opts() {
	if [[ "${clst_VERBOSE}" == "true" ]]
	then
		emerge_opts="--verbose"
		bootstrap_opts="${bootstrap_opts} -v"
	else
		emerge_opts="--quiet"
		bootstrap_opts="${bootstrap_opts} -q"
	fi
	if [ -n "${clst_FETCH}" ]
	then
		export bootstrap_opts="${bootstrap_opts} -f"
		export emerge_opts="${emerge_opts} -f"
	# if we have PKGCACHE, and either update_seed is empty or 'no', make and use binpkgs
	elif [ -n "${clst_PKGCACHE}" ] && [ -z "${clst_update_seed}" -o "${clst_update_seed}" = "no" ]
	then
		export emerge_opts="${emerge_opts} --usepkg --buildpkg --binpkg-respect-use=y --newuse"
		export bootstrap_opts="${bootstrap_opts} -r"
	fi
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
	LIBDIR=$(get_libdir)
	rm -rf /etc/distcc/hosts
	for i in cc gcc c++ g++; do
		rm -f /usr/${LIBDIR}/distcc/bin/${i}
		ln -s /usr/bin/distcc /usr/${LIBDIR}/distcc/bin/${i}
	done
	rm -f /usr/${LIBDIR}/distcc/bin/*-wrapper
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
	make_destpath
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

make_destpath() {
	# ROOT is / by default, so remove any ROOT= settings from make.conf
	sed -i '/ROOT=/d' ${clst_make_conf}
	export ROOT=/
	if [ "${1}" != "/" -a -n "${1}" ]
	then
		echo "ROOT=\"${1}\"" >> ${clst_make_conf}
		export ROOT=${1}
	fi
	if [ ! -d ${ROOT} ]
	then
		install -d ${ROOT}
	fi
}

run_merge() {
	# Sets up the ROOT= parameter
	# with no options ROOT=/
	make_destpath ${clst_root_path}

	export EMERGE_WARNING_DELAY=0
	export CLEAN_DELAY=0
	export EBEEP_IGNORE=0
	export EPAUSE_IGNORE=0
	[[ $CONFIG_PROTECT != "-*"* ]] && export CONFIG_PROTECT="-*"

	if [[ "${clst_VERBOSE}" == "true" ]]
	then
		echo "ROOT=${ROOT} emerge ${emerge_opts} -pt $@" || exit 1
		emerge ${emerge_opts} -pt $@ || exit 3
	fi

	echo "emerge ${emerge_opts} $@" || exit 1

	emerge ${emerge_opts} $@ || exit 1
}

show_debug() {
	if [ "${clst_DEBUG}" = "1" ]
	then
		unset PACKAGES
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

run_default_funcs() {
	if [ "${RUN_DEFAULT_FUNCS}" != "no" ]
	then
		update_env_settings
		setup_features
		show_debug
	fi
}

# Functions
# Copy libs of a executable in the chroot
function copy_libs() {
	# Check if it's a dynamix exec
	ldd ${1} > /dev/null 2>&1 || return

	for lib in `ldd ${1} | awk '{ print $3 }'`
	do
		echo ${lib}
		if [ -e ${lib} ]
		then
			if [ ! -e ${clst_root_path}/${lib} ]
			then
				copy_file ${lib}
				[ -e "${clst_root_path}/${lib}" ] && \
				strip -R .comment -R .note ${clst_root_path}/${lib} \
				|| echo "WARNING : Cannot strip lib ${clst_root_path}/${lib} !"
			fi
		else
			echo "WARNING : Some library was not found for ${lib} !"
		fi
	done
}

function copy_symlink() {
	STACK=${2}
	[ "${STACK}" = "" ] && STACK=16 || STACK=$((${STACK} - 1 ))

	if [ ${STACK} -le 0 ]
	then
		echo "WARNING : ${TARGET} : too many levels of symbolic links !"
		return
	fi

	[ ! -e ${clst_root_path}/`dirname ${1}` ] && \
		mkdir -p ${clst_root_path}/`dirname ${1}`
	[ ! -e ${clst_root_path}/${1} ] && \
		cp -vfdp ${1} ${clst_root_path}/${1}

	if [[ -n $(type -p realpath) ]]; then
		TARGET=`realpath ${1}`
	else
		TARGET=`readlink -f ${1}`
	fi
	if [ -h ${TARGET} ]
	then
		copy_symlink ${TARGET} ${STACK}
	else
		copy_file ${TARGET}
	fi
}

function copy_file() {
	f="${1}"

	if [ ! -e "${f}" ]
	then
		echo "WARNING : File not found : ${f}"
		continue
	fi

	[ ! -e ${clst_root_path}/`dirname ${f}` ] && \
		mkdir -p ${clst_root_path}/`dirname ${f}`
	[ ! -e ${clst_root_path}/${f} ] && \
		cp -vfdp ${f} ${clst_root_path}/${f}
	if [ -x ${f} -a ! -h ${f} ]
	then
		copy_libs ${f}
		strip -R .comment -R .note ${clst_root_path}/${f} > /dev/null 2>&1
	elif [ -h ${f} ]
	then
		copy_symlink ${f}
	fi
}

create_handbook_icon() {
	# This function creates a local icon to the Gentoo Handbook
	echo "[Desktop Entry]
Encoding=UTF-8
Version=1.0
Type=Link
URL=file:///mnt/cdrom/docs/handbook/html/index.html
Terminal=false
Name=Gentoo Linux Handbook
GenericName=Gentoo Linux Handbook
Comment=This is a link to the local copy of the Gentoo Linux Handbook.
Icon=text-editor" > /usr/share/applications/gentoo-handbook.desktop
}

readonly locales="
C.UTF8 UTF-8
"

# We do this everywhere, so why not put it in this script
run_default_funcs
