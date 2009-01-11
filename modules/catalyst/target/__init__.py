"""
Parent module of all target modules
"""

import os
import imp
import catalyst.util
from catalyst.output import warn

def find_target_modules():
	search_dir = os.path.abspath(os.path.dirname(__file__))
	target_module_list = [x[:-3] for x in os.listdir(search_dir) \
		if x.endswith('.py') and not x.startswith('__')]
	return target_module_list

def get_targets():
	target_modules = {}
	for x in find_target_modules():
		target_modules[x] = catalyst.util.load_module("catalyst.target." + x)
		if target_modules[x] is None:
			warn("Cannot import catalyst.target." + x + ". This usually only " + \
				"happens due to a syntax error, which should be reported as " \
				"a bug.")
	return target_modules

def build_target_map():
	target_map = {}
	targets = get_targets()
	for x in targets:
		if hasattr(targets[x], '__target_map'):
			target_map.update(targets[x].__target_map)
	return target_map
