"""
Parent module of all arch modules
"""

import os
import catalyst.util
from catalyst.output import warn

def find_arch_modules():
	search_dir = os.path.abspath(os.path.dirname(__file__))
	arch_module_list = [x[:-3] for x in os.listdir(search_dir) \
		if x.endswith('.py') and not x.startswith('__')]
	return arch_module_list

def get_arches():
	arch_modules = {}
	for x in find_arch_modules():
		arch_modules[x] = catalyst.util.load_module("catalyst.arch." + x)
		if arch_modules[x] is None:
			warn("Cannot import catalyst.arch." + x + ". This usually only " + \
				"happens due to a syntax error, which should be reported as " \
				"a bug.")
	return arch_modules

class generic_arch:

	def __init__(self, myspec):
		self.settings = myspec
