# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.

import builder,os
from catalyst_support import *

class arch_hppa(builder.generic):
	"builder class for hppa"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="hppa"
		self.settings["CHROOT"]="chroot"
		self.settings["CFLAGS"]="-O2"
		self.settings["CHOST"]="hppa-unknown-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({ "hppa":arch_hppa })
