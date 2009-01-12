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

	def check_autoresume(self, step=None):
		if "AUTORESUME" in self.settings:
			if step:
				if os.path.exists(self.settings["autoresume_path"] + step):
					return True
				else:
					return False
			else:
				return True
		return False

	def set_autoresume(self, step, value=""):
		if value:
			myf=open(self.settings["autoresume_path"] + step, "w")
			myf.write(value)
			myf.close()
		else:
			catalyst.util.touch(self.settings["autoresume_path"] + step)
