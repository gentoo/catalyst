# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/livecd_stage1_target.py,v 1.8 2005/04/11 20:05:40 rocket Exp $

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
					"preclean","fsscript","clear_autoresume","unmerge","unbind",\
					"remove","empty","clean"]


	def set_use(self):
	            self.settings["use"]=self.settings["livecd/use"]

        def set_spec_prefix(self):
	                self.settings["spec_prefix"]="livecd"
def register(foo):
	foo.update({"livecd-stage1":livecd_stage1_target})
	return foo
