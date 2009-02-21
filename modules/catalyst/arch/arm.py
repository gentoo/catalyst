
import catalyst.arch

class generic_arm(catalyst.arch.generic_arch):
	"Abstract base class for all arm (little endian) builders"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2 -pipe"

class generic_armeb(catalyst.arch.generic_arch):
	"Abstract base class for all arm (big endian) builders"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
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

class arch_armv4tl(generic_arm):
	"Builder class for armv4tl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv4tl-softfloat-linux-gnueabi"

class arch_armv5l(generic_arm):
	"Builder class for armv5l target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv5l-softfloat-linux-gnueabi"

class arch_armv5tl(generic_arm):
	"Builder class for armv5tl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv5tl-softfloat-linux-gnueabi"

class arch_armv5tel(generic_arm):
	"Builder class for armv5tel target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv5tel-softfloat-linux-gnueabi"

class arch_armv5tejl(generic_arm):
	"Builder class for armv5tejl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv5tejl-softfloat-linux-gnueabi"

class arch_armv6l(generic_arm):
	"Builder class for armv6l target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv6l-softloat-linux-gnueabi"

class arch_armv7l(generic_arm):
	"Builder class for armv7l target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv7l-softfloat-linux-gnueabi"

class arch_armv7al(generic_armeb):
	"Builder class for armv7al target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv7al-softfloat-linux-gnueabi"

class arch_armv5teb(generic_armeb):
	"Builder class for armv5teb (XScale) target"
	def __init__(self,myspec):
		generic_armeb.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -mcpu=xscale"
		self.settings["CHOST"]="armv5teb-softfloat-linux-gnueabi"

_subarch_map = {
	"arm"    : arch_arm,
	"armv4l" : arch_armv4l,
	"armv4tl": arch_armv4tl,
	"armv5l" : arch_armv5l,
	"armv5tl": arch_armv5tl,
	"armv5tel": arch_armv5tel,
	"armv5tejl": arch_armv5tejl,
	"armv6l" : arch_armv6l,
	"armv7l" : arch_armv7l,
	"armv7al" : arch_armv7al,
	"armeb"  : arch_armeb,
	"armv5b" : arch_armv5b
}

_machine_map = ("arm", "armv4l", "armv4tl", "armv5l", "armv5tl", "armv5tel", "armv5tejl", "armv6l", "armv7l", "armv7al", "armeb", "armv5teb")
