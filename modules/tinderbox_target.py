# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/tinderbox_target.py,v 1.17 2005/12/02 20:09:03 wolf31o2 Exp $

"""
builder class for the tinderbox target
"""

from catalyst_support import *
from generic_stage_target import *

class tinderbox_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["tinderbox/packages"]
		self.valid_values=self.required_values[:]
		self.valid_values.extend(["tinderbox/use"])
		generic_stage_target.__init__(self,spec,addlargs)

	def run_local(self):
		# tinderbox
		# example call: "grp.sh run xmms vim sys-apps/gleep"
		try:
			if os.path.exists(self.settings["controller_file"]):
			    cmd("/bin/bash "+self.settings["controller_file"]+" run "+\
				list_bashify(self.settings["tinderbox/packages"]),"run script failed.")
		
		except CatalystError:
			self.unbind()
			raise CatalystError,"Tinderbox aborting due to error."

	def set_pkgcache_path(self):
            if self.settings.has_key("pkgcache_path"):
                if type(self.settings["pkgcache_path"]) != types.StringType:
                    self.settings["pkgcache_path"]=normpath(string.join(self.settings["pkgcache_path"]))
            else:
                generic_stage_target.set_pkgcache_path(self)
	
	def set_cleanables(self):
	    self.settings["cleanables"]=["/etc/resolv.conf","/var/tmp/*","/root/*",\
					"/usr/portage"]
	def set_action_sequence(self):
                #Default action sequence for run method
                self.settings["action_sequence"]=["unpack","unpack_snapshot",\
                                "config_profile_link","setup_confdir","bind","chroot_setup",\
                                "setup_environment","run_local","preclean","unbind","clean",\
				"clear_autoresume"]
	
def register(foo):
	foo.update({"tinderbox":tinderbox_target})
	return foo
