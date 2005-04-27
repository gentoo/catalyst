# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/livecd_stage1_target.py,v 1.12 2005/04/27 17:44:58 rocket Exp $

"""
Builder class for LiveCD stage1.
"""

from catalyst_support import *
from generic_stage_target import *

class livecd_stage1_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["livecd/packages","livecd/use"]
		self.valid_values=self.required_values[:]
		generic_stage_target.__init__(self,spec,addlargs)

	def set_action_sequence(self):
		self.settings["action_sequence"]=["dir_setup","unpack","unpack_snapshot",\
					"config_profile_link","setup_confdir","portage_overlay",\
					"bind","chroot_setup","setup_environment","build_packages",\
					"unbind", "clean","clear_autoresume"]
        def set_target_path(self):
		self.settings["target_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["autoresume_path"]+"setup_target_path"):
				print "Resume point detected, skipping target path setup operation..."
		else:
			# first clean up any existing target stuff
			if os.path.exists(self.settings["target_path"]):
				cmd("rm -rf "+self.settings["target_path"],\
					"Could not remove existing directory: "+self.settings["target_path"])
				touch(self.settings["autoresume_path"]+"setup_target_path")
			
			if not os.path.exists(self.settings["target_path"]):
				os.makedirs(self.settings["target_path"])
        
	
	def set_target_path(self):
		pass
	def set_spec_prefix(self):
	                self.settings["spec_prefix"]="livecd"
	
	def set_packages(self):
	    generic_stage_target.set_packages(self)
	    if self.settings.has_key(self.settings["spec_prefix"]+"/packages"):
		self.settings[self.settings["spec_prefix"]+"/packages"].append("livecd-tools")

def register(foo):
	foo.update({"livecd-stage1":livecd_stage1_target})
	return foo
