
import catalyst.arch,os
from catalyst.support import *

class generic_arm(catalyst.arch.generic_arch):
	"Abstract base class for all arm (little endian) builders"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CXXFLAGS"]="-O1 -pipe"
   
class generic_armeb(catalyst.arch.generic_arch):
	"Abstract base class for all arm (big endian) builders"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CXXFLAGS"]="-O1 -pipe"

class arch_arm(generic_arm):
	"Builder class for arm (little endian) target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="arm-unknown-linux-gnu"

class arch_armeb(generic_armeb):
	"Builder class for arm (big endian) target"
	def __init__(self,myspec):
		generic_armeb.__init__(self,myspec)
		self.settings["CHOST"]="armeb-unknown-linux-gnu"

class arch_armv4l(generic_arm):
	"Builder class for armv4l (StrongArm-110) target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -mcpu=strongarm110"
		self.settings["CHOST"]="armv4l-unknown-linux-gnu"

class arch_armv5b(generic_arm):
	"Builder class for armv5b (XScale) target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -mcpu=xscale"
		self.settings["CHOST"]="armv5b-unknown-linux-gnu"

__subarch_map = {
	"arm"    : arch_arm,
	"armv4l" : arch_armv4l,
	"armeb"  : arch_armeb,
	"armv5b" : arch_armv5b
}

__machine_map = ("arm", "armv4l", "armeb", "armv5b", "armv5tel")


