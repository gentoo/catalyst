
import catalyst.arch

class generic_sh(catalyst.arch.generic_arch):
	"Abstract base class for all sh builders [Little-endian]"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"

class generic_sheb(catalyst.arch.generic_arch):
	"Abstract base class for all sheb builders [Big-endian]"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"

class arch_sh(generic_sh):
	"Builder class for SH [Little-endian]"
	def __init__(self,myspec):
		generic_sh.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="sh-unknown-linux-gnu"

class arch_sh2(generic_sh):
	"Builder class for SH-2 [Little-endian]"
	def __init__(self,myspec):
		generic_sh.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m2 -pipe"
		self.settings["CHOST"]="sh2-unknown-linux-gnu"

class arch_sh2a(generic_sh):
	"Builder class for SH-2A [Little-endian]"
	def __init__(self,myspec):
		generic_sh.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m2a -pipe"
		self.settings["CHOST"]="sh2a-unknown-linux-gnu"

class arch_sh3(generic_sh):
	"Builder class for SH-3 [Little-endian]"
	def __init__(self,myspec):
		generic_sh.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m3 -pipe"
		self.settings["CHOST"]="sh3-unknown-linux-gnu"

class arch_sh4(generic_sh):
	"Builder class for SH-4 [Little-endian]"
	def __init__(self,myspec):
		generic_sh.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m4 -pipe"
		self.settings["CHOST"]="sh4-unknown-linux-gnu"

class arch_sh4a(generic_sh):
	"Builder class for SH-4A [Little-endian]"
	def __init__(self,myspec):
		generic_sh.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m4a -pipe"
		self.settings["CHOST"]="sh4a-unknown-linux-gnu"

class arch_sheb(generic_sheb):
	"Builder class for SH [Big-endian]"
	def __init__(self,myspec):
		generic_sheb.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="sheb-unknown-linux-gnu"

class arch_sh2eb(generic_sheb):
	"Builder class for SH-2 [Big-endian]"
	def __init__(self,myspec):
		generic_sheb.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m2 -pipe"
		self.settings["CHOST"]="sh2eb-unknown-linux-gnu"

class arch_sh2aeb(generic_sheb):
	"Builder class for SH-2A [Big-endian]"
	def __init__(self,myspec):
		generic_sheb.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m2a -pipe"
		self.settings["CHOST"]="sh2aeb-unknown-linux-gnu"

class arch_sh3eb(generic_sheb):
	"Builder class for SH-3 [Big-endian]"
	def __init__(self,myspec):
		generic_sheb.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m3 -pipe"
		self.settings["CHOST"]="sh3eb-unknown-linux-gnu"

class arch_sh4eb(generic_sheb):
	"Builder class for SH-4 [Big-endian]"
	def __init__(self,myspec):
		generic_sheb.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m4 -pipe"
		self.settings["CHOST"]="sh4eb-unknown-linux-gnu"

class arch_sh4aeb(generic_sheb):
	"Builder class for SH-4A [Big-endian]"
	def __init__(self,myspec):
		generic_sheb.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m4a -pipe"
		self.settings["CHOST"]="sh4aeb-unknown-linux-gnu"

_subarch_map = {
	"sh"	:arch_sh,
	"sh2"	:arch_sh2,
	"sh2a"	:arch_sh2a,
	"sh3"	:arch_sh3,
	"sh4"	:arch_sh4,
	"sh4a"	:arch_sh4a,
	"sheb"	:arch_sheb,
	"sh2aeb" :arch_sh2aeb,
	"sh2eb" :arch_sh2eb,
	"sh3eb"	:arch_sh3eb,
	"sh4eb"	:arch_sh4eb,
	"sh4aeb" :arch_sh4aeb
}

_machine_map = ("sh2","sh2a","sh3","sh4","sh4a","sh2eb","sh2aeb","sh3eb","sh4eb","sh4aeb")

# vim: ts=4 sw=4 sta noet sts=4 ai
