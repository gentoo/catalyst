import builder

# This module defines the various "builder" classes for the various x86
# sub-arches. For example, we have a class to handle building of Pentium 4
# sub-arches, one for i686, etc. We also have a function called register
# that's called from the main catalyst program, which the main catalyst
# program uses to become informed of the various sub-arches supported by
# this module, as well as which classes should be used to build each 
# particular sub-architecture.

class generic_amd64(builder.generic):
	"abstract base class for all amd64 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="amd64"
		self.settings["CHROOT"]="chroot"

class arch_amd64(generic_amd64):
	"builder class for generic amd64 (athlon64/opteron)"
	def __init__(self,myspec):
		generic_amd64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2"
		self.settings["CHOST"]="x86_64-pc-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({"amd64":arch_amd64})
		
