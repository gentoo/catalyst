
import builder

class generic_ppc64(builder.generic):
	"abstract base class for all ppc64 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"

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
		self.settings["HOSTUSE"]=["altivec"]

class arch_power3(arch_ppc64):
	"builder class for power3 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe -mcpu=power3 -mtune=power3"

class arch_power4(arch_ppc64):
	"builder class for power4 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe -mcpu=power4 -mtune=power4"

class arch_power5(arch_ppc64):
	"builder class for power5 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe -mcpu=power5 -mtune=power5"

class arch_power6(arch_ppc64):
	"builder class for power6 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe -mcpu=power6 -mtune=power6"
		self.settings["HOSTUSE"]=["altivec"]

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({
		"ppc64":	arch_ppc64,
		"970":		arch_970,
		"cell":		arch_cell,
		"power3":	arch_power3,
		"power4":	arch_power4,
		"power5":	arch_power5,
		"power6":	arch_power6
	}, ("ppc64","powerpc64"))


