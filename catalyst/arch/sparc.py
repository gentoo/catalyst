
from catalyst import builder

class generic_sparc(builder.generic):
	"abstract base class for all sparc builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		if self.settings["buildarch"]=="sparc64":
			self.setarch('linux32')
			self.settings["crosscompile"] = False

class generic_sparc64(builder.generic):
	"abstract base class for all sparc64 builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)

class arch_sparc(generic_sparc):
	"builder class for generic sparc (sun4cdm)"
	def __init__(self,myspec):
		generic_sparc.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="sparc-unknown-linux-gnu"

class arch_sparc64(generic_sparc64):
	"builder class for generic sparc64 (sun4u)"
	def __init__(self,myspec):
		generic_sparc64.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -mcpu=ultrasparc -pipe"
		self.settings["CHOST"]="sparc-unknown-linux-gnu"

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({
		"sparc"		: arch_sparc,
		"sparc64"	: arch_sparc64
	}, ("sparc","sparc64", ))
