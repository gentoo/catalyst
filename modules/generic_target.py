# Copyright 1999-2005 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/generic_target.py,v 1.5 2005/12/07 21:01:35 rocket Exp $

"""
The toplevel class for generic_stage_target. This is about as generic as we get.
"""

from catalyst_support import *

class generic_target:

	def __init__(self,myspec,addlargs):
		addl_arg_parse(myspec,addlargs,self.required_values,self.valid_values)
		self.settings=myspec
		self.env={}
