class generic_target:
	def __init__(self):
		self.settings={}

class base_x86(generic_target):
	def __init__(self):
		self.settings["mainarch"]="x86"

class arch_x86(base_x86):
	def __init__(self):
		base_x86.__init__(self)
		self.settings["CFLAGS"]="-O2 -mcpu=i686 -fomit-frame-pointer"

class arch_pentium4(base_x86):
	def __init__(self):
		base_x86.__init__(self)
		self.settings["CFLAGS"]="-O2 -mcpu=i686 -fomit-frame-pointer"
		self.settings["CHOST"]="i686-pc-linux-gnu"
		self.settings["HOSTUSE"]=["mmx","sse"]

class x86_factory:
	def __init__(self):
		self.subarchdict={"x86":arch_x86,"pentium4":arch_pentium4}
	def get_target(self,target):
		if self.subarchdict.has_key(target):
			return self.subarchdict[target]()
	def is_target(self,target):
		return target in self.subarchdict.keys()


		
