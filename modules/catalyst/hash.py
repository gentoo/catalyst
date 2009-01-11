"""
This module contains functions for generating the CONTENTS and hash files
"""

import os
from catalyst.error import *

def generate_contents(file, contents_function="auto", verbose=False):
	try:
		_ = contents_function
		if _ == 'auto' and file.endswith('.iso'):
			_ = 'isoinfo-l'
		if (_ in ['tar-tv','auto']):
			if file.endswith('.tgz') or file.endswith('.tar.gz'):
				_ = 'tar-tvz'
			elif file.endswith('.tbz2') or file.endswith('.tar.bz2'):
				_ = 'tar-tvj'
			elif file.endswith('.tar'):
				_ = 'tar-tv'

		if _ == 'auto':
			warn('File %r has unknown type for automatic detection.' % (file, ))
			return None
		else:
			contents_function = _
			_ = contents_map[contents_function]
			return _[0](file,_[1],verbose)
	except:
		raise CatalystError, \
			"Error generating contents, is appropriate utility (%s) installed on your system?" \
			% (contents_function, )

def calc_contents(file, cmd, verbose):
	cmd = cmd % { 'file': file }
	a = os.popen(cmd)
	result = "".join(a.readlines())
	a.close()
	if verbose:
		print result
	return result

# This has map must be defined after the function calc_content
# It is possible to call different functions from this but they must be defined
# before hash_map
# Key,function,cmd
contents_map = {
	# 'find' is disabled because it requires the source path, which is not
	# always available
	#"find"		:[calc_contents,"find %(path)s"],
	"tar-tv":[calc_contents,"tar tvf %(file)s"],
	"tar-tvz":[calc_contents,"tar tvzf %(file)s"],
	"tar-tvj":[calc_contents,"tar tvjf %(file)s"],
	"isoinfo-l":[calc_contents,"isoinfo -l -i %(file)s"],
	# isoinfo-f should be a last resort only
	"isoinfo-f":[calc_contents,"isoinfo -f -i %(file)s"],
}

def generate_hash(file, hash_function="crc32", verbose=False):
	try:
		return hash_map[hash_function][0](file, hash_map[hash_function][1], hash_map[hash_function][2], \
			hash_map[hash_function][3],verbose)
	except:
		raise CatalystError, "Error generating hash, is appropriate utility installed on your system?"

def calc_hash(file, cmd, cmd_args, id_string="MD5", verbose=False):
	a = os.popen(cmd + " " + cmd_args + " " + file)
	result = a.readline().split()[0]
	a.close()
	if verbose:
		print "%s (%s) = %s" % (id_string, file, result)
	return result

def calc_hash2(file, cmd, cmd_args, id_string="MD5", verbose=False):
	a = os.popen(cmd + " " + cmd_args + " " + file)
	header = a.readline()
	myline = a.readline().split()
	a.close()
	hash = myline[0]
	short_file = os.path.split(myline[1])[1]
	result = header + hash + "  " + short_file + "\n"
	if verbose:
		print "%s (%s) = %s" % (header, short_file, result)
	return result

# This has map must be defined after the function calc_hash
# It is possible to call different functions from this but they must be defined
# before hash_map
# Key,function,cmd,cmd_args,Print string
hash_map={
	 "adler32":[calc_hash2,"shash","-a ADLER32","ADLER32"],
	 "crc32":[calc_hash2,"shash","-a CRC32","CRC32"],
	 "crc32b":[calc_hash2,"shash","-a CRC32B","CRC32B"],
	 "gost":[calc_hash2,"shash","-a GOST","GOST"],
	 "haval128":[calc_hash2,"shash","-a HAVAL128","HAVAL128"],
	 "haval160":[calc_hash2,"shash","-a HAVAL160","HAVAL160"],
	 "haval192":[calc_hash2,"shash","-a HAVAL192","HAVAL192"],
	 "haval224":[calc_hash2,"shash","-a HAVAL224","HAVAL224"],
	 "haval256":[calc_hash2,"shash","-a HAVAL256","HAVAL256"],
	 "md2":[calc_hash2,"shash","-a MD2","MD2"],
	 "md4":[calc_hash2,"shash","-a MD4","MD4"],
	 "md5":[calc_hash2,"shash","-a MD5","MD5"],
	 "ripemd128":[calc_hash2,"shash","-a RIPEMD128","RIPEMD128"],
	 "ripemd160":[calc_hash2,"shash","-a RIPEMD160","RIPEMD160"],
	 "ripemd256":[calc_hash2,"shash","-a RIPEMD256","RIPEMD256"],
	 "ripemd320":[calc_hash2,"shash","-a RIPEMD320","RIPEMD320"],
	 "sha1":[calc_hash2,"shash","-a SHA1","SHA1"],
	 "sha224":[calc_hash2,"shash","-a SHA224","SHA224"],
	 "sha256":[calc_hash2,"shash","-a SHA256","SHA256"],
	 "sha384":[calc_hash2,"shash","-a SHA384","SHA384"],
	 "sha512":[calc_hash2,"shash","-a SHA512","SHA512"],
	 "snefru128":[calc_hash2,"shash","-a SNEFRU128","SNEFRU128"],
	 "snefru256":[calc_hash2,"shash","-a SNEFRU256","SNEFRU256"],
	 "tiger":[calc_hash2,"shash","-a TIGER","TIGER"],
	 "tiger128":[calc_hash2,"shash","-a TIGER128","TIGER128"],
	 "tiger160":[calc_hash2,"shash","-a TIGER160","TIGER160"],
	 "whirlpool":[calc_hash2,"shash","-a WHIRLPOOL","WHIRLPOOL"],
}
