
import catalyst.arch

class generic_arm(catalyst.arch.generic_arch):
	"Abstract base class for all arm (little endian) builders"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-Os -pipe"

class generic_armeb(catalyst.arch.generic_arch):
	"Abstract base class for all arm (big endian) builders"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-Os -pipe"

class arch_arm(generic_arm):
	"Builder class for arm (little endian) target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="arm-unknown-linux-gnu"
		self.settings["CFLAGS"]="-Os -march=armv4 -pipe"

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
		self.settings["CFLAGS"]="-Os -march=armv4 -pipe"

class arch_armv4tl(generic_arm):
	"Builder class for armv4tl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv4tl-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv4t -pipe"

class arch_armv5l(generic_arm):
	"Builder class for armv5l target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv5l-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv5 -pipe"

class arch_armv5tl(generic_arm):
	"Builder class for armv5tl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv5tl-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv5t -pipe"

class arch_armv5tel(generic_arm):
	"Builder class for armv5tel target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv5tel-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv5te -pipe"

class arch_armv5tejl(generic_arm):
	"Builder class for armv5tejl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv5tejl-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv5te -pipe"

class arch_armv6l(generic_arm):
	"Builder class for armv6l target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv6l-softloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv6 -pipe"

class arch_armv6jl(generic_arm):
	"Builder class for armv6jl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv6jl-softloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv6j -pipe"

class arch_armv6t2l(generic_arm):
	"Builder class for armv6t2l target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv6t2l-softloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv6t2 -pipe"

class arch_armv6zl(generic_arm):
	"Builder class for armv6zl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv6zl-softloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv6z -pipe"

class arch_armv6zkl(generic_arm):
	"Builder class for armv6zkl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv6zkl-softloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv6zk -pipe"

class arch_armv7l(generic_arm):
	"Builder class for armv7l target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv7l-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv7 -pipe"

class arch_armv7al(generic_arm):
	"Builder class for armv7al target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv7al-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv7-a -pipe"

class arch_armv7rl(generic_arm):
	"Builder class for armv7rl target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv7ml-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv7-r -pipe"

class arch_armv7ml(generic_arm):
	"Builder class for armv7ml target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv7ml-softfloat-linux-gnueabi"
		self.settings["CFLAGS"]="-Os -march=armv7-m -pipe"

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
	"armv6jl" : arch_armv6jl,
	"armv6t2l" : arch_armv6t2l,
	"armv6zl" : arch_armv6zl,
	"armv6zkl" : arch_armv6zkl,
	"armv7l" : arch_armv7l,
	"armv7al" : arch_armv7al,
	"armv7rl" : arch_armv7rl,
	"armv7ml" : arch_armv7ml,
	"armeb"  : arch_armeb,
	"armv5b" : arch_armv5b
}

_machine_map = ("arm", "armv4l", "armv4tl", "armv5l", "armv5tl", "armv5tel", "armv5tejl", "armv6l", "armv7l", "armeb", "armv5teb")

# vim: ts=4 sw=4 sta noet sts=4 ai
