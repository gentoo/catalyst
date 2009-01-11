"""
Parent module of all arch modules
"""

import os
import imp
import catalyst.util

# This hard-coded list of arch is here until I find a good way to get a list of
# other modules contained in the same dir as this file
__arch_module_list = (
	"alpha", 
	"amd64", 
	"arm", 
	"hppa", 
	"ia64", 
	"mips", 
	"powerpc", 
	"s390", 
	"sh", 
	"sparc", 
	"x86"
)

class arches:

	__arch_modules = None

	def __init__(self):
		self.__arch_modules = {}

	def find_arch_modules(self):
		search_dir = os.path.abspath(os.path.dirname(__file__))
		arch_module_list = [x[:-3] for x in os.listdir(search_dir) \
			if x.endswith('.py') and not x.startswith('__')]
		return arch_module_list

	def get_arches(self):
		# We don't know if this works yet
#		for x in self.find_arch_modules():
		for x in __arch_module_list:
			self.__arch_modules[x] = catalyst.util.load_module("catalyst.arch." + x)
			if self.__arch_modules[x] is None:
				msg("Cannot import catalyst.arch." + x + ". This usually only " + \
					"happens due to a syntax error, which should be reported as " \
					"a bug.")
		return self.__arch_modules
