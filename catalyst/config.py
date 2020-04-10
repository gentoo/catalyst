
import re

from catalyst import log
from catalyst.support import CatalystError

class ParserBase():

	filename = ""
	lines = None
	values = None
	key_value_separator = "="
	multiple_values = False
	empty_values = True
	eval_none = False

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
			with open(filename, "r") as myf:
				self.lines = myf.readlines()
		except:
			raise CatalystError("Could not open file " + filename,
				print_traceback=True)
		self.filename = filename
		self.parse()

	def parse_lines(self, lines):
		self.lines = lines
		self.parse()

	def parse(self):
		values = {}
		cur_array = []

		trailing_comment=re.compile(r'\s*#.*$')

		for x, myline in enumerate(self.lines):
			myline = myline.strip()

			# Force the line to be clean
			# Remove Comments ( anything following # )
			myline = trailing_comment.sub("", myline)

			# Skip any blank lines
			if not myline:
				continue

			if self.key_value_separator in myline:
				# Split on the first occurence of the separator creating two strings in the array mobjs
				mobjs = myline.split(self.key_value_separator, 1)
				mobjs[1] = mobjs[1].strip().strip('"')

				# Start a new array using the first element of mobjs
				cur_array = [mobjs[0]]
				if mobjs[1]:
					# do any variable substitiution embeded in it with
					# the values already obtained
					mobjs[1] = mobjs[1] % values
					if self.multiple_values:
						# split on white space creating additional array elements
						subarray = mobjs[1].split()
						cur_array += subarray
					else:
						cur_array += [mobjs[1]]

			# Else add on to the last key we were working on
			else:
				if self.multiple_values:
					cur_array += myline.split()
				else:
					raise CatalystError("Syntax error: %s" % x, print_traceback=True)

			# XXX: Do we really still need this "single value is a string" behavior?
			if len(cur_array) == 2:
				values[cur_array[0]] = cur_array[1]
			else:
				values[cur_array[0]] = cur_array[1:]

		if not self.empty_values:
			# Make sure the list of keys is static since we modify inside the loop.
			for x in list(values.keys()):
				# Delete empty key pairs
				if not values[x]:
					log.warning('No value set for key "%s"; deleting', x)
					del values[x]

		if self.eval_none:
			# Make sure the list of keys is static since we modify inside the loop.
			for x in list(values.keys()):
				# reset None values
				if isinstance(values[x], str) and values[x].lower() in ['none']:
					log.info('None value found for key "%s"; reseting', x)
					values[x] = None
		self.values = values

class SpecParser(ParserBase):

	key_value_separator = ':'
	multiple_values = True
	empty_values = False
	eval_none = True

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
