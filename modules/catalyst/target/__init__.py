"""
Parent module of all target modules
"""

import os
import imp
import catalyst.util

# This is only until we move all the output stuff into catalyst.output
from catalyst_support import msg

class targets:

	def __init__(self):
		self._target_modules = {}

	def find_target_modules(self):
		search_dir = os.path.abspath(os.path.dirname(__file__))
		target_module_list = [x[:-3] for x in os.listdir(search_dir) \
			if x.endswith('.py') and not x.startswith('__')]
		return target_module_list

	def get_targets(self):
		for x in self.find_target_modules():
			self._target_modules[x] = catalyst.util.load_module("catalyst.target." + x)
			if self._target_modules[x] is None:
				msg("Cannot import catalyst.target." + x + ". This usually only " + \
					"happens due to a syntax error, which should be reported as " \
					"a bug.")
		return self._target_modules
