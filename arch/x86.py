import builder

# This module defines the various "builder" classes for the various x86
# sub-arches. For example, we have a class to handle building of Pentium 4
# sub-arches, one for i686, etc. We also have a function called register
# that's called from the main catalyst program, which the main catalyst
# program uses to become informed of the various sub-arches supported by
# this module, as well as which classes should be used to build each 
# particular sub-architecture.

class generic_x86(builder.generic):
	"abstract base class for all x86 builders"
	def __init__(self):
		self.settings["mainarch"]="x86"

class arch_x86(generic_x86):
	"builder class for generic x86 (486+)"
	def __init__(self):
		base_x86.__init__(self)
		self.settings["CFLAGS"]="-O2 -mcpu=i686 -fomit-frame-pointer"

class arch_pentium4(generic_x86):
	"builder class for Pentium 4"
	def __init__(self):
		base_x86.__init__(self)
		self.settings["CFLAGS"]="-O2 -mcpu=i686 -fomit-frame-pointer"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSE"]=["mmx","sse"]

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({"pentium4":arch_pentium4,"x86":arch_x86})
		
