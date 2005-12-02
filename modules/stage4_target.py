# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/stage4_target.py,v 1.12 2005/12/02 20:09:03 wolf31o2 Exp $

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

	def set_pkgcache_path(self):
	    if self.settings.has_key("pkgcache_path"):	
		if type(self.settings["pkgcache_path"]) != types.StringType:
		    self.settings["pkgcache_path"]=normpath(string.join(self.settings["pkgcache_path"]))
	    else:
		generic_stage_target.set_pkgcache_path(self)

	def set_cleanables(self):
		self.settings["cleanables"]=["/var/tmp/*","/tmp/*"]

	def set_action_sequence(self):
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
					"config_profile_link","setup_confdir","portage_overlay",\
					"bind","chroot_setup","setup_environment","build_packages",\
					"build_kernel","bootloader","root_overlay","fsscript",
					"preclean","rcupdate","unmerge","unbind","remove","empty",\
					"clean","capture", "clear_autoresume"]

def register(foo):
	foo.update({"stage4":stage4_target})
	return foo

