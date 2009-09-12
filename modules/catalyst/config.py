import re
from catalyst.error import *
from catalyst.output import *

required_config_file_values = ("storedir", "sharedir", "distdir", "portdir")
optional_config_file_values = (
	"PKGCACHE", "KERNCACHE", "CCACHE", "DISTCC", "ICECREAM", "ENVSCRIPT",
	"AUTORESUME", "FETCH", "CLEAR_AUTORESUME", "options", "DEBUG", "VERBOSE",
	"PURGE", "PURGEONLY", "SNAPCACHE", "snapshot_cache", "hash_function",
	"digests", "contents", "SEEDCACHE"
)

valid_config_file_values = required_config_file_values + optional_config_file_values

class ParserBase:

	filename = ""
	lines = None
	values = None
	key_value_separator = "="
	multiple_values = False
	empty_values = True

	def __getitem__(self, key):
		return self.values[key]

	def get_values(self):
		return self.values

	def dump(self):
		dump = ""
		for x in self.values.keys():
			dump += x + " = " + repr(self.values[x]) + "\n"
		return dump

	def parse_file(self, filename):
		try:
			myf = open(filename, "r")
		except:
			raise CatalystError, "Could not open file " + filename
		self.lines = myf.readlines()
		myf.close()
		self.filename = filename
		self.parse()

	def parse_lines(self, lines):
		self.lines = lines
		self.parse()

	def parse(self):
		values = {}
		cur_array = []

		trailing_comment=re.compile('\s*#.*$')
#		white_space=re.compile('\s+')

		for x, myline in enumerate(self.lines):
			myline = myline.strip()

			# Force the line to be clean
			# Remove Comments ( anything following # )
			myline = trailing_comment.sub("", myline)

			# Skip any blank lines
			if not myline: continue

			# Look for separator
			msearch = myline.find(self.key_value_separator)

			# If separator found assume its a new key
			if msearch != -1:
				# Split on the first occurence of the separator creating two strings in the array mobjs
				mobjs = myline.split(self.key_value_separator, 1)
				mobjs[1] = mobjs[1].strip().strip('"')

#				# Check that this key doesn't exist already in the spec
#				if mobjs[0] in values:
#					raise Exception("You have a duplicate key (" + mobjs[0] + ") in your spec. Please fix it")

				# Start a new array using the first element of mobjs
				cur_array = [mobjs[0]]
				if mobjs[1]:
					if self.multiple_values:
						# split on white space creating additional array elements
#						subarray = white_space.split(mobjs[1])
						subarray = mobjs[1].split()
						cur_array += subarray
					else:
						cur_array += [mobjs[1]]

			# Else add on to the last key we were working on
			else:
				if self.multiple_values:
#					mobjs = white_space.split(myline)
#					cur_array += mobjs
					cur_array += myline.split()
				else:
					raise CatalystError, "Syntax error: " + x

			# XXX: Do we really still need this "single value is a string" behavior?
			if len(cur_array) == 2:
				values[cur_array[0]] = cur_array[1]
			else:
				values[cur_array[0]] = cur_array[1:]

		if not self.empty_values:
			for x in values.keys():
				# Delete empty key pairs
				if not values[x]:
					msg("\n\tWARNING: No value set for key " + x + "...deleting")
					del values[x]

		self.values = values

class SpecParser(ParserBase):

	key_value_separator = ':'
	multiple_values = True
	empty_values = False

	def __init__(self, filename=""):
		if filename:
			self.parse_file(filename)

class ConfigParser(ParserBase):

	key_value_separator = '='
	multiple_values = False
	empty_values = True

	def __init__(self, filename=""):
		if filename:
			self.parse_file(filename)

class Spec:

	special_prefixes = ('boot', )
	default_values = {
		# Do we really still need this?
		'rel_type': 'default'
	}

	def __init__(self, values=None):
		self.values = { 'global': {} }
		self.target = None
		if values:
			self.parse_values(values)

	def parse_values(self, values):
		for x in values:
			parts = x.split('/')
			if len(parts) == 1 or parts[0] in self.special_prefixes:
				self.values['global'][x] = values[x]
			else:
				if not parts[0] in self.values:
					self.values[parts[0]] = {}
				self.values[parts[0]]['/'.join(parts[1:])] = values[x]
		if 'target' in self.values['global']:
			self.values['global']['targets'] = set((self.values['global']['target'], ))
			del self.values['global']['target']

	def set_target(self, target):
		self.target = target

	def get_values(self, target=None):
		tmp = {}
		tmp.update(self.default_values)
		tmp.update(self.values['global'])
		if target is None:
			target = self.target
			tmp['target'] = target
		if target in self.values:
			tmp.update(self.values[target])
		return tmp

	def compare_key(self, key1, key2):
		foo = re.compile(key1)
		return foo.match(key2)

	def validate_values(self, required, valid, target=None):
		if target is None:
			target = self.target
		values = self.get_values(target)
		for x in values:
			if x in required or x in valid:
				continue
			for y in set(required + valid):
				if not self.compare_key(y, x):
					raise CatalystError("The key '" + x + "' is not a valid key for this target")
		for y in required:
			if not y in values:
				raise CatalystError("The required key '" + y + "' was not found")

class Singleton(type):

	def __init__(self, *args):
		type.__init__(self, *args)
		self._instances = {}

	def __call__(self, *args):
		if not args in self._instances:
			self._instances[args] = type.__call__(self, *args)
		return self._instances[args]

class config:

	__metaclass__ = Singleton

	def __init__(self):
		if not hasattr(self, 'spec'):
			self.spec = None
			self.conf = {}
			self.targetmap = None

	def set_spec(self, spec):
		self.spec = spec

	def get_spec(self):
		return self.spec

	def set_conf(self, conf):
		self.conf = conf

	def update_conf(self, conf):
		self.conf.update(conf)

	def get_conf(self):
		return self.conf

	def set_targetmap(self, targetmap):
		self.targetmap = targetmap

	def get_targetmap(self):
		return self.targetmap

# vim: ts=4 sw=4 sta noet sts=4 ai
