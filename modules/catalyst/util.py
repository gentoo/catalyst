"""
Collection of utility functions for catalyst
"""

import sys, traceback

def capture_traceback():
	etype, value, tb = sys.exc_info()
	s = [x.strip() for x in traceback.format_exception(etype, value, tb)]
	return s

def print_traceback():
	for x in capture_traceback():
		print x

def load_module(name):
	try:
		exec("import " + name)
		return sys.modules[name]
	except Exception:
		return None
