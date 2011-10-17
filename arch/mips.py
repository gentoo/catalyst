
import builder,os
from catalyst_support import *

class generic_mips(builder.generic):
	"Abstract base class for all mips builders [Big-endian]"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CHOST"]="mips-unknown-linux-gnu"

class generic_mipsel(builder.generic):
	"Abstract base class for all mipsel builders [Little-endian]"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CHOST"]="mipsel-unknown-linux-gnu"

class generic_mips64(builder.generic):
	"Abstract base class for all mips64 builders [Big-endian]"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CHOST"]="mips64-unknown-linux-gnu"

class generic_mips64el(builder.generic):
	"Abstract base class for all mips64el builders [Little-endian]"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CHOST"]="mips64el-unknown-linux-gnu"

class arch_mips1(generic_mips):
	"Builder class for MIPS I [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips1 -mabi=32 -pipe"

class arch_mips32(generic_mips):
	"Builder class for MIPS 32 [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips32 -mabi=32 -pipe"

class arch_mips32_softfloat(generic_mips):
	"Builder class for MIPS 32 [Big-endian softfloat]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips32 -mabi=32 -pipe"
		self.settings["CHOST"]="mips-softfloat-linux-gnu"

class arch_mips32r2(generic_mips):
	"Builder class for MIPS 32r2 [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips32r2 -mabi=32 -pipe"

class arch_mips32r2_softfloat(generic_mips):
	"Builder class for MIPS 32r2 [Big-endian softfloat]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips32r2 -mabi=32 -pipe"
		self.settings["CHOST"]="mips-softfloat-linux-gnu"

class arch_mips3(generic_mips):
	"Builder class for MIPS III [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips3 -mabi=32 -mfix-r4000 -mfix-r4400 -pipe"

class arch_mips3_n32(generic_mips64):
	"Builder class for MIPS III [Big-endian N32]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips3 -mabi=n32 -mfix-r4000 -mfix-r4400 -pipe"

class arch_mips3_n64(generic_mips64):
	"Builder class for MIPS III [Big-endian N64]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips3 -mabi=64 -mfix-r4000 -mfix-r4400 -pipe"

class arch_mips3_multilib(generic_mips64):
	"Builder class for MIPS III [Big-endian multilib]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips3 -mfix-r4000 -mfix-r4400 -pipe"

class arch_mips4(generic_mips):
	"Builder class for MIPS IV [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips4 -mabi=32 -pipe"

class arch_mips4_n32(generic_mips64):
	"Builder class for MIPS IV [Big-endian N32]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips4 -mabi=n32 -pipe"

class arch_mips4_n64(generic_mips64):
	"Builder class for MIPS IV [Big-endian N64]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips4 -mabi=64 -pipe"

class arch_mips4_multilib(generic_mips64):
	"Builder class for MIPS IV [Big-endian multilib]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips4 -pipe"

class arch_mips4_r10k(generic_mips):
	"Builder class for MIPS IV R10k [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=r10k -mabi=32 -pipe"

class arch_mips4_r10k_n32(generic_mips64):
	"Builder class for MIPS IV R10k [Big-endian N32]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=r10k -mabi=n32 -pipe"

class arch_mips4_r10k_n64(generic_mips64):
	"Builder class for MIPS IV R10k [Big-endian N64]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=r10k -mabi=64 -pipe"

class arch_mips4_r10k_multilib(generic_mips64):
	"Builder class for MIPS IV R10k [Big-endian multilib]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=r10k -pipe"

class arch_mips64(generic_mips):
	"Builder class for MIPS 64 [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64 -mabi=32 -pipe"

class arch_mips64_n32(generic_mips64):
	"Builder class for MIPS 64 [Big-endian N32]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64 -mabi=n32 -pipe"

class arch_mips64_n64(generic_mips64):
	"Builder class for MIPS 64 [Big-endian N64]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64 -mabi=64 -pipe"

class arch_mips64_multilib(generic_mips64):
	"Builder class for MIPS 64 [Big-endian multilib]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64 -pipe"

class arch_mips64r2(generic_mips):
	"Builder class for MIPS 64r2 [Big-endian]"
	def __init__(self,myspec):
		generic_mips.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64r2 -mabi=32 -pipe"

