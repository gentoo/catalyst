
import catalyst.arch

class generic_alpha(catalyst.arch.generic_arch):
	"abstract base class for all alpha builders"
	def __init__(self,myspec):
		catalyst.arch.generic_arch.__init__(self,myspec)
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-mieee -pipe"

class arch_alpha(generic_alpha):
	"builder class for generic alpha (ev4+)"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -O2 -mcpu=ev4"
		self.settings["CHOST"]="alpha-unknown-linux-gnu"

class arch_ev4(generic_alpha):
	"builder class for alpha ev4"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -O2 -mcpu=ev4"
		self.settings["CHOST"]="alphaev4-unknown-linux-gnu"

class arch_ev45(generic_alpha):
	"builder class for alpha ev45"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -O2 -mcpu=ev45"
		self.settings["CHOST"]="alphaev45-unknown-linux-gnu"

class arch_ev5(generic_alpha):
	"builder class for alpha ev5"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -O2 -mcpu=ev5"
		self.settings["CHOST"]="alphaev5-unknown-linux-gnu"

class arch_ev56(generic_alpha):
	"builder class for alpha ev56 (ev5 plus BWX)"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -O2 -mcpu=ev56"
		self.settings["CHOST"]="alphaev56-unknown-linux-gnu"

class arch_pca56(generic_alpha):
	"builder class for alpha pca56 (ev5 plus BWX & MAX)"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -O2 -mcpu=pca56"
		self.settings["CHOST"]="alphaev56-unknown-linux-gnu"

class arch_ev6(generic_alpha):
	"builder class for alpha ev6"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -O2 -mcpu=ev6"
		self.settings["CHOST"]="alphaev6-unknown-linux-gnu"
		self.settings["HOSTUSE"]=["ev6"]

class arch_ev67(generic_alpha):
	"builder class for alpha ev67 (ev6 plus CIX)"
	def __init__(self,myspec):
		generic_alpha.__init__(self,myspec)
		self.settings["CFLAGS"]+=" -O2 -mcpu=ev67"
		self.settings["CHOST"]="alphaev67-unknown-linux-gnu"
		self.settings["HOSTUSE"]=["ev6"]

_subarch_map = {
	"alpha": arch_alpha,
	"ev4": arch_ev4,
	"ev45": arch_ev45,
	"ev5": arch_ev5,
	"ev56": arch_ev56,
	"pca56": arch_pca56,
	"ev6": arch_ev6,
	"ev67": arch_ev67
}

_machine_map = ("alpha", )

# vim: ts=4 sw=4 sta noet sts=4 ai
