
import os,catalyst.arch
from catalyst.error import *

class generic_ppc(catalyst.arch.generic_arch):
	"abstract base class for all 32-bit powerpc builders"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHOST"]="powerpc-unknown-linux-gnu"
		if self.settings["buildarch"]=="ppc64":
			if not os.path.exists("/bin/linux32") and not os.path.exists("/usr/bin/linux32"):
				raise CatalystError,"required executable linux32 not found (\"emerge setarch\" to fix.)"
			self.settings["CHROOT"]="linux32 chroot"
			self.settings["crosscompile"] = False;
		else:
			self.settings["CHROOT"]="chroot"

class generic_ppc64(catalyst.arch.generic_arch):
	"abstract base class for all 64-bit powerpc builders"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"

class arch_ppc(generic_ppc):
	"builder class for generic powerpc"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=powerpc -mtune=powerpc -fno-strict-aliasing -pipe"

class arch_ppc64(generic_ppc64):
	"builder class for generic ppc64"
	def __init__(self,myspec):
		generic_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="powerpc64-unknown-linux-gnu"

class arch_970(arch_ppc64):
	"builder class for 970 aka G5 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe -mcpu=970 -mtune=970"
		self.settings["HOSTUSE"]=["altivec"]

class arch_cell(arch_ppc64):
	"builder class for cell under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe -mcpu=cell -mtune=cell"
		self.settings["HOSTUSE"]=["altivec","ibm"]

class arch_g3(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=G3 -mtune=G3 -fno-strict-aliasing -pipe"

class arch_g4(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=G4 -mtune=G4 -maltivec -mabi=altivec -fno-strict-aliasing -pipe"
		self.settings["HOSTUSE"]=["altivec"]

class arch_g5(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=G5 -mtune=G5 -maltivec -mabi=altivec -fno-strict-aliasing -pipe"
		self.settings["HOSTUSE"]=["altivec"]

class arch_power(generic_ppc):
	"builder class for generic power"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=power -mtune=power -fno-strict-aliasing -pipe"

class arch_power_ppc(generic_ppc):
	"builder class for generic powerpc/power"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=common -mtune=common -fno-strict-aliasing -pipe"

class arch_power3(arch_ppc64):
	"builder class for power3 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe -mcpu=power3 -mtune=power3"
		self.settings["HOSTUSE"]=["ibm"]

class arch_power4(arch_ppc64):
	"builder class for power4 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe -mcpu=power4 -mtune=power4"
		self.settings["HOSTUSE"]=["ibm"]

class arch_power5(arch_ppc64):
	"builder class for power5 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe -mcpu=power5 -mtune=power5"
		self.settings["HOSTUSE"]=["ibm"]

class arch_power6(arch_ppc64):
	"builder class for power6 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe -mcpu=power6 -mtune=power6"
		self.settings["HOSTUSE"]=["altivec","ibm"]

__subarch_map = {
	"970"		: arch_970,
	"cell"		: arch_cell,
	"g3"		: arch_g3,
	"g4"		: arch_g4,
	"g5"		: arch_g5,
	"power"		: arch_power,
	"power-ppc"	: arch_power_ppc,
	"power3"	: arch_power3,
	"power4"	: arch_power4,
	"power5"	: arch_power5,
	"power6"	: arch_power6,
	"ppc"		: arch_ppc,
	"ppc64"		: arch_ppc64
}

__machine_map = ("ppc","ppc64","powerpc","powerpc64")

