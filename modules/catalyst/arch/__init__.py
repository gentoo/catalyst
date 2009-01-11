"""
Parent module of all arch modules
"""

import os
import imp
import catalyst.util

# This is only until we move all the output stuff into catalyst.output
from catalyst.support import msg

def find_arch_modules(self):
	search_dir = os.path.abspath(os.path.dirname(__file__))
	arch_module_list = [x[:-3] for x in os.listdir(search_dir) \
		if x.endswith('.py') and not x.startswith('__')]
	return arch_module_list

def get_arches(self):
	arch_modules = {}
	for x in find_arch_modules():
		arch_modules[x] = catalyst.util.load_module("catalyst.arch." + x)
		if arch_modules[x] is None:
			msg("Cannot import catalyst.arch." + x + ". This usually only " + \
				"happens due to a syntax error, which should be reported as " \
				"a bug.")
	return arch_modules

class generic_arch:

	def __init__(self, myspec):
		self.settings = myspec
