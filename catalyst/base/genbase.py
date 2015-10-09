

import os


class GenBase(object):
	"""
	This class does generation of the contents and digests files.
	"""
	def __init__(self,myspec):
		self.settings = myspec


	def gen_contents_file(self, path):
		contents = path + ".CONTENTS"
		if os.path.exists(contents):
			os.remove(contents)
		if "contents" in self.settings:
			contents_map = self.settings["contents_map"]
			if os.path.exists(path):
				myf = open(contents, "w")
				keys={}
				for i in self.settings["contents"].split():
					keys[i]=1
					array=keys.keys()
					array.sort()
				for j in array:
					contents = contents_map.contents(path, j,
						verbose=self.settings["VERBOSE"])
					if contents:
						myf.write(contents)
				myf.close()

	def gen_digest_file(self, path):
		digests = path + ".DIGESTS"
		if os.path.exists(digests):
			os.remove(digests)
		if "digests" in self.settings:
			hash_map = self.settings["hash_map"]
			if os.path.exists(path):
				myf=open(digests, "w")
				keys={}
				for i in self.settings["digests"].split():
					keys[i]=1
					array=keys.keys()
					array.sort()
				for f in [path, path + '.CONTENTS']:
					if os.path.exists(f):
						if "all" in array:
							for k in list(hash_map.hash_map):
								digest = hash_map.generate_hash(f, hash_=k)
								myf.write(digest)
						else:
							for j in array:
								digest = hash_map.generate_hash(f, hash_=j)
								myf.write(digest)
				myf.close()

