# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/generic_target.py,v 1.1 2004/05/17 01:21:17 zhen Exp $

"""
The toplevel class for generic_stage_target. This is about as generic as we get.
"""

import os,string,imp,types,shutil
from catalyst_support import *
from stat import *

class generic_target:

	def __init__(self,myspec,addlargs):
		addl_arg_parse(myspec,addlargs,self.required_values,self.valid_values)
		self.settings=myspec
		pass
