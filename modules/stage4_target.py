# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/stage4_target.py,v 1.2 2005/04/11 20:05:40 rocket Exp $

"""
Builder class for LiveCD stage1.
"""

from catalyst_support import *
from generic_stage_target import *

class stage4_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		#self.required_values=["stage4/use"]
		self.required_values=[]
		self.valid_values=self.required_values[:]
		self.valid_values.extend(["stage4/use", "stage4/packages", "stage4/root_overlay", "stage4/fsscript", \
					     "stage4/rcadd","stage4/rcdel"])
		generic_stage_target.__init__(self,spec,addlargs)
	
	def set_use(self):
		if self.settings.has_key("use"):
			self.settings["use"]=self.settings["stage4/use"]
		else:
			pass
	def set_cleanables(self):
		self.settings["cleanables"]=["/var/tmp/*","/tmp/*"]

	def set_action_sequence(self):
		self.settings["action_sequence"]=["dir_setup","unpack","unpack_snapshot",\
					"config_profile_link","setup_confdir","portage_overlay",\
					"bind","chroot_setup","setup_environment","build_packages",\
					"build_kernel","root_overlay","preclean","rcupdate","fsscript",\
					"clear_autoresume","unmerge","unbind","remove","empty",\
					"clean","capture"]

def register(foo):
	foo.update({"stage4":stage4_target})
	return foo
