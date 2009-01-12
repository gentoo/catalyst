"""
This module contains miscellaneous functions for outputting messages
"""

import sys

verbosity = 1

def msg(mymsg="", verblevel=1, newline=True):
	if verbosity >= verblevel:
		if newline:
			print mymsg
		else:
			print mymsg,

def warn(message):
	msg("!!! catalyst: " + message)

def die(message, exitcode=1):
	warn(message)
	sys.exit(exitcode)

