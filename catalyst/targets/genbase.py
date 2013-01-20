

import os


class GenBase(object):
	"""
	This class does generation of the contents and digests files.
	"""
	def __init__(self,myspec):
		self.settings = myspec


	def gen_contents_file(self,file):
		if os.path.exists(file+".CONTENTS"):
			os.remove(file+".CONTENTS")
		if "contents" in self.settings:
			contents_map = self.settings["contents_map"]
			if os.path.exists(file):
				myf=open(file+".CONTENTS","w")
				keys={}
				for i in self.settings["contents"].split():
					keys[i]=1
					array=keys.keys()
					array.sort()
				for j in array:
					contents = contents_map.generate_contents(file, j,
						verbose="VERBOSE" in self.settings)
					if contents:
						myf.write(contents)
				myf.close()

	def gen_digest_file(self,file):
		if os.path.exists(file+".DIGESTS"):
			os.remove(file+".DIGESTS")
		if "digests" in self.settings:
			hash_map = self.settings["hash_map"]
			if os.path.exists(file):
				myf=open(file+".DIGESTS","w")
				keys={}
				for i in self.settings["digests"].split():
					keys[i]=1
					array=keys.keys()
					array.sort()
				for f in [file, file+'.CONTENTS']:
					if os.path.exists(f):
						if "all" in array:
							for k in list(hash_map.hash_map):
								hash = hash_map.generate_hash(f,hash_=k,
									verbose = "VERBOSE" in self.settings)
								myf.write(hash)
						else:
							for j in array:
								hash = hash_map.generate_hash(f,hash_=j,
									verbose = "VERBOSE" in self.settings)
								myf.write(hash)
				myf.close()

