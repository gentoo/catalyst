# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/generic_stage_target.py,v 1.8 2004/08/02 23:23:34 zhen Exp $

"""
This class does all of the chroot setup, copying of files, etc. It is
the driver class for pretty much everything that Catalyst does.
"""

import os,string,imp,types,shutil
from catalyst_support import *
from generic_target import *
from stat import *

class generic_stage_target(generic_target):

	def __init__(self,myspec,addlargs):
		
		self.required_values.extend(["version_stamp","target","subarch","rel_type",\
			"profile","snapshot","source_subpath"])
		
		self.valid_values.extend(["version_stamp","target","subarch","rel_type","profile",\
			"snapshot","source_subpath","portage_confdir"])
		generic_target.__init__(self,addlargs,myspec)
		
		# map the mainarch we are running under to the mainarches we support for
		# building stages and LiveCDs. (for example, on amd64, we can build stages for
		# x86 or amd64.
		targetmap={ 	"x86" : ["x86"],
				"amd64" : ["x86","amd64"],
				"sparc64" : ["sparc","sparc64"],
				"ia64" : ["ia64"],
				"alpha" : ["alpha"],
				"sparc" : ["sparc"],
				"s390"	: ["s390"],
				"ppc" : ["ppc"],
				"ppc64" : ["ppc","ppc64"],
				"hppa" : ["hppa"],
				"mips" : ["mips"]
		}
		
		machinemap={ 	"i386" : "x86",
				"i486" : "x86",
				"i586" : "x86",
				"i686" : "x86",
				"x86_64" : "amd64",
				"sparc64" : "sparc64",
				"ia64" : "ia64",
				"alpha" : "alpha",
				"sparc" : "sparc",
				"s390"	: "s390",
				"ppc" : "ppc",
				"ppc64" : "ppc64",
				"parisc" : "hppa",
				"parisc64" : "hppa",
				"mips" : "mips",
				"mips64" : "mips"
		}
	
		mymachine=os.uname()[4]
		if not machinemap.has_key(mymachine):
			raise CatalystError, "Unknown machine type "+mymachine
			
		self.settings["hostarch"]=machinemap[mymachine]
		self.archmap={}
		self.subarchmap={}
		
		for x in targetmap[self.settings["hostarch"]]:
			try:
				fh=open(self.settings["sharedir"]+"/arch/"+x+".py")
				# this next line loads the plugin as a module and assigns it to archmap[x]
				self.archmap[x]=imp.load_module(x,fh,"arch/"+x+".py",(".py","r",imp.PY_SOURCE))
				# this next line registers all the subarches supported in the plugin
				self.archmap[x].register(self.subarchmap)
				fh.close()	
			
			except IOError:
				msg("Can't find "+x+".py plugin in "+self.settings["sharedir"]+"/arch/")
		
		# call arch constructor, pass our settings
		self.arch=self.subarchmap[self.settings["subarch"]](self.settings)
		
		# self.settings["mainarch"] should now be set by our arch constructor, so we print
		# a nice informational message:
		if self.settings["mainarch"]==self.settings["hostarch"]:
			print "Building natively for",self.settings["hostarch"]
		
		else:
			print "Building on",self.settings["hostarch"],"for alternate machine type",\
				self.settings["mainarch"]
		
		# grab build settings from the environment
		for envvar in "CHOST", "CFLAGS", "CXXFLAGS":
			if os.environ.has_key(envvar):
			self.settings[envvar] = os.environ[envvar]
		
		# define all of our core variables
		self.settings["target_profile"]=self.settings["profile"]
		self.settings["target_subpath"]=self.settings["rel_type"]+"/"+self.settings["target"]+\
			"-"+self.settings["subarch"]+"-"+self.settings["version_stamp"]
			
		st=self.settings["storedir"]
		self.settings["snapshot_path"]=st+"/snapshots/portage-"+self.settings["snapshot"]+".tar.bz2"
		if self.settings["target"] in ["grp","tinderbox"]:
			# grp creates a directory of packages and sources rather than a compressed tarball
			self.settings["target_path"]=st+"/builds/"+self.settings["target_subpath"]
			self.settings["source_path"]=st+"/builds/"+self.settings["source_subpath"]+".tar.bz2"
		
		elif self.settings["target"] == "livecd-stage2":
			self.settings["source_path"]=st+"/tmp/"+self.settings["source_subpath"]
			self.settings["cdroot_path"]=st+"/builds/"+self.settings["target_subpath"]
		
		else:
			self.settings["target_path"]=st+"/builds/"+self.settings["target_subpath"]+".tar.bz2"
			self.settings["source_path"]=st+"/builds/"+self.settings["source_subpath"]+".tar.bz2"
		
		self.settings["chroot_path"]=st+"/tmp/"+self.settings["target_subpath"]
		
		# this next line checks to make sure that the specified variables exist on disk.
		file_locate(self.settings,["source_path","snapshot_path","distdir"],expand=0)
		
		# if we are using portage_confdir, check that as well
		if self.settings.has_key("portage_confdir"):
			file_locate(self.settings,["portage_confdir"],expand=0)
		
		# setup our mount points
		self.mounts=[ "/proc","/dev","/dev/pts","/usr/portage/distfiles" ]
		self.mountmap={"/proc":"/proc", "/dev":"/dev", "/dev/pts":"/dev/pts",\
			"/usr/portage/distfiles":self.settings["distdir"]}
		
		if self.settings["target"]=="grp":
			self.mounts.append("/tmp/grp")
			self.mountmap["/tmp/grp"]=self.settings["target_path"]

		# configure any user specified options (either in catalyst.conf or on the cmdline)
		if self.settings.has_key("PKGCACHE"):
			self.settings["pkgcache_path"]=st+"/packages/"+self.settings["target_subpath"]
			self.mounts.append("/usr/portage/packages")
			self.mountmap["/usr/portage/packages"]=self.settings["pkgcache_path"]

		if self.settings.has_key("CCACHE"):
			if os.environ.has_key("CCACHE_DIR"):
				ccdir=os.environ["CCACHE_DIR"]
				del os.environ["CCACHE_DIR"]
			else:
				ccdir="/root/.ccache"
			if not os.path.isdir(ccdir):
					raise CatalystError,\
						"Compiler cache support can't be enabled (can't find "+ccdir+")"
			self.mounts.append("/var/tmp/ccache")
			self.mountmap["/var/tmp/ccache"]=ccdir
			# for the chroot:
			os.environ["CCACHE_DIR"]="/var/tmp/ccache"	
			
	def mount_safety_check(self):
		mypath=self.settings["chroot_path"]
		
		"""
		check and verify that none of our paths in mypath are mounted. We don't want to clean
		up with things still mounted, and this allows us to check. 
		returns 1 on ok, 0 on "something is still mounted" case.
		"""
		if not os.path.exists(mypath):
			return
			
		for x in self.mounts:
			if not os.path.exists(mypath+x):
				continue
			
			if ismount(mypath+x):
				#something is still mounted
				try:
					print x+" is still mounted; performing auto-bind-umount..."
					# try to umount stuff ourselves
					self.unbind()
					if ismount(mypath+x):
						raise CatalystError, "Auto-unbind failed for "+x
					
					else:
						print "Auto-unbind successful, continuing..."
				
				except CatalystError:
					raise CatalystError, "Unable to auto-unbind "+x
		
	def dir_setup(self):
		print "Setting up directories..."
		self.mount_safety_check()
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["chroot_path"]+"/tmp/.clst_dir_setup"):
			print "Resume point detected, skipping directory setup..."
		
		else:
			cmd("rm -rf "+self.settings["chroot_path"],\
				"Could not remove existing directory: "+self.settings["chroot_path"])
			
			if not os.path.exists(self.settings["chroot_path"]+"/tmp"):
				os.makedirs(self.settings["chroot_path"]+"/tmp")
				touch(self.settings["chroot_path"]+"/tmp/.clst_dir_setup")
			
		if not os.path.exists(self.settings["chroot_path"]):
			os.makedirs(self.settings["chroot_path"])
		
		if self.settings.has_key("PKGCACHE"):	
			if not os.path.exists(self.settings["pkgcache_path"]):
				os.makedirs(self.settings["pkgcache_path"])
	
		
	def unpack_and_bind(self):
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["chroot_path"]+"/tmp/.clst_unpack_and_bind"):
			print "Resume point detected, skipping unpack and bind operation..."
		
		else:
			print "Unpacking stage tarball..."
			cmd("tar xjpf "+self.settings["source_path"]+" -C "+self.settings["chroot_path"],\
				"Error unpacking tarball")
				
			if os.path.exists(self.settings["chroot_path"]+"/usr/portage"):
				print "Cleaning up existing portage tree snapshot..."
				cmd("rm -rf "+self.settings["chroot_path"]+"/usr/portage",\
					"Error removing existing snapshot directory.")
			
			print "Unpacking portage tree snapshot..."
			cmd("tar xjpf "+self.settings["snapshot_path"]+" -C "+\
				self.settings["chroot_path"]+"/usr","Error unpacking snapshot")
			
			touch(self.settings["chroot_path"]+"/tmp/.clst_unpack_and_bind")

		# for safety's sake, we really don't want to resume these either		
		print "Configuring profile link..."
		cmd("rm -f "+self.settings["chroot_path"]+"/etc/make.profile",\
			"Error zapping profile link")
		cmd("ln -sf ../usr/portage/profiles/"+self.settings["target_profile"]+\
			" "+self.settings["chroot_path"]+"/etc/make.profile","Error creating profile link")
		
		if self.settings.has_key("portage_confdir"):
			print "Configuring /etc/portage..."
			cmd("rm -rf "+self.settings["chroot_path"]+"/etc/portage","Error zapping /etc/portage")
			cmd("cp -R "+self.settings["portage_confdir"]+" "+self.settings["chroot_path"]+\
				"/etc/portage","Error copying /etc/portage")

		# do all of our bind mounts here (does not get autoresumed!)
		for x in self.mounts: 
			if not os.path.exists(self.settings["chroot_path"]+x):
				os.makedirs(self.settings["chroot_path"]+x)
			
			if not os.path.exists(self.mountmap[x]):
				os.makedirs(self.mountmap[x])
			
			src=self.mountmap[x]
			retval=os.system("mount --bind "+src+" "+self.settings["chroot_path"]+x)
			if retval!=0:
				self.unbind()
				raise CatalystError,"Couldn't bind mount "+src
		
	def unbind(self):
		ouch=0
		mypath=self.settings["chroot_path"]
		myrevmounts=self.mounts[:]
		myrevmounts.reverse()
		# unmount in reverse order for nested bind-mounts
		for x in myrevmounts:
			if not os.path.exists(mypath+x):
				continue
			
			if not ismount(mypath+x):
				# it's not mounted, continue
				continue
			
			retval=os.system("umount "+mypath+x)
			
			if retval!=0:
				ouch=1
				warn("Couldn't umount bind mount: "+mypath+x)
				# keep trying to umount the others, to minimize damage if developer makes a mistake
		
		if ouch:
			"""
			if any bind mounts really failed, then we need to raise
			this to potentially prevent an upcoming bash stage cleanup script
			from wiping our bind mounts.
			"""
			raise CatalystError,"Couldn't umount one or more bind-mounts; aborting for safety."

	def chroot_setup(self):
		print "Setting up chroot..."
		cmd("cp /etc/resolv.conf "+self.settings["chroot_path"]+"/etc",\
			"Could not copy resolv.conf into place.")
		
		# copy over the envscript, if applicable
		if self.settings.has_key("ENVSCRIPT"):
			if not os.path.exists(self.settings["ENVSCRIPT"]):
				raise CatalystError, "Can't find envscript "+self.settings["ENVSCRIPT"]
			cmd("cp "+self.settings["ENVSCRIPT"]+" "+self.settings["chroot_path"]+"/tmp/envscript",\
				"Could not copy envscript into place.")
		
		# modify and write out make.conf (for the chroot)
		cmd("rm -f "+self.settings["chroot_path"]+"/etc/make.conf")
		myf=open(self.settings["chroot_path"]+"/etc/make.conf","w")
		myf.write("# These settings were set by the catalyst build script that automatically built this stage\n")
		myf.write("# Please consult /etc/make.conf.example for a more detailed example\n")
		myf.write('CFLAGS="'+self.settings["CFLAGS"]+'"\n')
		myf.write('CHOST="'+self.settings["CHOST"]+'"\n')
		
		# figure out what our USE vars are for building
		myusevars=[]
		if self.settings.has_key("HOSTUSE"):
			myusevars.extend(self.settings["HOSTUSE"])
			
		if self.settings["target"]=="grp":
			myusevars.append("bindist")
			myusevars.extend(self.settings["grp/use"])
			myf.write('USE="'+string.join(myusevars)+'"\n')
			
		elif self.settings["target"]=="tinderbox":
			myusevars.extend(self.settings["tinderbox/use"])
			myf.write('USE="'+string.join(myusevars)+'"\n')
			
		elif self.settings["target"]=="livecd-stage1":
			myusevars.extend(self.settings["livecd/use"])
			myf.write('USE="'+string.join(myusevars)+'"\n')
			
		elif self.settings["target"]=="embedded":
			myusevars.extend(self.settings["embedded/use"])
			myf.write('USE="'+string.join(myusevars)+'"\n')
			
		if self.settings.has_key("CXXFLAGS"):
			myf.write('CXXFLAGS="'+self.settings["CXXFLAGS"]+'"\n')
		
		else:
			myf.write('CXXFLAGS="${CFLAGS}"\n')
		myf.close()

		#create entry in /etc/passwd for distcc user
		if self.settings.has_key("DISTCC"): 
			myf=open(self.settings["chroot_path"]+"/etc/passwd","a")
			myf.write("distcc:x:7980:2:distccd:/dev/null:/bin/false\n")
			myf.close()
		
	def clean(self):
		destpath=self.settings["chroot_path"]
		
		cleanables=["/etc/resolv.conf","/var/tmp/*","/tmp/*","/root/*","/usr/portage"]
			
		if self.settings["target"]=="stage1":
			destpath+="/tmp/stage1root"
			# this next stuff can eventually be integrated into the python
			# and glibc ebuilds themselves (USE="build"):
			cleanables.extend(["/usr/share/gettext","/usr/lib/python2.2/test",\
				"/usr/lib/python2.2/encodings","/usr/lib/python2.2/email",\
				"/usr/lib/python2.2/lib-tk","/usr/share/zoneinfo"])
				
		for x in cleanables: 
			print "Cleaning chroot: "+x+"..."
			cmd("rm -rf "+destpath+x,"Couldn't clean "+x)
		
		cmd("/bin/bash "+self.settings["sharedir"]+"/targets/"+self.settings["target"]+\
			"/"+self.settings["target"]+".sh clean","clean script failed.")
	
	def preclean(self):
		# cleanup after distcc
		if self.settings.has_key("DISTCC"):
			myf=open(self.settings["chroot_path"]+"/etc/passwd","r")
			outf=open(self.settings["chroot_path"]+"/tmp/out.txt","w")
			for line in myf:
				if not line.startswith("distcc:"):
					outf.write(line)
			myf.close()
			outf.close()
			os.rename(self.settings["chroot_path"]+"/tmp/out.txt",self.settings["chroot_path"]+"/etc/passwd")
			cmd("/usr/bin/pkill -U 7980","could not kill distcc process(es)")
			
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+"/targets/"+self.settings["target"]+\
				"/"+self.settings["target"]+".sh preclean","preclean script failed.")
		
		except:
			self.unbind()
			raise

	def capture(self):
		"""capture target in a tarball"""
		mypath=self.settings["target_path"].split("/")
		# remove filename from path
		mypath=string.join(mypath[:-1],"/")
		
		# now make sure path exists
		if not os.path.exists(mypath):
			os.makedirs(mypath)

		# clean resume points since they are no longer needed
		if self.settings.has_key("AUTORESUME"):
			cmd("rm -f "+self.settings["chroot_path"]+"/tmp/.clst*",\
				"Couldn't remove resume points")
			
		print "Creating stage tarball..."
		
		if self.settings["target"]=="stage1":
			cmd("tar cjf "+self.settings["target_path"]+" -C "+self.settings["chroot_path"]+\
				"/tmp/stage1root .","Couldn't create stage tarball")
		
		elif self.settings["target"]=="embedded":
			cmd("tar cjf "+self.settings["target_path"]+" -C "+self.settings["chroot_path"]+\
				"/tmp/mergeroot .","Couldn't create stage tarball")
		
		else:
			cmd("tar cjf "+self.settings["target_path"]+" -C "+self.settings["chroot_path"]+\
				" .","Couldn't create stage tarball")

	def run_local(self):
		try:
			cmd("/bin/bash "+self.settings["sharedir"]+"/targets/"+self.settings["target"]+\
				"/"+self.settings["target"]+".sh run","build script failed")

		except CatalystError:
			self.unbind()
			raise CatalystError,"Stage build aborting due to error."

	def run(self):
		self.dir_setup()
		self.unpack_and_bind()
		try:
			self.chroot_setup()
		
		except:
			self.unbind()
			raise
		
		# modify the current environment. This is an ugly hack that should be fixed. We need this
		# to use the os.system() call since we can't specify our own environ:
		for x in self.settings.keys():
			# "/" is replaced with "_", "-" is also replaced with "_"
			varname="clst_"+string.replace(x,"/","_")
			varname=string.replace(varname,"-","_")
			if type(self.settings[x])==types.StringType:
				# prefix to prevent namespace clashes:
				os.environ[varname]=self.settings[x]
			elif type(self.settings[x])==types.ListType:
				os.environ[varname]=string.join(self.settings[x])
			
		self.run_local()
		if self.settings["target"] in ["stage1","stage2","stage3","livecd-stage2"]:
			self.preclean()
		
		if self.settings["target"] in ["livecd-stage2"]:
			self.unmerge()
		self.unbind()
		
		if self.settings["target"] in ["stage1","stage2","stage3","livecd-stage2"]:
			# clean is for removing things after bind-mounts are 
			# unmounted (general file removal and cleanup)
			self.clean()
		
		if self.settings["target"] in ["stage1","stage2","stage3","embedded"]:
			self.capture()
		
		if self.settings["target"] in ["livecd-stage2"]:
			self.cdroot_setup()
