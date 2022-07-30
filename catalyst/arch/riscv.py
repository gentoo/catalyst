
from catalyst import builder

class generic_riscv(builder.generic):
	"abstract base class for all riscv builders"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["COMMON_FLAGS"]="-O2 -pipe"
		self.settings["CHOST"]="riscv64-unknown-linux-gnu"

class arch_riscv(generic_riscv):
	"builder class for generic riscv"
	def __init__(self,myspec):
		generic_riscv.__init__(self,myspec)

class arch_rv64_multilib(generic_riscv):
	"builder class for rv64_multilib"
	def __init__(self,myspec):
		generic_riscv.__init__(self,myspec)

class arch_rv64_lp64d(generic_riscv):
	"builder class for rv64_lp64d"
	def __init__(self,myspec):
		generic_riscv.__init__(self,myspec)

class arch_rv64_lp64d_musl(generic_riscv):
	"builder class for rv64_lp64d_musl"
	def __init__(self,myspec):
		generic_riscv.__init__(self,myspec)
		self.settings["CHOST"]="riscv64-gentoo-linux-musl"

class arch_rv64_lp64(generic_riscv):
	"builder class for rv64_lp64"
	def __init__(self,myspec):
		generic_riscv.__init__(self,myspec)

class arch_rv64_lp64_musl(generic_riscv):
	"builder class for rv64_lp64_musl"
	def __init__(self,myspec):
		generic_riscv.__init__(self,myspec)
		self.settings["CHOST"]="riscv64-gentoo-linux-musl"

class arch_rv32_ilp32d(generic_riscv):
	"builder class for rv32_ilp32d"
	def __init__(self,myspec):
		generic_riscv.__init__(self,myspec)
		self.settings["CHOST"]="riscv32-unknown-linux-gnu"

class arch_rv32_ilp32(generic_riscv):
	"builder class for rv32_ilp32"
	def __init__(self,myspec):
		generic_riscv.__init__(self,myspec)
		self.settings["CHOST"]="riscv32-unknown-linux-gnu"


def register():
	"Inform main catalyst program of the contents of this plugin."
	return ({
		"riscv"		: arch_riscv,
		"rv64_multilib"	: arch_rv64_multilib,
		"rv64_lp64d"	: arch_rv64_lp64d,
		"rv64_lp64d_musl"	: arch_rv64_lp64d_musl,
		"rv64_lp64"	: arch_rv64_lp64,
		"rv32_ilp32d"	: arch_rv32_ilp32d,
		"rv32_ilp32"	: arch_rv32_ilp32
		}, ("rv64_multilib"))
