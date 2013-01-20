
import os
from collections import namedtuple
from subprocess import Popen, PIPE

from support import CatalystError


# Use HashMap.fields for the value legend
# fields = ["func", "cmd", "args", "id"]
HASH_DEFINITIONS = {
	"adler32"  :["calc_hash2", "shash", ["-a", "ADLER32"], "ADLER32"],
	"crc32"    :["calc_hash2", "shash", ["-a", "CRC32"], "CRC32"],
	"crc32b"   :["calc_hash2", "shash", ["-a", "CRC32B"], "CRC32B"],
	"gost"     :["calc_hash2", "shash", ["-a", "GOST"], "GOST"],
	"haval128" :["calc_hash2", "shash", ["-a", "HAVAL128"], "HAVAL128"],
	"haval160" :["calc_hash2", "shash", ["-a", "HAVAL160"], "HAVAL160"],
	"haval192" :["calc_hash2", "shash", ["-a", "HAVAL192"], "HAVAL192"],
	"haval224" :["calc_hash2", "shash", ["-a", "HAVAL224"], "HAVAL224"],
	"haval256" :["calc_hash2", "shash", ["-a", "HAVAL256"], "HAVAL256"],
	"md2"      :["calc_hash2", "shash", ["-a", "MD2"], "MD2"],
	"md4"      :["calc_hash2", "shash", ["-a", "MD4"], "MD4"],
	"md5"      :["calc_hash2", "shash", ["-a", "MD5"], "MD5"],
	"ripemd128":["calc_hash2", "shash", ["-a", "RIPEMD128"], "RIPEMD128"],
	"ripemd160":["calc_hash2", "shash", ["-a", "RIPEMD160"], "RIPEMD160"],
	"ripemd256":["calc_hash2", "shash", ["-a", "RIPEMD256"], "RIPEMD256"],
	"ripemd320":["calc_hash2", "shash", ["-a", "RIPEMD320"], "RIPEMD320"],
	"sha1"     :["calc_hash2", "shash", ["-a", "SHA1"], "SHA1"],
	"sha224"   :["calc_hash2", "shash", ["-a", "SHA224"], "SHA224"],
	"sha256"   :["calc_hash2", "shash", ["-a", "SHA256"], "SHA256"],
	"sha384"   :["calc_hash2", "shash", ["-a", "SHA384"], "SHA384"],
	"sha512"   :["calc_hash2", "shash", ["-a", "SHA512"], "SHA512"],
	"snefru128":["calc_hash2", "shash", ["-a", "SNEFRU128"], "SNEFRU128"],
	"snefru256":["calc_hash2", "shash", ["-a", "SNEFRU256"], "SNEFRU256"],
	"tiger"    :["calc_hash2", "shash", ["-a", "TIGER"], "TIGER"],
	"tiger128" :["calc_hash2", "shash", ["-a", "TIGER128"], "TIGER128"],
	"tiger160" :["calc_hash2", "shash", ["-a", "TIGER160"], "TIGER160"],
	"whirlpool":["calc_hash2", "shash", ["-a", "WHIRLPOOL"], "WHIRLPOOL"],
	}


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
		self.hash_map = {}

		# create the hash definition namedtuple classes
		for name in list(hashes):
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
		result = header + "\n" + hash_result + "  " + short_file + "\n"
		if verbose:
			print header + " (%s) = %s" % (short_file, result)
		return result



