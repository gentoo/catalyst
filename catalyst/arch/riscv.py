
from catalyst import builder

class arch_riscv(builder.generic):
	"builder class for riscv"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="riscv64-unknown-linux-gnu"
		self.settings["PROFILE_ARCH"] = "riscv"

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({ "riscv":arch_riscv }, ("rv64","riscv64","riscv"))
