
import catalyst.arch,os
from catalyst.support import *

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

class arch_mips1(generic_mips):
	"Builder class for MIPS I [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips1 -mabi=32 -pipe"

class arch_mips2(generic_mips):
	"Builder class for MIPS II [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips2 -mabi=32 -pipe"

class arch_mips3(generic_mips):
	"Builder class for MIPS III [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=32 -pipe"

class arch_mips3_n32(generic_mips):
	"Builder class for MIPS III [Big-endian N32]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=n32 -pipe"
		self.settings["CHOST"]="mips64-unknown-linux-gnu"
		self.settings["HOSTUSE"]=["n32"]

class arch_mips3_n64(generic_mips):
	"Builder class for MIPS III [Big-endian N64]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=64 -pipe"
		self.settings["CHOST"]="mips64-unknown-linux-gnu"
		self.settings["HOSTUSE"]=["n64"]

class arch_mips4(generic_mips):
	"Builder class for MIPS IV [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=32 -pipe"

class arch_mips4_n32(generic_mips):
	"Builder class for MIPS IV [Big-endian N32]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=n32 -pipe"
		self.settings["CHOST"]="mips64-unknown-linux-gnu"
		self.settings["HOSTUSE"]=["n32"]

class arch_mips4_n64(generic_mips):
	"Builder class for MIPS IV [Big-endian N64]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=64 -pipe"
		self.settings["CHOST"]="mips64-unknown-linux-gnu"
		self.settings["HOSTUSE"]=["n64"]

class arch_mipsel1(generic_mipsel):
	"Builder class for all MIPS I [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips1 -mabi=32 -pipe"

class arch_mipsel2(generic_mipsel):
	"Builder class for all MIPS II [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips2 -mabi=32 -pipe"

class arch_mipsel3(generic_mipsel):
	"Builder class for all MIPS III [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=32 -pipe"

class arch_mipsel3_n32(generic_mipsel):
	"Builder class for all MIPS III [Little-endian N32]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips3 -mabi=n32 -pipe"
		self.settings["CHOST"]="mips64el-unknown-linux-gnu"
		self.settings["HOSTUSE"]=["n32"]

class arch_mipsel4(generic_mipsel):
	"Builder class for all MIPS IV [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=32 -pipe"

class arch_mipsel4_n32(generic_mipsel):
	"Builder class for all MIPS IV [Little-endian N32]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mips4 -mabi=n32 -pipe"
		self.settings["CHOST"]="mips64el-unknown-linux-gnu"
		self.settings["HOSTUSE"]=["n32"]

class arch_cobalt(generic_mipsel):
	"Builder class for all cobalt [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=r5000 -mabi=32 -pipe"
		self.settings["CHOST"]="mipsel-unknown-linux-gnu"
		self.settings["HOSTUSE"]=["cobalt"]

class arch_cobalt_n32(generic_mipsel):
	"Builder class for all cobalt [Little-endian N32]"
	def __init__(self,myspec):
		arch_mipsel4_n32.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=r5000 -mabi=n32 -pipe"
		self.settings["HOSTUSE"]=["cobalt","n32"]

class arch_ip27(generic_mipsel):
	"Builder class for all IP27 [Big-endian]"
	def __init__(self,myspec):
		arch_mips4.__init__(self,myspec)
		self.settings["HOSTUSE"]=["ip27"]

class arch_ip27_n32(generic_mipsel):
	"Builder class for all IP27 [Big-endian N32]"
	def __init__(self,myspec):
		arch_mips4_n32.__init__(self,myspec)
		self.settings["HOSTUSE"]=["ip27","n32"]

class arch_ip28(generic_mipsel):
	"Builder class for all IP28 [Big-endian]"
	def __init__(self,myspec):
		arch_mips4.__init__(self,myspec)
		self.settings["HOSTUSE"]=["ip28"]

class arch_ip28_n32(generic_mipsel):
	"Builder class for all IP28 [Big-endian N32]"
	def __init__(self,myspec):
		arch_mips4_n32.__init__(self,myspec)
		self.settings["HOSTUSE"]=["ip28","n32"]

class arch_ip30(generic_mipsel):
	"Builder class for all IP30 [Big-endian]"
	def __init__(self,myspec):
		arch_mips4.__init__(self,myspec)
		self.settings["HOSTUSE"]=["ip30"]

class arch_ip30_n32(generic_mipsel):
	"Builder class for all IP30 [Big-endian N32]"
	def __init__(self,myspec):
		arch_mips4_n32.__init__(self,myspec)
		self.settings["HOSTUSE"]=["ip30","n32"]

__subarch_map = {
	"cobalt"		: arch_cobalt,
	"cobalt_n32"	: arch_cobalt_n32,
	"ip27"			: arch_ip27,
	"ip27_n32"		: arch_ip27_n32,
	"ip28"			: arch_ip28,
	"ip28_n32"		: arch_ip28_n32,
	"ip30"			: arch_ip30,
	"ip30_n32"		: arch_ip30_n32,
	"mips"			: arch_mips1,
	"mips1"			: arch_mips1,
	"mips2"			: arch_mips2,
	"mips3"			: arch_mips3,
	"mips3_n32"		: arch_mips3_n32,
	"mips3_n64"		: arch_mips3_n64,
	"mips4"			: arch_mips4,
	"mips4_n32"		: arch_mips4_n32,
	"mipsel"		: arch_mipsel1,
	"mipsel1"		: arch_mipsel1,
	"mipsel2"		: arch_mipsel2,
	"mipsel3"		: arch_mipsel3,
	"mipsel3_n32"	: arch_mipsel3_n32,
	"mipsel4"		: arch_mipsel4,
	"mipsel4_n32"	: arch_mipsel4_n32,
	"loongson"		: arch_mipsel3,
}

__machine_map = ("mips","mips64")