class arch_mips64r2_n32(generic_mips64):
	"Builder class for MIPS 64r2 [Big-endian N32]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64r2 -mabi=n32 -pipe"

class arch_mips64r2_n64(generic_mips64):
	"Builder class for MIPS 64r2 [Big-endian N64]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64r2 -mabi=64 -pipe"

class arch_mips64r2_multilib(generic_mips64):
	"Builder class for MIPS 64r2 [Big-endian multilib]"
	def __init__(self,myspec):
		generic_mips64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64r2 -pipe"

class arch_mipsel1(generic_mipsel):
	"Builder class for MIPS I [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips1 -mabi=32 -pipe"

class arch_mips32el(generic_mipsel):
	"Builder class for MIPS 32 [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips32 -mabi=32 -pipe"

class arch_mips32el_softfloat(generic_mipsel):
	"Builder class for MIPS 32 [Little-endian softfloat]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips32 -mabi=32 -pipe"
		self.settings["CHOST"]="mipsel-softfloat-linux-gnu"

class arch_mips32r2el(generic_mipsel):
	"Builder class for MIPS 32r2 [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips32r2 -mabi=32 -pipe"

class arch_mips32r2el_softfloat(generic_mipsel):
	"Builder class for MIPS 32r2 [Little-endian softfloat]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips32r2 -mabi=32 -pipe"
		self.settings["CHOST"]="mipsel-softfloat-linux-gnu"

class arch_mipsel3(generic_mipsel):
	"Builder class for MIPS III [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips3 -mabi=32 -Wa,-mfix-loongson2f-nop -pipe"

class arch_mipsel3_n32(generic_mips64el):
	"Builder class for MIPS III [Little-endian N32]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips3 -mabi=n32 -Wa,-mfix-loongson2f-nop -pipe"

class arch_mipsel3_n64(generic_mips64el):
	"Builder class for MIPS III [Little-endian N64]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips3 -mabi=64 -Wa,-mfix-loongson2f-nop -pipe"

class arch_mipsel3_multilib(generic_mips64el):
	"Builder class for MIPS III [Little-endian multilib]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips3 -Wa,-mfix-loongson2f-nop -pipe"

class arch_loongson2e(generic_mipsel):
	"Builder class for Loongson 2E [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=loongson2e -mabi=32 -pipe -mplt"

class arch_loongson2e_n32(generic_mips64el):
	"Builder class for Loongson 2E [Little-endian N32]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=loongson2e -mabi=n32 -pipe -mplt"

class arch_loongson2f(generic_mipsel):
	"Builder class for Loongson 2F [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O3 -march=loongson2f -mabi=32 -pipe -mplt -Wa,-mfix-loongson2f-nop"

class arch_loongson2f_n32(generic_mips64el):
	"Builder class for Loongson 2F [Little-endian N32]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O3 -march=loongson2f -mabi=n32 -pipe -mplt -Wa,-mfix-loongson2f-nop"

class arch_mipsel4(generic_mipsel):
	"Builder class for MIPS IV [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips4 -mabi=32 -pipe"

class arch_mipsel4_n32(generic_mips64el):
	"Builder class for MIPS IV [Little-endian N32]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips4 -mabi=n32 -pipe"

class arch_mipsel4_n64(generic_mips64el):
	"Builder class for MIPS IV [Little-endian N64]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips4 -mabi=64 -pipe"

class arch_mipsel4_multilib(generic_mips64el):
	"Builder class for MIPS IV [Little-endian multilib]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips4 -pipe"

class arch_mips64el(generic_mipsel):
	"Builder class for MIPS 64 [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64 -mabi=32 -pipe"

class arch_mips64el_n32(generic_mips64el):
	"Builder class for MIPS 64 [Little-endian N32]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64 -mabi=n32 -pipe"

class arch_mips64el_n64(generic_mips64el):
	"Builder class for MIPS 64 [Little-endian N64]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64 -mabi=64 -pipe"

class arch_mips64el_multilib(generic_mips64el):
	"Builder class for MIPS 64 [Little-endian multilib]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64 -pipe"

class arch_mips64r2el(generic_mipsel):
	"Builder class for MIPS 64r2 [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64r2 -mabi=32 -pipe"

