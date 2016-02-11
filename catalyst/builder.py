import os

class generic(object):
	def __init__(self,myspec):
		self.settings=myspec
		self.settings.setdefault('CHROOT', 'chroot')

	def setarch(self, arch):
		"""Set the chroot wrapper to run through `setarch |arch|`

		Useful for building x86-on-amd64 and such.
		"""
		if os.uname()[0] == 'Linux':
			self.settings['CHROOT'] = 'setarch %s %s' % (arch, self.settings['CHROOT'])

	def mount_safety_check(self):
		"""
		Make sure that no bind mounts exist in chrootdir (to use before
		cleaning the directory, to make sure we don't wipe the contents of
		a bind mount
		"""
		pass

	def mount_all(self):
		"""do all bind mounts"""
		pass

	def umount_all(self):
		"""unmount all bind mounts"""
		pass
