import sys

class CatalystError(Exception):
	def __init__(self, message):
		if message:
			print "catalyst: "+message
		sys.exit(1)

def die(msg=None):
	raise CatalystError, msg

def warn(msg):
	print "catalyst: "+msg


