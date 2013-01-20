
import os
from collections import namedtuple
from subprocess import Popen, PIPE

from support import CatalystError


class HashMap(object):
	'''Class for handling
	Catalyst's hash generation'''

	fields = ["func", "cmd", "args", "id"]


	def __init__(self, hashes=None):
		'''Class init

		@param hashes: dictionary of Key:[function, cmd, cmd_args, Print string]
		@param fields: list of ordered field names for the hashes
			eg: ["func", "cmd", "args", "id"]
		'''
		if hashes is None:
			hashes = {}
		#self.hashes = {}
		self.hash_map = {}

		# create the hash definition namedtuple classes
		for name in list(hashes):
			#obj = self.hashes[name] = namedtuple(name, self.fields)
			obj = namedtuple(name, self.fields)
			obj.__slots__ = ()
			self.hash_map[name] = obj._make(hashes[name])
		del obj


	def generate_hash(self, file_, hash_="crc32", verbose=False):
		'''Prefered method of generating a hash for the passed in file_

		@param file_: the file to generate the hash for
		@param hash_: the hash algorythm to use
		@param verbose: boolean
		@returns the hash result
		'''
		try:
			return getattr(self, self.hash_map[hash_].func)(
				file_,
				hash_,
				verbose
				)
		except:
			raise CatalystError("Error generating hash, is appropriate " + \
				"utility installed on your system?", traceback=True)


	def calc_hash(self, file_, hash_, verbose=False):
		'''
		Calculate the hash for "file_"

		@param file_: the file to generate the hash for
		@param hash_: the hash algorythm to use
		@param verbose: boolean
		@returns the hash result
		'''
		_hash = self.hash_map[hash_]
		args = [_hash.cmd]
		args.extend(_hash.args)
		args.append(file_)
		source = Popen(args, stdout=PIPE)
		mylines = source.communicate()[0]
		mylines=mylines[0].split()
		result=mylines[0]
		if verbose:
			print _hash.id + " (%s) = %s" % (file_, result)
		return result


	def calc_hash2(self, file_, hash_type, verbose=False):
		'''
		Calculate the hash for "file_"

		@param file_: the file to generate the hash for
		@param hash_: the hash algorythm to use
		@param verbose: boolean
		@returns the hash result
		'''
		_hash = self.hash_map[hash_type]
		args = [_hash.cmd]
		args.extend(_hash.args)
		args.append(file_)
		#print("DEBUG: calc_hash2; args =", args)
		source = Popen(args, stdout=PIPE)
		output = source.communicate()
		lines = output[0].split('\n')
		#print("DEBUG: calc_hash2; output =", output)
		header = lines[0]
		h_f = lines[1].split()
		hash_result = h_f[0]
		short_file = os.path.split(h_f[1])[1]
		result = header + hash_result + "  " + short_file + "\n"
		if verbose:
			print header+" (%s) = %s" % (short_file, result)
		return result



