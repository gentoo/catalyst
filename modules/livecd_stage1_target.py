# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/livecd_stage1_target.py,v 1.6 2005/01/04 21:13:43 wolf31o2 Exp $

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

	def run_local(self):
		mypack=list_bashify(self.settings["livecd/packages"])
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/livecd-stage1/livecd-stage1.sh run "+mypack)
		
		except CatalystError:
			self.unbind()
			raise CatalystError,"LiveCD stage1 build aborting due to error."
	def set_action_sequence(self):
		self.settings["action_sequence"]=["dir_setup","unpack_and_bind","chroot_setup",\
					    "setup_environment","run_local","preclean","unbind","clean"]

	def set_use(self):
	            self.settings["use"]=self.settings["livecd/use"]

def register(foo):
	foo.update({"livecd-stage1":livecd_stage1_target})
	return foo
