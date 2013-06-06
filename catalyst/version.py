#!/usr/bin/python -OO

# Maintained in full by:
# Catalyst Team <catalyst@gentoo.org>
# Release Engineering Team <releng@gentoo.org>
# Copyright: 2011 Brian Harring <ferringb@gmail.com>
# License: BSD/GPL2
# Copied & edited by: Brian Dolbec <dolsen@gentoo.org>

'''Version information and/or git version information
'''

import os

from snakeoil.version import format_version

__version__="rewrite-git"
_ver = None


def get_git_version(version=__version__):
	"""Return: a string describing our version."""
	global _ver
	_ver = format_version('catalyst',__file__, version)
	return _ver


def get_version(reset=False):
	'''Returns a saved release version string or the
	generated git release version.
	'''
	global __version__, _ver
	if _ver and not reset:
		return _ver
	try: # getting the fixed version
		from .verinfo import version
		_ver = version
		__version__ = version.split('\n')[0].split()[1]
	except ImportError: # get the live version
		version = get_git_version()
	return version



def set_release_version(version, root=None):
	'''Saves the release version along with the
	git log release information

	@param version: string
	@param root: string, optional alternate root path to save to
	'''
	#global __version__
	filename = "verinfo.py"
	if not root:
		path = os.path.join(os.path.dirname(__file__), filename)
	else:
		path = os.path.join(root, filename)
	#__version__ = version
	ver = get_git_version(version)
	with open(path, 'w') as f:
		f.write("version = {0!r}".format(ver))
