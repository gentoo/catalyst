# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/livecd_stage1_target.py,v 1.1 2004/05/17 01:21:17 zhen Exp $

"""
Builder class for LiveCD stage1.
"""

import os,string,imp,types,shutil
from catalyst_support import *
from generic_stage_target import *
from stat import *

class livecd_stage1_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["livecd/packages","livecd/use"]
		self.valid_values=self.required_values[:]
		generic_stage_target.__init__(self,spec,addlargs)

	def run_local(self):
		mypack=list_bashify(self.settings["livecd/packages"])
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+"/targets/livecd-stage1/livecd-stage1.sh run "+mypack)
		except CatalystError:
			self.unbind()
			raise CatalystError,"LiveCD stage1 build aborting due to error."

def register(foo):
	foo.update({"livecd-stage1":livecd_stage1_target})
	return foo
