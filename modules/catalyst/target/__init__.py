"""
Parent module of all target modules
"""

import os
import catalyst.util
from catalyst.output import warn

def find_target_modules():
	search_dir = os.path.abspath(os.path.dirname(__file__))
	target_module_list = [x[:-3] for x in os.listdir(search_dir) \
		if x.endswith('.py') and not x.startswith('__')]
	return target_module_list

def get_targets():
	target_modules = {}
	for x in find_target_modules():
		target_modules[x] = catalyst.util.load_module("catalyst.target." + x)
		if target_modules[x] is None:
			warn("Cannot import catalyst.target." + x + ". This usually only " + \
				"happens due to a syntax error, which should be reported as " \
				"a bug.")
	return target_modules

def build_target_map():
	target_map = {}
	targets = get_targets()
	for x in targets:
		if hasattr(targets[x], '__target_map'):
			target_map.update(targets[x].__target_map)
	return target_map

def find_built_targets(build_dir):
	built_targets = []
	for root, dir, files in os.walk(build_dir):
		for file in files:
			try:
				built_targets.append(built_target(root + '/' + file))
			except:
				catalyst.output.warn("Failed to parse '%s' as a built target" % (file,))

	return built_targets

class built_target:

	_filename = None
	_target = None
	_version_stamp = None
	_arch = None
	_rel_type = None
	_media = None

	def __init__(self, filename=None):
		if filename:
			self.parse_filename(filename)

	def parse_filename(self, filename):
		self._filename = filename

		(rel_type, file) = filename.split('/')[-2:]
		self._rel_type = rel_type
		(target_full, media) = file.split('.', 1)
		self._media = media
		target_parts = target_full.split('-')

		if len(target_parts) != 3:
			raise CatalystError("The file '%s' cannot be parsed as a built target" % (filename,))

		(target, arch, version_stamp) = target_parts

		self._target = target
		self._arch = arch
		self._version_stamp = version_stamp

	def get_target(self):
		return self._target

	def get_arch(self):
		return self._arch

	def get_version_stamp(self):
		return self._version_stamp

	def get_media(self):
		return self._media

	def get_rel_type(self):
		return self._rel_type

	def get_values(self):
		foo = { 'target': self._target, 'arch': self._arch, 'version_stamp': self._version_stamp, 'rel_type': self._rel_type, 'media': self._media }
		return foo

# vim: ts=4 sw=4 sta noet sts=4 ai
