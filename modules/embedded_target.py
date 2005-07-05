# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/embedded_target.py,v 1.13 2005/07/05 21:53:41 wolf31o2 Exp $

"""
This class works like a 'stage3'.  A stage2 tarball is unpacked, but instead
of building a stage3, it emerges a 'system' into another directory
inside the 'stage2' system.  This way we do not have to emerge gcc/portage
into the staged system.

It sounds real complicated but basically it runs
ROOT=/tmp/submerge emerge --blahblah foo bar
"""

import os,string,imp,types,shutil
from catalyst_support import *
from generic_stage_target import *
from stat import *

class embedded_target(generic_stage_target):

    def __init__(self,spec,addlargs):
        self.required_values=[]
        self.valid_values=[]
        self.valid_values.extend(["embedded/empty","embedded/rm","embedded/unmerge","embedded/fs-prepare","embedded/fs-finish","embedded/mergeroot","embedded/packages","embedded/use","embedded/fs-type","embedded/runscript","boot/kernel"])

        if addlargs.has_key("embedded/fs-type"):
            self.valid_values.append("embedded/fs-ops")

	generic_stage_target.__init__(self,spec,addlargs)
	self.set_build_kernel_vars(addlargs)

    def set_action_sequence(self):
	self.settings["action_sequence"]=["dir_setup","unpack","unpack_snapshot",\
					"config_profile_link","setup_confdir",\
					"portage_overlay","bind","chroot_setup",\
					"setup_environment","build_kernel","build_packages",\
					"bootloader","root_overlay","fsscript","unmerge",\
					"unbind","remove","empty","clean","capture","clear_autoresume"]

    def set_stage_path(self):
        self.settings["stage_path"]=self.settings["chroot_path"]+"/tmp/mergeroot"
	print "embedded stage path is "+self.settings["stage_path"]

    def set_root_path(self):
        self.settings["root_path"]="/tmp/mergeroot"
	print "embedded root path is "+self.settings["root_path"]

    def set_dest_path(self):
	self.settings["destpath"]=self.settings["chroot_path"]+self.settings["root_path"]
		
def register(foo):
        foo.update({"embedded":embedded_target})
        return foo
