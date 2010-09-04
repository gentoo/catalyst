
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

class arch_armv6t2(generic_arm):
	"Builder class for armv6t2 target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv6t2-unknown-linux-gnueabi"
		self.settings["CFLAGS"]=" -march=armv6t2 -mfpu=vfp -mfloat-abi=softfp"

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
		self.settings["CFLAGS"]+=" -march=armv7-a -mfpu=vfp -mfloat-abi=softfp"

class arch_armv7r(generic_arm):
	"Builder class for armv7r target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv7r-unknown-linux-gnueabi"
		self.settings["CFLAGS"]+=" -march=armv7-r -mfpu=vfp -mfloat-abi=softfp"

class arch_armv7m(generic_arm):
	"Builder class for armv7m target"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv7m-unknown-linux-gnueabi"
		self.settings["CFLAGS"]+=" -march=armv7-m -mfpu=vfp -mfloat-abi=softfp"

class arch_armv7a_hardfp(generic_arm):
	"Builder class for armv7a hardfloat target, needs >=gcc-4.5"
	def __init__(self,myspec):
		generic_arm.__init__(self,myspec)
		self.settings["CHOST"]="armv7a-hardfloat-linux-gnueabi"
		self.settings["CFLAGS"]+=" -march=armv7-a -mfpu=vfp -mfloat-abi=hard"

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
	"armv5tl": arch_armv5tl,
	"armv5tel": arch_armv5tel,
	"armv5tejl": arch_armv5tejl,
	"armv6j" : arch_armv6j,
	"armv6t2" : arch_armv6t2,
	"armv6z" : arch_armv6z,
	"armv6zk" : arch_armv6zk,
	"armv7a" : arch_armv7a,
	"armv7r" : arch_armv7r,
	"armv7m" : arch_armv7m,
	"armv7a_hardfp" : arch_armv7a_hardfp,
	"armeb"  : arch_armeb,
	"armv5teb" : arch_armv5teb
}

_machine_map = ("arm", "armv4l", "armv4tl", "armv5tl", "armv5tel", "armv5tejl", "armv6l", "armv7l", "armeb", "armv5teb")

# vim: ts=4 sw=4 sta noet sts=4 ai
