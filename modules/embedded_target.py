# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/embedded_target.py,v 1.10 2005/04/14 14:59:48 rocket Exp $

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

	self.set_build_kernel_vars(addlargs)

	generic_stage_target.__init__(self,spec,addlargs)
	self.settings["image_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]+"/image"	
    def build_fs(self):
        try:
            if self.settings.has_key("embedded/fs-type"):
                cmd("/bin/bash "+self.settings["controller_file"]+" package","filesystem packaging failed")
        except CatalystError:
                self.unbind()
                raise CatalystError, "embedded filesystem creation aborting due to error."

    # this code is mostly duplication from the livecd stage2 module
    def pre_build_fs(self):
    	try:
		if self.settings.has_key("embedded/fs-prepare"):
			cmd("/bin/bash "+self.settings["embedded/fs-prepare"], "pre filesystem packaging cause an error in execution")
	except CatalystError:
		self.unbind()
		raise CatalystError, "embedded pre filesystem creation script aborting due to error"

    def post_build_fs(self):
    	try:
		if self.settings.has_key("embedded/fs-finish"):
			cmd("/bin/bash "+self.settings["embedded/fs-finish"], "pre filesystem packaging cause an error in execution")
	except CatalystError:
		self.unbind()
		raise CatalystError, "embedded post filesystem creation script aborting due to error"

    def set_action_sequence(self):
	self.settings["action_sequence"]=["dir_setup","unpack","unpack_snapshot",\
					"config_profile_link","setup_confdir","bind","chroot_setup",\
					"setup_environment","build_packages","build_kernel","unmerge","unbind",\
					"remove","empty","clean","pre_build_fs","build_fs","post_build_fs","clear_autoresume"]

    def set_stage_path(self):
        self.settings["stage_path"]=self.settings["chroot_path"]+"/tmp/mergeroot"
	print "embedded stage path is "+self.settings["stage_path"]

    def set_root_path(self):
        self.settings["root_path"]="/tmp/mergeroot"
	print "embedded root path is "+self.settings["root_path"]
    def set_dest_path(self):
	self.settings["destpath"]=self.settings["chroot_path"]+self.settings["root_path"]
		
    def set_target_path(self):
	self.settings["target_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]

def register(foo):
        foo.update({"embedded":embedded_target})
        return foo
