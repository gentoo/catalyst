"""
The toplevel class for generic_stage_target. This is about as generic as we get.
"""

import os
import catalyst
from catalyst.output import *
from catalyst.spawn import cmd

class generic_target(catalyst.target.target):

	def __init__(self):
#		if myspec and addlargs:
#			catalyst.util.addl_arg_parse(myspec,addlargs,self.required_values,self.valid_values)
#			self.settings=myspec
#		else:
		self.config = catalyst.config.config()
		self.settings = self.config.get_spec().get_values()
		self.settings.update(self.config.get_conf())

		self.required_values = []
		self.valid_values = []

		self.env={}
		self.env["PATH"]="/bin:/sbin:/usr/bin:/usr/sbin"

		self._arch = self.settings["subarch"]
		self._rel_type = self.settings["rel_type"]
		self._version_stamp = self.settings["version_stamp"]
		self._media = self.settings["build"]
		self._target = self.settings["target"]

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
					autoresume_size = os.path.getsize(self.settings["autoresume_path"] + step)
					if autoresume_size == 0:
						return True
					else:
						metadata = catalyst.util.readfile(self.settings["autoresume_path"] + step)
						metadata = metadata.split()
						if os.path.exists(metadata[0]):
							if os.path.isfile(metadata[0]):
								path_hash = catalyst.hash.generate_hash(metadata[0], hash_function=self.settings["hash_function"], verbose=False)
								if path_hash != metadata[1]:
									self.clear_autoresume()
									return False
						else:
							self.clear_autoresume()
							return False
						return True
				else:
					self.clear_autoresume()
					return False
			else:
				return True
		return False

	def set_autoresume(self, step, path=None):
		if path:
			metadata = ""
			if os.path.isfile(path):
				path_hash = catalyst.hash.generate_hash(path, hash_function=self.settings["hash_function"], verbose=False)
				metadata = path + " " + path_hash
			else:
				metadata = path
			myf=open(self.settings["autoresume_path"] + step, "w")
			myf.write(metadata)
			myf.close()
		else:
			catalyst.util.touch(self.settings["autoresume_path"] + step)

	def run_controller_action(self, action, args=""):
		if os.path.exists(self.settings["controller_file"]):
			command = action
			if args:
				command += " " + args
			cmd("/bin/bash " + self.settings["controller_file"] + " " + command, \
				action + " script failed.", env=self.env)

	def calculate_source_subpath(self):
		depends = self.depends
		subpaths = []
		for x in depends:
			foo = self.settings['rel_type'] + '/' + x + '-' + self.settings['subarch'] + '-' + self.settings['version_stamp']
			subpaths.append(foo)
		return subpaths

# vim: ts=4 sw=4 sta noet sts=4 ai
