

from catalyst.support import addl_arg_parse

class TargetBase(object):
	"""
	The toplevel class for all targets. This is about as generic as we get.
	"""
	def __init__(self, myspec, addlargs):
		addl_arg_parse(myspec,addlargs,self.required_values,self.valid_values)
		self.settings=myspec
		self.env={}
		self.env["PATH"]="/bin:/sbin:/usr/bin:/usr/sbin"
