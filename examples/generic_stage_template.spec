# generic installation stage specfile
# used to build a stage1, stage2, or stage3 installation tarball

# The subarch can be any of the supported catalyst subarches (like athlon-xp).
# Refer to the catalyst reference manual for suppurted subarches.
# http://www.gentoo.org/proj/en/releng/catalyst/reference.xml
# example:
# subarch: athlon-xp
subarch:

# The version stamp is an identifier for the build.  It can be anything you wish
# it to be, but it is usually a date.
# example:
# version_stamp: 2005.0
version_stamp: 

# The target specifies what target we want catalyst to do. For stages, the
# supported targets are: stage1 stage2 stage3
# example:
# target: stage2
target:

# The rel_type defines what kind of build we are doing.  This is merely another
# identifier, but it useful for allowing multiple concurrent builds.  Usually,
# default will suffice.
# example:
# rel_type: default
rel_type:

# This is the system profile to be used by catalyst to build this target.  It is
# specified as a relative path from /usr/portage/profiles.
# example:
# profile: default-linux/x86/2005.0
profile:

# This specifies which snapshot to use for building this target.
# example:
# snapshot: 20050324
snapshot:

# This specifies where the seed stage comes from for this target,  The path is
# relative to $clst_sharedir/builds.  The rel_type is also used as a path prefix
# for the seed.
# example:
# default/stage3-x86-2004.3
source_subpath:

# These are the hosts used as distcc slaves when distcc is enabled in your 
# catalyst.conf.  It follows the same syntax as distcc-config --set-hosts and
# is entirely optional.
# example:
# distcc_hosts: 127.0.0.1 192.168.0.1
distcc_hosts:

# This is an optional directory containing portage configuration files.  It
# follows the same syntax as /etc/portage and should be consistent across all
# targets to minimize problems.
# example:
# portage_confdir: /etc/portage
portage_confdir:
