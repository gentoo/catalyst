
from catalyst import builder

class arch_arm64(builder.generic):
	"builder class for arm64"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CFLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="aarch64-unknown-linux-gnu"

def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({ "arm64":arch_arm64 }, ("aarch64","arm64", ))
