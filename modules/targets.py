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

	def mount_safety_check(self,mypath):
		#check and verify that none of our paths in mypath are mounted. We don't want to clean up with things still
		#mounted, and this allows us to check. returns 1 on ok, 0 on "something is still mounted" case.
		paths=["/usr/portage/packages","/usr/portage/distfiles", "/var/tmp/distfiles", "/proc", "/root/.ccache", "/dev"]
		if not os.path.exists(mypath):
			return 1 
		mypstat=os.stat(mypath)[stat.ST_DEV]
		for x in paths:
			if not os.path.exists(mypath+x):
				continue
			teststat=os.stat(mypath+x)[stat.ST_DEV]
			if teststat!=mypstat:
				#something is still mounted
				return 0
		return 1
		
	def dir_setup(self):
		if not self.mount_safety_check(self.settings["chroot_path"]):
			print "Error: bind mounts still mounted in "+self.settings["chroot_path"]+"."
			print "Will not clean up directory until this is fixed."
			return 0
		retval=os.system("rm -rf "+self.settings["chroot_path"])
		if retval != 0:
			print "Could not remove existing directory: "+self.settings["chroot_path"]
			return 0
		os.makedirs(self.settings["chroot_path"])
		if not os.path.exists(self.settings["pkgcache_path"]):
			os.makedirs(self.settings["pkgcache_path"])
		return 1
		
	def unpack_and_bind(self):
		retval=os.system("tar xjpf "+self.settings["source_path"]+" -C "+self.settings["chroot_path"])
		if retval!=0:
			die("Unpack error")
		for x in [[self.settings["portdir"],"/usr/portage"],[self.settings["distdir"],"/usr/portage/distfiles"],
				["/proc","/proc"],["/dev","/dev"]]:
			retval=os.system("mount --bind "+x[0]+" "+x[1])
			if not retval:
				die("Bind mount error")
	
	def run(self):
		print "I'm running!"
		retval=self.dir_setup()
		if not retval:
			return 0
		retval=self.unpack_and_bind()
		if not retval:
			return 0

class snapshot_target(generic_target):
	def __init__(self):
		self.settings["target_subpath"]="portage-"+self.settings["version_stamp"]
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=st+"/snapshots/"+self.settings["target_subpath"]+".tar.bz2"
		self.settings["tmp_path"]=st+"/tmp/"+self.settings["target_subpath"]

	def do_snapshot(portdir,snap_temp_dir,snapdir,snapversion):
		print "Creating Portage tree snapshot "+snapversion+" from "+portdir+"..."
		mytmp=snap_temp_dir+"/snap-"+snapversion
		if os.path.exists(mytmp):
			retval=os.system("rm -rf "+mytmp)
			if retval != 0:
				die("Could not remove existing directory: "+mytmp)
		os.makedirs(mytmp)
		retval=os.system("rsync -a --exclude /packages/ --exclude /distfiles/ --exclude CVS/ "+portdir+"/ "+mytmp+"/portage/")
		if retval != 0:
			die("snapshot failure.")
		print "Compressing Portage snapshot tarball..."
		retval=os.system("( cd "+mytmp+"; tar cjf "+snapdir+"/portage-"+snapversion+".tar.bz2 portage )")
		if retval != 0:
			die("snapshot tarball creation failure.")
		print "Cleaning up temporary snapshot directory..."
		#Be a good citizen and clean up after ourselves
		retval=os.system("rm -rf "+mytmp)
		if retval != 0:
			die("Unable to clean up directory: "+mytmp)
	def run(self):
		self.do_snapshot(self.settings["portdir"],self.settings["tmp_path"],self.settings["snapshot_path"],self.settings["snapversion"])

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
	
