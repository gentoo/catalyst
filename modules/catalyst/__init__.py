import catalyst.hash
import catalyst.arch
import catalyst.lock
import catalyst.util
import catalyst.error
import catalyst.spawn
import catalyst.target
import catalyst.config

hash = catalyst.hash
arch = catalyst.arch
lock = catalyst.lock
util = catalyst.util
error = catalyst.error
spawn = catalyst.spawn
target = catalyst.target
config = catalyst.config

"""
This class implements a proper singleton. This is useful for having a "global"
var with config and spec values instead of passing them around between objects
and functions
"""
class Singleton(object):

	def __new__(type):
		if not '_the_instance' in type.__dict__:
			type._the_instance = object.__new__(type)
		return type._the_instance

