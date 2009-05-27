"""
This module contains the custom exception classes used by catalyst
"""

import sys, traceback
from catalyst.output import *

class CatalystError(Exception):
	def __init__(self, message):
		if message:
			(extype,value)=sys.exc_info()[:2]
			if value!=None:
				msg()
				msg(traceback.print_exc(file=sys.stdout))
			msg()
			warn(message)
			msg()

class LockInUse(Exception):
	def __init__(self, message):
		if message:
			#(extype,value)=sys.exc_info()[:2]
			#if value!=None:
			    #print
			    #kprint traceback.print_exc(file=sys.stdout)
			msg()
			warn("lock file in use: " + message)
			msg()

# vim: ts=4 sw=4 sta noet sts=4 ai
