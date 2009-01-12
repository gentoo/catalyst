"""
The toplevel class for generic_stage_target. This is about as generic as we get.
"""

import catalyst

class generic_target:

	def __init__(self,myspec,addlargs):
		catalyst.util.addl_arg_parse(myspec,addlargs,self.required_values,self.valid_values)
		self.settings=myspec
		self.env={}
		self.env["PATH"]="/bin:/sbin:/usr/bin:/usr/sbin"
