# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/stage4_target.py,v 1.1 2005/04/04 17:48:33 rocket Exp $

"""
Builder class for LiveCD stage1.
"""

from catalyst_support import *
from generic_stage_target import *

class stage4_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["stage4/packages","stage4/use"]
		self.valid_values=self.required_values[:]
		self.valid_values.append("stage4/root_overlay")
		generic_stage_target.__init__(self,spec,addlargs)
	
	def set_use(self):
	            self.settings["use"]=self.settings["stage4/use"]

	def set_action_sequence(self):
		self.settings["action_sequence"]=["dir_setup","unpack","unpack_snapshot",\
					"config_profile_link","setup_confdir","portage_overlay",\
					"bind","chroot_setup","setup_environment",\
					"root_overlay","build_packages","preclean","clear_autoresume",\
					"unmerge","unbind","remove","empty","clean","capture"]


def register(foo):
	foo.update({"stage4":stage4_target})
	return foo
