import builder,os,catalyst_support

# This module defines the various "builder" classes for the various x86
# sub-arches. For example, we have a class to handle building of Pentium 4
# sub-arches, one for i686, etc. We also have a function called register
# that's called from the main catalyst program, which the main catalyst
# program uses to become informed of the various sub-arches supported by
# this module, as well as which classes should be used to build each 
# particular sub-architecture.

class generic_x86(builder.generic):
	"abstract base class for all x86 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="x86"
		if self.settings["hostarch"]=="amd64":
			if not os.path.exists("/usr/bin/linux32"):
				raise CatalystError,"required /usr/bin/linux32 executable not found (\"emerge linux32\" to fix.)"
			self.settings["CHROOT"]="linux32 chroot"
		else:
			self.settings["CHROOT"]="chroot"

class arch_x86(generic_x86):
	"builder class for generic x86 (386+)"
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=i686 -fomit-frame-pointer"
		self.settings["CHOST"]="i386-pc-linux-gnu"

class arch_i386(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=i386 -fomit-frame-pointer"

class arch_i486(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=i486 -fomit-frame-pointer"
		self.settings["CHOST"]="i486-pc-linux-gnu"

class arch_i586(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=i586 -fomit-frame-pointer"
		self.settings["CHOST"]="i586-pc-linux-gnu"

class arch_pentium_mmx(arch_i586):
	def __init__(self,myspec):
		arch_i586.__init__(self,myspec)
		self.settings["HOSTUSE"]=["mmx"]
	
class arch_i686(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=i686 -fomit-frame-pointer"
		self.settings["CHOST"]="i686-pc-linux-gnu"

class arch_athlon(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=athlon -fomit-frame-pointer"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSE"]=["mmx","3dnow"]

class arch_athlon_xp(generic_x86):
	#this handles XP and MP processors
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=athlon-xp -fomit-frame-pointer"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSE"]=["mmx","3dnow"]

class arch_pentium4(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=pentium4 -fomit-frame-pointer -finline-functions -finline-limit=800"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSE"]=["mmx","sse"]

class arch_pentium3(generic_x86):
	def __init__(self,myspec):
		generic_x86.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -march=pentium3 -fomit-frame-pointer -finline-functions -finline-limit=800"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSE"]=["mmx","sse"]

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({"pentium4":arch_pentium4,"x86":arch_x86,"i386":arch_i386,"i486":arch_i486,"i586":arch_i586,"i686":arch_i686,"athlon":arch_athlon,
	"athlon-xp":arch_athlon_xp,"athlon-mp":arch_athlon_xp,"pentium3":arch_pentium3,"pentium-mmx":arch_pentium_mmx})
		