class arch_mips64r2el_n32(generic_mips64el):
	"Builder class for MIPS 64r2 [Little-endian N32]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64r2 -mabi=n32 -pipe"

class arch_mips64r2el_n64(generic_mips64el):
	"Builder class for MIPS 64r2 [Little-endian N64]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64r2 -mabi=64 -pipe"

class arch_mips64r2el_multilib(generic_mips64el):
	"Builder class for MIPS 64r2 [Little-endian multilib]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=mips64r2 -pipe"

class arch_cobalt(generic_mipsel):
	"Builder class for cobalt [Little-endian]"
	def __init__(self,myspec):
		generic_mipsel.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=r5000 -mabi=32 -pipe"
		self.settings["HOSTUSE"]=["cobalt"]

class arch_cobalt_n32(generic_mips64el):
	"Builder class for cobalt [Little-endian N32]"
	def __init__(self,myspec):
		generic_mips64el.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=r5000 -mabi=n32 -pipe"
		self.settings["HOSTUSE"]=["cobalt"]

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({ 
			"cobalt"		: arch_cobalt,
			"cobalt_n32"	: arch_cobalt_n32,
			"mips"			: arch_mips1,
			"mips1"			: arch_mips1,
			"mips32"		: arch_mips32,
			"mips32_softfloat"		: arch_mips32_softfloat,
			"mips32r2"		: arch_mips32r2,
			"mips32r2_softfloat"	: arch_mips32r2_softfloat,
			"mips3"			: arch_mips3,
			"mips3_n32"		: arch_mips3_n32,
			"mips3_n64"		: arch_mips3_n64,
			"mips3_multilib": arch_mips3_multilib,
			"mips4"			: arch_mips4,
			"mips4_n32"		: arch_mips4_n32,
			"mips4_n64"		: arch_mips4_n64,
			"mips4_multilib": arch_mips4_multilib,
			"mips4_r10k"	: arch_mips4_r10k,
			"mips4_r10k_n32": arch_mips4_r10k_n32,
			"mips4_r10k_n64": arch_mips4_r10k_n64,
			"mips4_r10k_multilib"	: arch_mips4_r10k_multilib,
			"mips64"		: arch_mips64,
			"mips64_n32"	: arch_mips64_n32,
			"mips64_n64"	: arch_mips64_n64,
			"mips64_multilib"	: arch_mips64_multilib,
			"mips64r2"		: arch_mips64r2,
			"mips64r2_n32"	: arch_mips64r2_n32,
			"mips64r2_n64"	: arch_mips64r2_n64,
			"mips64r2_multilib"	: arch_mips64r2_multilib,
			"mipsel"		: arch_mipsel1,
			"mipsel1"		: arch_mipsel1,
			"mips32el"		: arch_mips32el,
			"mips32el_softfloat"	: arch_mips32el_softfloat,
			"mips32r2el"	: arch_mips32r2el,
			"mips32r2el_softfloat"	: arch_mips32r2el_softfloat,
			"mipsel3"		: arch_mipsel3,
			"mipsel3_n32"	: arch_mipsel3_n32,
			"mipsel3_n64"	: arch_mipsel3_n64,
			"mipsel3_multilib"	: arch_mipsel3_multilib,
			"mipsel4"		: arch_mipsel4,
			"mipsel4_n32"	: arch_mipsel4_n32,
			"mipsel4_n64"	: arch_mipsel4_n64,
			"mipsel4_multilib"	: arch_mipsel4_multilib,
			"mips64el"		: arch_mips64el,
			"mips64el_n32"	: arch_mips64el_n32,
			"mips64el_n64"	: arch_mips64el_n64,
			"mips64el_multilib"	: arch_mips64el_multilib,
			"mips64r2el"	: arch_mips64r2el,
			"mips64r2el_n32"	: arch_mips64r2el_n32,
			"mips64r2el_n64"	: arch_mips64r2el_n64,
			"mips64r2el_multilib"	: arch_mips64r2el_multilib,
			"loongson2e"		: arch_loongson2e,
			"loongson2e_n32"	: arch_loongson2e_n32,
			"loongson2f"		: arch_loongson2f,
			"loongson2f_n32"	: arch_loongson2f_n32,
	}, ("mips","mips64"))
