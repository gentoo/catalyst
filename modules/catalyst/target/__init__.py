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

def build_targets():
	buildplan = build_target_buildplan()

	for target in buildplan:
		try:
			target.run()
		except:
			catalyst.util.print_traceback()
			catalyst.output.warn("Error encountered during run of target " + x)
			raise

def build_target_buildplan():
	targets = []
	config = catalyst.config.config()
	spec = config.get_spec()
	spec_values = spec.get_values()
	targetmap = config.get_targetmap()

	built_targets = find_built_targets(spec_values['storedir'] + '/builds/')

	if not "targets" in spec_values or not spec_values['targets']:
		raise CatalystError, "No target(s) specified."

	for x in spec_values['targets']:
		if not x in targetmap:
			raise CatalystError("Target \"" + x + "\" is not a known target.")
		config.get_spec().set_target(x)
		target_tmp = { 'object': targetmap[x](), 'parent': '' }
		target_tmp['info'] = target_tmp['object'].get_target_info()
		target_tmp['depends'] = target_tmp['object'].depends
		targets.append(target_tmp)

	for i, target in enumerate(targets):
		if len(target['depends']) == 0:
			targets[i]['parent'] = 'pass'
			continue

		for x target['depends']:
			for y in built_targets:
				info = y.get_target_info()
				if info['target'] == y and info['version_stamp'] == target['info']['version_stamp'] and \
					info['arch'] == target['info']['arch'] and info['rel_type'] == target['info']['rel_type']:
					targets[i]['parent'] = 'built'
					break

			for y in targets:
				info = y.get_target_info()
				if info['target'] == y and info['version_stamp'] == target['info']['version_stamp'] and \
					info['arch'] == target['info']['arch'] and info['rel_type'] == target['info']['rel_type']:
					targets[i]['parent'] = info['target']
					break

		if targets[i]['parent']:
			continue

		raise CatalystError("Failed to resolve depedencies for target '%s'" % (target['info']['target'],))

	while True:
		did_something = False
		for i, target in enumerate(targets):
			if target['parent'] in ('built', 'pass'):
				continue
			else:
				for j, foo in enumerate(targets):
					if foo['target'] == target['parent']:
						if i < j:
							tmp_target = targets.pop(j)
							targets.insert(i, tmp_target)
							did_something = True
							break
				if did_something:
					break
		if not did_something:
			break

	return targets


class target:

	_target = None
	_version_stamp = None
	_arch = None
	_rel_type = None
	_media = None

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

	def get_target_info(self):
		foo = { 'target': self._target, 'arch': self._arch, 'version_stamp': self._version_stamp, 'rel_type': self._rel_type, 'media': self._media }
		return foo

class built_target(target):

	_filename = None

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

# vim: ts=4 sw=4 sta noet sts=4 ai
