# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/arch/sh.py,v 1.1 2005/09/12 15:31:57 wolf31o2 Exp $

import builder,os
from catalyst_support import *

class generic_sh(builder.generic):
	"Abstract base class for all sh builders [Little-endian]"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="sh"
		self.settings["CHROOT"]="chroot"

class generic_sheb(builder.generic):
	"Abstract base class for all sheb builders [Big-endian]"
	def __init__(self,myspec):
		builder.generic.__init__(self,myspec)
		self.settings["mainarch"]="sh"
		self.settings["CHROOT"]="chroot"

class arch_sh3(generic_sh):
	"Builder class for SH-3 [Little-endian]"
	def __init__(self,myspec):
		generic_sh.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m3"
		self.settings["CHOST"]="sh3-unknown-linux-gnu"

class arch_sh4(generic_sh):
	"Builder class for SH-4 [Little-endian]"
	def __init__(self,myspec):
		generic_sh.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m4"
		self.settings["CHOST"]="sh4-unknown-linux-gnu"

class arch_sh3eb(generic_sheb):
	"Builder class for SH-3 [Big-endian]"
	def __init__(self,myspec):
		generic_sheb.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m3 -mb"
		self.settings["CHOST"]="sh3eb-unknown-linux-gnu"

class arch_sh4eb(generic_sheb):
	"Builder class for SH-4 [Big-endian]"
	def __init__(self,myspec):
		generic_sheb.__init__(self,myspec)
		self.settings["CFLAGS"]="-O2 -m4 -mb"
		self.settings["CHOST"]="sh4eb-unknown-linux-gnu"

def register(foo):
	"Inform main catalyst program of the contents of this plugin."
	foo.update({
			"sh"	:arch_sh3,
			"sh3"	:arch_sh3,
			"sh4"	:arch_sh4,
			"sheb"	:arch_sh3eb,
			"sh3eb"	:arch_sh3eb,
			"sh4eb"	:arch_sh4eb
	})
