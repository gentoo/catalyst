# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/tinderbox_target.py,v 1.4 2004/12/16 23:13:24 wolf31o2 Exp $

"""
builder class for the tinderbox target
"""

from catalyst_support import *
from generic_stage_target import *

class tinderbox_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["tinderbox/packages","tinderbox/use"]
		self.valid_values=self.required_values[:]
		generic_stage_target.__init__(self,spec,addlargs)

	def run_local(self):
		# tinderbox
		# example call: "grp.sh run xmms vim sys-apps/gleep"
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/tinderbox/tinderbox.sh run "+\
				list_bashify(self.settings["tinderbox/packages"]))
		
		except CatalystError:
			self.unbind()
			raise CatalystError,"Tinderbox aborting due to error."
	
	def set_target_path(self):
	    self.settings["target_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]
	def set_use(self):
	            self.settings["use"]=self.settings["tinderbox/use"]
def register(foo):
	foo.update({"tinderbox":tinderbox_target})
	return foo
