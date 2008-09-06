class spec:

	filename = ""
	speclines = None
	values = None

	def __init__(self, filename=""):
		if filename:
			self.parse(filename)

	def __getitem__(self, key):
		return self.values[key]

	def get_values(self):
		return self.values

	def dump(self):
		dump = ""
		for x in self.values.keys():
			dump += x + ": " + repr(self.values[x]) + "\n"

	def load(self, filename):
		self.filename = filename
		try:
			myf = open(filename, "r")
		except:
			raise CatalystError, "Could not open spec file " + filename
		self.speclines = myf.readlines()
		myf.close()
		self.parse()

	def parse(self):
		myspec = {}
		cur_array = []
		trailing_comment=re.compile("#.*$")
		white_space=re.compile("\s+")
		while len(self.speclines):
			myline = mylines.pop(0).strip()

			# Force the line to be clean 
			# Remove Comments ( anything following # )
			myline = trailing_comment.sub("", myline)

			# Skip any blank lines
			if not myline: continue

			# Look for colon
			msearch = myline.find(':')
		
			# If semicolon found assume its a new key
			# This may cause problems if : are used for key values but works for now
			if msearch != -1:
				# Split on the first semicolon creating two strings in the array mobjs
				mobjs = myline.split(':', 1)
				mobjs[1] = mobjs[1].strip()

				# Check that this key doesn't exist already in the spec
				if myspec.has_key(mobjs[0]):
					raise Exception("You have a duplicate key (" + mobjs[0] + ") in your spec. Please fix it")

				# Start a new array using the first element of mobjs
				cur_array = [mobjs[0]]
				if mobjs[1]:
					# split on white space creating additional array elements
					subarray = white_space.split(mobjs[1])
					if subarray:
						if len(subarray)==1:
							# Store as a string if only one element is found.
							# this is to keep with original catalyst behavior 
							# eventually this may go away if catalyst just works
							# with arrays.
							cur_array.append(subarray[0])
						else:
							cur_array += subarray
		
			# Else add on to the last key we were working on
			else:
				mobjs = white_space.split(myline)
				cur_array += mobjs
		
			# XXX: Do we really still need this "single value is a string" behavior?
			if len(cur_array) == 2:
				myspec[cur_array[0]] = cur_array[1]
			else:
				myspec[cur_array[0]] = cur_array[1:]
	
		for x in myspec.keys():
			# Delete empty key pairs
			if not myspec[x]:
				print "\n\tWARNING: No value set for key " + x + "...deleting"
				del myspec[x]
		self.values = myspec



