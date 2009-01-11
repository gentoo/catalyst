"""
This module contains the custom exception classes used by catalyst
"""

import sys, traceback
import catalyst.output

class CatalystError(Exception):
	def __init__(self, message):
		if message:
			(type,value)=sys.exc_info()[:2]
			if value!=None:
				print
				print traceback.print_exc(file=sys.stdout)
			print
			catalyst.output.warn(message)
			print

class LockInUse(Exception):
	def __init__(self, message):
		if message:
			#(type,value)=sys.exc_info()[:2]
			#if value!=None:
			    #print
			    #kprint traceback.print_exc(file=sys.stdout)
			print
			catalyst.output.warn("lock file in use: " + message)
			print

