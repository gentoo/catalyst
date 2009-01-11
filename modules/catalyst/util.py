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
		# I'm not sure if it's better to use imp.load_module() for this, but
		# it seems to work just fine this way, and it's easier.
		exec("import " + name)
		return sys.modules[name]
	except Exception:
		return None

def find_binary(myc):
	"""look through the environmental path for an executable file named whatever myc is"""
	# this sucks. badly.
	p=os.getenv("PATH")
	if p == None:
		return None
	for x in p.split(":"):
		#if it exists, and is executable
		if os.path.exists("%s/%s" % (x,myc)) and os.stat("%s/%s" % (x,myc))[0] & 0x0248:
			return "%s/%s" % (x,myc)
	return None

