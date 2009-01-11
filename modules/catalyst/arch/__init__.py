"""
Parent module of all arch modules
"""

import os
import imp
import catalyst.util

# This is only until we move all the output stuff into catalyst.output
from catalyst_support import msg

class arches:

	def __init__(self):
		self._arch_modules = {}

	def find_arch_modules(self):
		search_dir = os.path.abspath(os.path.dirname(__file__))
		arch_module_list = [x[:-3] for x in os.listdir(search_dir) \
			if x.endswith('.py') and not x.startswith('__')]
		return arch_module_list

	def get_arches(self):
		for x in self.find_arch_modules():
			self._arch_modules[x] = catalyst.util.load_module("catalyst.arch." + x)
			if self._arch_modules[x] is None:
				msg("Cannot import catalyst.arch." + x + ". This usually only " + \
					"happens due to a syntax error, which should be reported as " \
					"a bug.")
		return self._arch_modules
