
from catalyst import builder

class generic_m68k(builder.generic):
	"abstract base class for all m68k builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]=" -pipe"

class arch_m68k(generic_m68k):
	"builder class for generic m68k"
	def __init__(self,myspec):
		generic_m68k.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]+=" -O2"
		self.settings["CHOST"]="m68k-unknown-linux-gnu"

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({ "m68k":arch_m68k },
	("m68k", ))
