# Copyright (C) 2013 W. Trevor King <wking@tremily.us>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"Catalyst is a release building tool used by Gentoo Linux"

import codecs as _codecs
from distutils.core import setup as _setup
import itertools as _itertools
import os as _os

from catalyst import __version__


_this_dir = _os.path.dirname(__file__)
package_name = 'catalyst'
tag = '{0}-{1}'.format(package_name, __version__)


def files(root):
	"""Iterate through all the file paths under `root`

	Distutils wants all paths to be written in the Unix convention
	(i.e. slash-separated) [1], so that's what we'll do here.

	[1]: http://docs.python.org/2/distutils/setupscript.html#writing-the-setup-script
	"""
	for dirpath, dirnames, filenames in _os.walk(root):
		for filename in filenames:
			path = _os.path.join(dirpath, filename)
			if _os.path.sep != '/':
				path = path.replace(_os.path.sep, '/')
			yield path


_setup(
	name=package_name,
	version=__version__,
	maintainer='Gentoo Release Engineering',
	maintainer_email='releng@gentoo.org',
	url='http://www.gentoo.org/proj/en/releng/{0}/'.format(package_name),
	download_url='http://git.overlays.gentoo.org/gitweb/?p=proj/{0}.git;a=snapshot;h={1};sf=tgz'.format(package_name, tag),
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
		'Programming Language :: Python :: 2.6',
		'Programming Language :: Python :: 2.7',
		],
	scripts=['bin/{0}'.format(package_name)],
	packages=[
		package_name,
		'{0}.arch'.format(package_name),
		'{0}.base'.format(package_name),
		'{0}.targets'.format(package_name),
		],
	data_files=[
		('/etc/catalyst', [
			'etc/catalyst.conf',
			'etc/catalystrc',
			]),
		('lib/catalyst/', list(_itertools.chain(
			files('livecd'),
			files('targets'),
			))),
		],
	provides=[package_name],
	)
