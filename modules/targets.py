import os,stat
from catalyst_support import *

class generic_target:

	def __init__(self,myspec):
		self.settings=myspec
		pass

class generic_stage_target(generic_target):

	def __init__(self,myspec):
		generic_target.__init__(self,myspec)
		#we'd want to make sure we have all the settings we need here
		self.settings["target_subpath"]=self.settings["rel_type"]+"-"+self.settings["mainarch"]+"-"+self.settings["rel_version"]
		self.settings["target_subpath"]+="/"+self.settings["target"]+"-"+self.settings["subarch"]+"-"+self.settings["version_stamp"]
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=st+"/snapshots/portage-"+self.settings["snapshot"]+".tar.bz2"
		self.settings["target_path"]=st+"/builds/"+self.settings["target_subpath"]+".tar.bz2"
		self.settings["source_path"]=st+"/builds/"+self.settings["source_subpath"]+".tar.bz2"
		self.settings["chroot_path"]=st+"/tmp/"+self.settings["target_subpath"]
		self.settings["pkgcache_path"]=st+"/packages/"+self.settings["target_subpath"]

	def mount_safety_check(self):
		mypath=self.settings["chroot_path"]
		#check and verify that none of our paths in mypath are mounted. We don't want to clean up with things still
		#mounted, and this allows us to check. returns 1 on ok, 0 on "something is still mounted" case.
		paths=["/usr/portage/packages","/usr/portage/distfiles", "/var/tmp/distfiles", "/proc", "/root/.ccache", "/dev"]
		if not os.path.exists(mypath):
			return 
		mypstat=os.stat(mypath)[stat.ST_DEV]
		for x in paths:
			if not os.path.exists(mypath+x):
				continue
			teststat=os.stat(mypath+x)[stat.ST_DEV]
			if teststat!=mypstat:
				#something is still mounted
				raise CatalystError, x+" is still mounted; aborting."
		return 1
		
	def dir_setup(self):
		self.mount_safety_check()
		retval=os.system("rm -rf "+self.settings["chroot_path"])
		if retval != 0:
			raise CatalystError,"Could not remove existing directory: "+self.settings["chroot_path"]
		os.makedirs(self.settings["chroot_path"])
		if not os.path.exists(self.settings["pkgcache_path"]):
			os.makedirs(self.settings["pkgcache_path"])
		
	def unpack_and_bind(self):
		retval=os.system("tar xjpf "+self.settings["source_path"]+" -C "+self.settings["chroot_path"])
		if retval!=0:
			raise CatalystError,"Error unpacking tarball"
		for x in [[self.settings["portdir"],"/usr/portage"],[self.settings["distdir"],"/usr/portage/distfiles"],
				["/proc","/proc"],["/dev","/dev"]]:
			retval=os.system("mount --bind "+x[0]+" "+x[1])
			if not retval:
				self.unbind()
				raise CatalystError,"Couldn't bind mount "+x[0]

	def unbind(self):
		pass	

	def setup(self):
		#setup will leave everything in unbound state if there is a failure
		self.dir_setup()
		self.unpack_and_bind()

	def run(self):
		self.setup()
		try:
			pass
		finally:
			#always unbind
			self.unbind()
	
class snapshot_target(generic_target):
	def __init__(self):
		self.settings["target_subpath"]="portage-"+self.settings["version_stamp"]
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=st+"/snapshots/"+self.settings["target_subpath"]+".tar.bz2"
		self.settings["tmp_path"]=st+"/tmp/"+self.settings["target_subpath"]

	def setup(self):
		#nothing to do here
		pass

	def run(self):
		print "Creating Portage tree snapshot "+snapversion+" from "+portdir+"..."
		mytmp=self.settings["tmp_path"]+"/"+self.settings["target_subpath"]
		if os.path.exists(mytmp):
			retval=os.system("rm -rf "+mytmp)
			if retval != 0:
				raise CatalystError, "Could not remove existing directory: "+mytmp
		os.makedirs(mytmp)
		retval=os.system("rsync -a --exclude /packages/ --exclude /distfiles/ --exclude CVS/ "+self.settings["portdir"]+"/ "+mytmp+"/portage/")
		if retval != 0:
			raise CatalystError,"Snapshot failure"
		print "Compressing Portage snapshot tarball..."
		retval=os.system("( cd "+mytmp+"; tar cjf "+self.settings["snapshot_path"]+"/portage-"+self.settings["snapversion"]+".tar.bz2 portage )")
		if retval != 0:
			raise CatalystError,"Snapshot creation failure"
		self.cleanup()

	def cleanup(self):
		mytmp=self.settings["tmp_path"]+"/"+self.settings["target_subpath"]
		print "Cleaning up temporary snapshot directory..."
		#Be a good citizen and clean up after ourselves
		retval=os.system("rm -rf "+mytmp)
		if retval != 0:
			raise CatalystError,"Snapshot cleanup failure"
			
class stage1_target(generic_stage_target):
	def __init__(self,spec):
		generic_stage_target.__init__(self,spec)
		pass

class stage2_target(generic_stage_target):
	def __init__(self,spec):
		generic_stage_target.__init__(self,spec)
		pass

class stage3_target(generic_stage_target):
	def __init__(self,spec):
		generic_stage_target.__init__(self,spec)
		pass

class grp_target(generic_stage_target):
	def __init__(self,spec):
		generic_target.__init__(self,spec)
		pass

class livecd_target(generic_stage_target):
	def __init__(self):
		generic_target.__init__(self)
		pass

def register(foo):
	foo.update({"stage1":stage1_target,"stage2":stage2_target,"stage3":stage3_target,
	"grp":grp_target,"livecd":livecd_target,"snapshot":snapshot_target})
	return foo
	
