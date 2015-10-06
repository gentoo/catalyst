
import re
from catalyst.support import CatalystError

class ParserBase(object):

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
			raise CatalystError("Could not open file " + filename,
				print_traceback=True)
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

		trailing_comment=re.compile(r'\s*#.*$')
		#white_space=re.compile('\s+')

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

#				# Check that this key doesn't exist already in the spec
#				if mobjs[0] in values:
#					raise Exception("You have a duplicate key (" + mobjs[0] + ") in your spec. Please fix it")

				# Start a new array using the first element of mobjs
				cur_array = [mobjs[0]]
				if mobjs[1]:
					# do any variable substitiution embeded in it with
					# the values already obtained
					mobjs[1] = mobjs[1] % values
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
					raise CatalystError("Syntax error: %s" % x, print_traceback=True)

			# XXX: Do we really still need this "single value is a string" behavior?
			if len(cur_array) == 2:
				values[cur_array[0]] = cur_array[1]
			else:
				values[cur_array[0]] = cur_array[1:]

		if not self.empty_values:
			for x in values.keys():
				# Delete empty key pairs
				if not values[x]:
					print "\n\tWARNING: No value set for key " + x + "...deleting"
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
