# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/stage3_target.py,v 1.3 2004/10/15 02:27:58 zhen Exp $

"""
Builder class for a stage3 installation tarball build.
"""

from catalyst_support import *
from generic_stage_target import *

class stage3_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=[]
		generic_stage_target.__init__(self,spec,addlargs)

def register(foo):
	foo.update({"stage3":stage3_target})
	return foo
