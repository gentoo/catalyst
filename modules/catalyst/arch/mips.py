
import catalyst.arch

class generic_mips(catalyst.arch.generic_arch):
	"Abstract base class for all mips builders [Big-endian]"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CHOST"]="mips-unknown-linux-gnu"

class generic_mipsel(catalyst.arch.generic_arch):
	"Abstract base class for all mipsel builders [Little-endian]"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CHOST"]="mipsel-unknown-linux-gnu"

class generic_mips64(catalyst.arch.generic_arch):
	"Abstract base class for all mips64 builders [Big-endian]"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CHOST"]="mips64-unknown-linux-gnu"

class generic_mips64el(catalyst.arch.generic_arch):
	"Abstract base class for all mips64el builders [Little-endian]"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CHOST"]="mips64el-unknown-linux-gnu"

class generic_multilib(catalyst.arch.generic_arch):
	"Abstract base class for MIPS multilib"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["HOSTUSE"]=["multilib"]

class arch_mips1(generic_mips):
	"Builder class for MIPS I [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips1 -mabi=32 -pipe"

class arch_mips3(generic_mips):
	"Builder class for MIPS III [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=32 -mfix-r4000 -mfix-r4400 -pipe"

class arch_mips3_n32(generic_mips64):
	"Builder class for MIPS III [Big-endian N32]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=n32 -mfix-r4000 -mfix-r4400 -pipe"

class arch_mips3_n64(generic_mips64):
	"Builder class for MIPS III [Big-endian N64]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=64 -mfix-r4000 -mfix-r4400 -pipe"

class arch_mips3_multilib(generic_mips64,generic_multilib):
	"Builder class for MIPS III [Big-endian multilib]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		generic_multilib.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mfix-r4000 -mfix-r4400 -pipe"

class arch_mips4(generic_mips64):
	"Builder class for MIPS IV [Big-endian]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=32 -pipe"

class arch_mips4_n32(generic_mips64):
	"Builder class for MIPS IV [Big-endian N32]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=n32 -pipe"

class arch_mips4_n64(generic_mips64):
	"Builder class for MIPS IV [Big-endian N64]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=64 -pipe"

class arch_mips4_multilib(generic_mips64,generic_multilib):
	"Builder class for MIPS IV [Big-endian multilib]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		generic_multilib.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -pipe"

class arch_mipsel1(generic_mipsel):
	"Builder class for all MIPS I [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips1 -mabi=32 -pipe"

class arch_mipsel3(generic_mipsel):
	"Builder class for all MIPS III [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=32 -Wa,-mfix-loongson2f-nop -pipe"

class arch_mipsel3_n32(generic_mips64el):
	"Builder class for all MIPS III [Little-endian N32]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=n32 -Wa,-mfix-loongson2f-nop -pipe"

class arch_mipsel3_n64(generic_mips64el):
	"Builder class for MIPS III [Little-endian N64]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=64 -Wa,-mfix-loongson2f-nop -pipe"

class arch_mipsel3_multilib(generic_mips64el,generic_multilib):
	"Builder class for MIPS III [Little-endian multilib]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		generic_multilib.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -Wa,-mfix-loongson2f-nop -pipe"

class arch_loongson2e(generic_mipsel):
	"Builder class for all Loongson 2E [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=loongson2e -mabi=32 -pipe -mplt"

class arch_loongson2e_n32(generic_mips64el):
	"Builder class for all Loongson 2E [Little-endian N32]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=loongson2e -mabi=n32 -pipe -mplt"

class arch_loongson2f(generic_mipsel):
	"Builder class for all Loongson 2F [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O3 -march=loongson2f -mabi=32 -pipe -mplt -Wa,-mfix-loongson2f-nop"

class arch_loongson2f_n32(generic_mips64el):
	"Builder class for all Loongson 2F [Little-endian N32]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O3 -march=loongson2f -mabi=n32 -pipe -mplt -Wa,-mfix-loongson2f-nop"

class arch_mipsel4(generic_mips64el):
	"Builder class for all MIPS IV [Little-endian]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=32 -pipe"

class arch_mipsel4_n32(generic_mips64el):
	"Builder class for all MIPS IV [Little-endian N32]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=n32 -pipe"

class arch_mipsel4_n64(generic_mips64el):
	"Builder class for MIPS IV [Little-endian N64]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=64 -pipe"

class arch_mipsel4_multilib(generic_mips64el,generic_multilib):
	"Builder class for MIPS IV [Little-endian multilib]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		generic_multilib.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -pipe"

class arch_cobalt(generic_mipsel):
	"Builder class for all cobalt [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=r5000 -mabi=32 -pipe"
		self.settings["HOSTUSE"]=["cobalt"]

class arch_cobalt_n32(generic_mips64el):
	"Builder class for all cobalt [Little-endian N32]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=r5000 -mabi=n32 -pipe"
		self.settings["HOSTUSE"]=["cobalt"]

_subarch_map = {
	"cobalt"		: arch_cobalt,
	"cobalt_n32"	: arch_cobalt_n32,
	"mips"			: arch_mips1,
	"mips1"			: arch_mips1,
	"mips3"			: arch_mips3,
	"mips3_n32"		: arch_mips3_n32,
	"mips3_n64"		: arch_mips3_n64,
	"mips3_multilib": arch_mips3_multilib,
	"mips4"			: arch_mips4,
	"mips4_n32"		: arch_mips4_n32,
	"mips4_n64"		: arch_mips4_n64,
	"mips4_multilib": arch_mips4_multilib,
	"mipsel"		: arch_mipsel1,
	"mipsel1"		: arch_mipsel1,
	"mipsel3"		: arch_mipsel3,
	"mipsel3_n32"	: arch_mipsel3_n32,
	"mipsel3_n64"	: arch_mipsel3_n64,
	"mipsel3_multilib"	: arch_mipsel3_multilib,
	"mipsel4"		: arch_mipsel4,
	"mipsel4_n32"	: arch_mipsel4_n32,
	"mipsel4_n64"	: arch_mipsel4_n64,
	"mipsel4_multilib"	: arch_mipsel4_multilib,
	"loongson2e"		: arch_loongson2e,
	"loongson2e_n32"	: arch_loongson2e_n32,
	"loongson2f"		: arch_loongson2f,
	"loongson2f_n32"	: arch_loongson2f_n32,
}

_machine_map = ("mips","mips64")

# vim: ts=4 sw=4 sta noet sts=4 ai
