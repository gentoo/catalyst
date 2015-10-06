"""Catalyst is a release building tool used by Gentoo Linux"""

from __future__ import print_function

import codecs as _codecs
from distutils.core import setup as _setup, Command as _Command
from email.utils import parseaddr as _parseaddr
import os as _os

from catalyst import __version__, __maintainer__
from catalyst.version import set_release_version as _set_release_version
from catalyst.version import get_version as _get_version


_this_dir = _os.path.dirname(__file__)
_package_name = 'catalyst'
_maintainer_name, _maintainer_email = _parseaddr(__maintainer__)


def _posix_path(path):
	"""Convert a native path to a POSIX path

	Distutils wants all paths to be written in the Unix convention
	(i.e. slash-separated) [1], so that's what we'll do here.

	[1]: https://docs.python.org/2/distutils/setupscript.html
	"""
	if _os.path.sep != '/':
		return path.replace(_os.path.sep, '/')
	return path


def _files(prefix, root):
	"""Iterate through all the file paths under `root`

	Yielding `(target_dir, (file_source_paths, ...))` tuples.
	"""
	for dirpath, _dirnames, filenames in _os.walk(root):
		reldir = _os.path.relpath(dirpath, root)
		install_directory = _posix_path(
			_os.path.join(prefix, reldir))
		file_source_paths = [
			_posix_path(_os.path.join(dirpath, filename))
			for filename in filenames]
		yield (install_directory, file_source_paths)


_data_files = [('/etc/catalyst', ['etc/catalyst.conf','etc/catalystrc']),
	('/usr/share/man/man1', ['files/catalyst.1']),
	('/usr/share/man/man5', ['files/catalyst-config.5', 'files/catalyst-spec.5'])
	]
_data_files.extend(_files('share/catalyst/livecd', 'livecd'))
_data_files.extend(_files('share/catalyst/targets', 'targets'))


class set_version(_Command):
	'''Saves the specified release version information
	'''
	description = "hardcode script's version using VERSION from environment"
	user_options = []  # [(long_name, short_name, desc),]

	def initialize_options (self):
		pass

	def finalize_options (self):
		pass

	def run(self):
		# pylint: disable=global-statement
		global __version__
		try:
			version = _os.environ['VERSION']
		except KeyError:
			print("Try setting 'VERSION=x.y.z' on the command line... Aborting")
			return
		_set_release_version(version)
		__version__ = _get_version()
		print("Version set to:\n", __version__)


_setup(
	name=_package_name,
	version=__version__,
	maintainer=_maintainer_name,
	maintainer_email=_maintainer_email,
	url='https://wiki.gentoo.org/wiki/Catalyst',
	download_url='http://distfiles.gentoo.org/distfiles/{0}-{1}.tar.bz2'.format(
		_package_name, __version__),
	license='GNU General Public License (GPL)',
	platforms=['all'],
	description=__doc__,
	long_description=_codecs.open(
		_os.path.join(_this_dir, 'README'), 'r', 'utf-8').read(),
	classifiers=[
		'Development Status :: 5 - Production/Stable',
		'License :: OSI Approved :: GNU General Public License v2 or later (GPLv2+)',
		'Intended Audience :: System Administrators',
		'Operating System :: POSIX',
		'Topic :: System :: Archiving :: Packaging',
		'Topic :: System :: Installation/Setup',
		'Topic :: System :: Software Distribution',
		'Programming Language :: Python :: 2',
		'Programming Language :: Python :: 2.7',
		],
	scripts=['bin/{0}'.format(_package_name)],
	packages=[
		_package_name,
		'{0}.arch'.format(_package_name),
		'{0}.base'.format(_package_name),
		'{0}.targets'.format(_package_name),
		],
	data_files=_data_files,
	provides=[_package_name],
	cmdclass={
		'set_version': set_version
		},
	)
