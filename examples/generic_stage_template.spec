## generic installation stage specfile
## used to build a stage1, stage2, or stage3 installation tarball

## John Davis <zhen@gentoo.org>

# subarch can be any of the supported Catalyst subarches (like athlon-xp). Refer
# to the catalyst reference manual (http://www.gentoo.org/proj/en/releng/catalyst) for supported arches.
# example:
# subarch: athlon-xp
subarch:

# version stamp is an identifier for the build. can be anything you want it to be, but it
# is usually a date.
# example:
# version_stamp: 2004.2
version_stamp: 

# target specifies what type of build Catalyst is to do. check the catalyst reference manual
# for supported targets.
# example:
# target: stage2
target:

# rel_type defines what kind of build we are doing. usually, default will suffice.
# example:
# rel_type: default
rel_type:

# system profile used to build the media
# example:
# profile: default-x86-2004.0
profile:

# which snapshot to use
# example:
# snapshot: 20040614
snapshot:

# where the seed stage comes from, path is relative to $clst_sharedir (catalyst.conf)
# example:
# default/stage3-x86-2004.1
source_subpath:
