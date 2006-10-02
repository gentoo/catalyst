# $Header: /var/cvsroot/gentoo/src/catalyst/modules/generic_target.py,v 1.7 2006/10/02 20:41:54 wolf31o2 Exp $

"""
The toplevel class for generic_stage_target. This is about as generic as we get.
"""

from catalyst_support import *

class generic_target:

	def __init__(self,myspec,addlargs):
		addl_arg_parse(myspec,addlargs,self.required_values,self.valid_values)
		self.settings=myspec
		self.env={}
		self.env["PATH"]="/bin:/sbin:/usr/bin:/usr/sbin"
