from catalyst import builder

class generic_ppc(builder.generic):
	"abstract base class for all 32-bit powerpc builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHOST"]="powerpc-unknown-linux-gnu"
		self.settings['setarch_build'] = 'ppc64'
		self.settings['setarch_arch'] = 'linux32'
		self.settings["PROFILE_ARCH"] = "ppc"

class generic_ppc64(builder.generic):
	"abstract base class for all 64-bit powerpc builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["PROFILE_ARCH"] = "ppc64"

class arch_ppc(generic_ppc):
	"builder class for generic powerpc"
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -mcpu=powerpc -mtune=powerpc -pipe"

class arch_ppc64(generic_ppc64):
	"builder class for generic ppc64"
	def __init__(self,myspec):
		generic_ppc64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="powerpc64-unknown-linux-gnu"

class arch_ppc64le(generic_ppc64):
	"builder class for generic ppc64le"
	def __init__(self,myspec):
		generic_ppc64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="powerpc64le-unknown-linux-gnu"

class arch_970(arch_ppc64):
	"builder class for 970 aka G5 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe -mcpu=970 -mtune=970"
		self.settings["HOSTUSE"]=["altivec"]

class arch_cell(arch_ppc64):
	"builder class for cell under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe -mcpu=cell -mtune=cell"
		self.settings["HOSTUSE"]=["altivec","ibm"]

class arch_g3(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -mcpu=G3 -mtune=G3 -pipe"

class arch_g4(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -mcpu=G4 -mtune=G4 -maltivec -mabi=altivec -pipe"
		self.settings["HOSTUSE"]=["altivec"]

class arch_g5(generic_ppc):
	def __init__(self,myspec):
		generic_ppc.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -mcpu=G5 -mtune=G5 -maltivec -mabi=altivec -pipe"
		self.settings["HOSTUSE"]=["altivec"]

class arch_power5(arch_ppc64):
	"builder class for power5 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe -mcpu=power5 -mtune=power5"
		self.settings["HOSTUSE"]=["ibm"]

class arch_power6(arch_ppc64):
	"builder class for power6 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe -mcpu=power6 -mtune=power6"
		self.settings["HOSTUSE"]=["altivec","ibm"]

class arch_power7(arch_ppc64):
	"builder class for power7 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe -mcpu=power7 -mtune=power7 -mabi=elfv2"
		self.settings["HOSTUSE"]=["altivec","ibm"]

class arch_power7le(arch_ppc64le):
	"builder class for power7 under ppc64le"
	def __init__(self,myspec):
		arch_ppc64le.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe -mcpu=power7 -mtune=power7 -mabi=elfv2"
		self.settings["HOSTUSE"]=["altivec","ibm"]

class arch_power8(arch_ppc64):
	"builder class for power8 under ppc64"
	def __init__(self,myspec):
		arch_ppc64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe -mcpu=power8 -mtune=power8 -mabi=elfv2"
		self.settings["HOSTUSE"]=["altivec","ibm"]

class arch_power8le(arch_ppc64le):
	"builder class for power8 under ppc64le"
	def __init__(self,myspec):
		arch_ppc64le.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe -mcpu=power8 -mtune=power8 -mabi=elfv2"
		self.settings["HOSTUSE"]=["altivec","ibm"]

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({
		"970"		: arch_970,
		"cell"		: arch_cell,
		"g3"		: arch_g3,
		"g4"		: arch_g4,
		"g5"		: arch_g5,
		"power5"	: arch_power5,
		"power6"	: arch_power6,
		"power7"	: arch_power7,
		"power7le"	: arch_power7le,
		"power8"	: arch_power8,
		"power8le"	: arch_power8le,
		"ppc"		: arch_ppc,
		"ppc64"		: arch_ppc64,
		"ppc64le"	: arch_ppc64le,
	}, ("ppc","ppc64","ppc64le","powerpc","powerpc64","powerpc64le"))
