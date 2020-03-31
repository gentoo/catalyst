
from catalyst import builder

class generic_amd64(builder.generic):
	"abstract base class for all amd64 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)

class arch_amd64(generic_amd64):
	"builder class for generic amd64 (Intel and AMD)"
	def __init__(self,myspec):
		generic_amd64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe"

class arch_nocona(generic_amd64):
	"improved version of Intel Pentium 4 CPU with 64-bit extensions, MMX, SSE, SSE2 and SSE3 support"
	def __init__(self,myspec):
		generic_amd64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -march=nocona -pipe"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx","mmxext","sse","sse2","sse3"]}

class arch_core2(generic_amd64):
	"Intel Core 2 CPU with 64-bit extensions, MMX, SSE, SSE2, SSE3 and SSSE3 support"
	def __init__(self,myspec):
		generic_amd64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -march=core2 -pipe"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx","mmxext","sse","sse2","sse3","ssse3"]}

class arch_k8(generic_amd64):
	"generic k8, opteron and athlon64 support"
	def __init__(self,myspec):
		generic_amd64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -march=k8 -pipe"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx","mmxext","3dnow","3dnowext","sse","sse2"]}

class arch_k8_sse3(generic_amd64):
	"improved versions of k8, opteron and athlon64 with SSE3 support"
	def __init__(self,myspec):
		generic_amd64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -march=k8-sse3 -pipe"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx","mmxext","3dnow","3dnowext","sse","sse2","sse3"]}

class arch_amdfam10(generic_amd64):
	"AMD Family 10h core based CPUs with x86-64 instruction set support"
	def __init__(self,myspec):
		generic_amd64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -march=amdfam10 -pipe"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx","mmxext","3dnow","3dnowext","sse","sse2","sse3","sse4a"]}

class arch_x32(generic_amd64):
	"builder class for generic x32 (Intel and AMD)"
	def __init__(self,myspec):
		generic_amd64.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe"

def register():
	"inform main catalyst program of the contents of this plugin"
	return ({
		"amd64"		: arch_amd64,
		"k8"		: arch_k8,
		"opteron"	: arch_k8,
		"athlon64"	: arch_k8,
		"athlonfx"	: arch_k8,
		"nocona"	: arch_nocona,
		"core2"		: arch_core2,
		"k8-sse3"	: arch_k8_sse3,
		"opteron-sse3"	: arch_k8_sse3,
		"athlon64-sse3"	: arch_k8_sse3,
		"amdfam10"	: arch_amdfam10,
		"barcelona"	: arch_amdfam10,
		"x32"		: arch_x32,
	}, ("x86_64","amd64","nocona"))
