# Copyright 1999-2004 Gentoo Technologies, Inc.
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/builder.py,v 1.5 2004/02/11 03:31:55 zhen Exp $

class generic:
	def __init__(self,myspec):
		self.settings=myspec
	def mount_safety_check(self):
		"""make sure that no bind mounts exist in chrootdir (to use before
		cleaning the directory, to make sure we don't wipe the contents of
		a bind mount"""
		pass
	def mount_all(self):
		"""do all bind mounts"""
		pass
	def umount_all(self):
		"""unmount all bind mounts"""
		pass
