# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/tinderbox_target.py,v 1.2 2004/07/03 00:33:37 zhen Exp $

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

def register(foo):
	foo.update({"tinderbox":tinderbox_target})
	return foo
