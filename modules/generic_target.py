# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/generic_target.py,v 1.2 2004/07/03 00:33:37 zhen Exp $

"""
The toplevel class for generic_stage_target. This is about as generic as we get.
"""

from catalyst_support import *

class generic_target:

	def __init__(self,myspec,addlargs):
		addl_arg_parse(myspec,addlargs,self.required_values,self.valid_values)
		self.settings=myspec
		pass
