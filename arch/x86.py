
import builder,os
from catalyst_support import *

class generic_x86(builder.generic):
	"abstract base class for all x86 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		if self.settings["buildarch"]=="amd64":
			if not os.path.exists("/bin/linux32") and not os.path.exists("/usr/bin/linux32"):
					raise CatalystError,"required executable linux32 not found (\"emerge setarch\" to fix.)"
			self.settings["CHROOT"]="linux32 chroot"
			self.settings["crosscompile"] = False;
		else:
			self.settings["CHROOT"]="chroot"

class arch_x86(generic_x86):
	"builder class for generic x86 (386+)"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mtune=i686 -pipe"
		self.settings["CHOST"]="i386-pc-linux-gnu"

class arch_i386(generic_x86):
	"Intel i386 CPU"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=i386 -pipe"
		self.settings["CHOST"]="i386-pc-linux-gnu"

class arch_i486(generic_x86):
	"Intel i486 CPU"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=i486 -pipe"
		self.settings["CHOST"]="i486-pc-linux-gnu"

class arch_i586(generic_x86):
	"Intel Pentium CPU"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=i586 -pipe"
		self.settings["CHOST"]="i586-pc-linux-gnu"

class arch_i686(generic_x86):
	"Intel Pentium Pro CPU"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=i686 -pipe"
		self.settings["CHOST"]="i686-pc-linux-gnu"

class arch_pentium_mmx(generic_x86):
	"Intel Pentium MMX CPU with MMX support"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=pentium-mmx -pipe"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx"]}

class arch_pentium2(generic_x86):
	"Intel Pentium 2 CPU with MMX support"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=pentium2 -pipe"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx"]}

class arch_pentium3(generic_x86):
	"Intel Pentium 3 CPU with MMX and SSE support"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=pentium3 -pipe"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx","sse"]}

class arch_pentium4(generic_x86):
	"Intel Pentium 4 CPU with MMX, SSE and SSE2 support"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=pentium4 -pipe"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx","sse","sse2"]}

class arch_pentium_m(generic_x86):
	"Intel Pentium M CPU with MMX, SSE and SSE2 support"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=pentium-m -pipe"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx","sse","sse2"]}

class arch_prescott(generic_x86):
	"improved version of Intel Pentium 4 CPU with MMX, SSE, SSE2 and SSE3 support"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=prescott -pipe"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx","sse","sse2"]}
		self.settings["CHOST"]="i686-pc-linux-gnu"

class arch_k6(generic_x86):
	"AMD K6 CPU with MMX support"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=k6 -pipe"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx"]}

class arch_k6_2(generic_x86):
	"AMD K6-2 CPU with MMX and 3dNOW! support"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=k6-2 -pipe"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx","3dnow"]}

class arch_athlon(generic_x86):
	"AMD Athlon CPU with MMX, 3dNOW!, enhanced 3dNOW! and SSE prefetch support"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=athlon -pipe"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx","3dnow"]}

class arch_athlon_xp(generic_x86):
	"improved AMD Athlon CPU with MMX, 3dNOW!, enhanced 3dNOW! and full SSE support"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=athlon-xp -pipe"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSEEXPAND"]={"CPU_FLAGS_X86":["mmx","3dnow","sse"]}

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({
		"x86"			: arch_x86,
		"i386"			: arch_i386,
		"i486"			: arch_i486,
		"i586"			: arch_i586,
		"i686"			: arch_i686,
		"pentium"		: arch_i586,
		"pentium2"		: arch_pentium2,
		"pentium3"		: arch_pentium3,
		"pentium3m"		: arch_pentium3,
		"pentium-m"		: arch_pentium_m,
		"pentium4"		: arch_pentium4,
		"pentium4m"		: arch_pentium4,
		"pentiumpro"		: arch_i686,
		"pentium-mmx"		: arch_pentium_mmx,
		"prescott"		: arch_prescott,
		"k6"			: arch_k6,
		"k6-2"			: arch_k6_2,
		"k6-3"			: arch_k6_2,
		"athlon"		: arch_athlon,
		"athlon-tbird"		: arch_athlon,
		"athlon-4"		: arch_athlon_xp,
		"athlon-xp"		: arch_athlon_xp,
		"athlon-mp"		: arch_athlon_xp
	}, ('i386', 'i486', 'i586', 'i686'))
