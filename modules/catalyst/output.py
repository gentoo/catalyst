"""
This module contains miscellaneous functions for outputting messages
"""

import sys

verbosity = 1

def msg(mymsg, verblevel=1):
	if verbosity >= verblevel:
		print mymsg

def warn(msg):
	print "!!! catalyst: " + msg

def die(msg, exitcode=1):
	warn(msg)
	sys.exit(exitcode)

