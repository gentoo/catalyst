
import builder,os
from catalyst_support import *

class generic_arm(builder.generic):
	"Abstract base class for all arm (little endian) builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2 -pipe"
   
class generic_armeb(builder.generic):
	"Abstract base class for all arm (big endian) builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2 -pipe"

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
	"Builder class for armv4l target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv4l-unknown-linux-gnu"
		self.settings["CFLAGS"]+=" -march=armv4"

class arch_armv4tl(generic_arm):
	"Builder class for armv4tl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv4tl-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]+=" -march=armv4t"

class arch_armv5tl(generic_arm):
	"Builder class for armv5tl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv5tl-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]+=" -march=armv5t"

class arch_armv5tel(generic_arm):
	"Builder class for armv5tel target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv5tel-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]+=" -march=armv5te"

class arch_armv5tejl(generic_arm):
	"Builder class for armv5tejl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv5tejl-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]+=" -march=armv5te"

class arch_armv6j(generic_arm):
	"Builder class for armv6j target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv6j-unknown-linux-gnueabi"
		self.settings["CFLAGS"]+=" -march=armv6j -mfpu=vfp -mfloat-abi=softfp"

class arch_armv6z(generic_arm):
	"Builder class for armv6z target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv6z-unknown-linux-gnueabi"
		self.settings["CFLAGS"]+=" -march=armv6z -mfpu=vfp -mfloat-abi=softfp"

class arch_armv6zk(generic_arm):
	"Builder class for armv6zk target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv6zk-unknown-linux-gnueabi"
		self.settings["CFLAGS"]+=" -march=armv6zk -mfpu=vfp -mfloat-abi=softfp"

class arch_armv7a(generic_arm):
	"Builder class for armv7a target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv7a-unknown-linux-gnueabi"
		self.settings["CFLAGS"]+=" -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=softfp"

class arch_armv7a_hardfp(generic_arm):
	"Builder class for armv7a hardfloat target, needs >=gcc-4.5"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv7a-hardfloat-linux-gnueabi"
		self.settings["CFLAGS"]+=" -march=armv7-a -mfpu=vfpv3-d16 -mfloat-abi=hard"

class arch_armv5teb(generic_armeb):
	"Builder class for armv5teb (XScale) target"
	def __init__(self,myspec):
		generic_armeb.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -mcpu=xscale"
		self.settings["CHOST"]="armv5teb-softfloat-linux-gnueabi"

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({
		"arm"    : arch_arm,
		"armv4l" : arch_armv4l,
		"armv4tl": arch_armv4tl,
		"armv5tl": arch_armv5tl,
		"armv5tel": arch_armv5tel,
		"armv5tejl": arch_armv5tejl,
		"armv6j" : arch_armv6j,
		"armv6z" : arch_armv6z,
		"armv6zk" : arch_armv6zk,
		"armv7a" : arch_armv7a,
		"armv7a_hardfp" : arch_armv7a_hardfp,
		"armeb"  : arch_armeb,
		"armv5teb" : arch_armv5teb
	}, ("arm", "armv4l", "armv4tl", "armv5tl", "armv5tel", "armv5tejl", "armv6l", 
"armv7l", "armeb", "armv5teb") )

