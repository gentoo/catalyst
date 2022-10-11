
from catalyst import builder

class generic_loong(builder.generic):
	"abstract base class for all loong builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]=" -pipe"

class arch_loong(generic_loong):
	"builder class for generic loong"
	def __init__(self,myspec):
		generic_loong.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]+=" -O2"
		self.settings["CHOST"]="loongarch64-unknown-linux-gnu"

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({ "loong":arch_loong },
	("loong", ))
