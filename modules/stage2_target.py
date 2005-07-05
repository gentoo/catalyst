# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/stage2_target.py,v 1.4 2005/07/05 21:53:41 wolf31o2 Exp $

"""
Builder class for a stage2 installation tarball build.
"""

from catalyst_support import *
from generic_stage_target import *

class stage2_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=[]
		self.valid_values=[]
		generic_stage_target.__init__(self,spec,addlargs)

def register(foo):
	foo.update({"stage2":stage2_target})
	return foo
