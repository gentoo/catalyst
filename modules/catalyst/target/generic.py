"""
The toplevel class for generic_stage_target. This is about as generic as we get.
"""

import os
import catalyst
from catalyst.output import *

class generic_target:

	def __init__(self, myspec=None, addlargs=None):
		if myspec and addlargs:
			catalyst.util.addl_arg_parse(myspec,addlargs,self.required_values,self.valid_values)
			self.settings=myspec
		else:
			self.config = catalyst.config.config()
			self.settings = self.config.get_spec().get_values()
			self.settings.update(self.config.get_conf())

		self.env={}
		self.env["PATH"]="/bin:/sbin:/usr/bin:/usr/sbin"

	def set_autoresume_path(self):
		self.settings["autoresume_path"] = catalyst.util.normpath(self.settings["storedir"] + \
			"/tmp/" + self.settings["rel_type"] + "/" + ".autoresume-" + \
			self.settings["target"] + "-" + self.settings["subarch"] + "-" + \
			self.settings["version_stamp"] + "/")
		if self.check_autoresume():
			msg("The autoresume path is " + self.settings["autoresume_path"])
		if not os.path.exists(self.settings["autoresume_path"]):
			os.makedirs(self.settings["autoresume_path"],0755)


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
