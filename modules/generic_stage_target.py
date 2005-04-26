# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/generic_stage_target.py,v 1.39 2005/04/26 14:58:04 rocket Exp $

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
			"snapshot","source_subpath","portage_confdir","cflags","cxxflags","chost","hostuse"])
		generic_target.__init__(self,addlargs,myspec)
		
		# map the mainarch we are running under to the mainarches we support for
		# building stages and LiveCDs. (for example, on amd64, we can build stages for
		# x86 or amd64.
		targetmap={ 	
				"x86" : ["x86"],
				"amd64" : ["x86","amd64"],
				"sparc64" : ["sparc","sparc64"],
				"ia64" : ["ia64"],
				"alpha" : ["alpha"],
				"sparc" : ["sparc"],
				"s390" : ["s390"],
				"ppc" : ["ppc"],
				"ppc64" : ["ppc","ppc64"],
				"hppa" : ["hppa"],
				"mips" : ["mips"],
				"arm" : ["arm"]
		}
		
		machinemap={ 	
				"i386" : "x86",
				"i486" : "x86",
				"i586" : "x86",
				"i686" : "x86",
				"x86_64" : "amd64",
				"sparc64" : "sparc64",
				"ia64" : "ia64",
				"alpha" : "alpha",
				"sparc" : "sparc",
				"s390" : "s390",
				"ppc" : "ppc",
				"ppc64" : "ppc64",
				"parisc" : "hppa",
				"parisc64" : "hppa",
				"mips" : "mips",
				"mips64" : "mips",
				"arm" : "arm",
				"armv4l" : "arm",
				"armeb" : "arm",
				"armv5b" : "arm"
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
		
		print "Using target:",self.settings["target"]
		# self.settings["mainarch"] should now be set by our arch constructor, so we print
		# a nice informational message:
		if self.settings["mainarch"]==self.settings["hostarch"]:
			print "Building natively for",self.settings["hostarch"]
		
		else:
			print "Building on",self.settings["hostarch"],"for alternate machine type",\
				self.settings["mainarch"]
		# This should be first to be set as other set_ options depend on this
		self.set_spec_prefix()
		
		# define all of our core variables
		self.set_target_profile()
		self.set_target_subpath()
	
		# set paths
		self.set_autoresume_path()
		self.set_snapshot_path()
		self.set_source_path()
		self.set_chroot_path()
		self.set_root_path()
		self.set_dest_path()
		self.set_stage_path()
		self.set_target_path()
		
		self.set_controller_file()
		self.set_action_sequence()
		self.set_use()
		self.set_cleanables()
		self.set_iso_volume_id()
		self.set_build_kernel_vars(addlargs)	
		self.set_fsscript()
		self.set_install_mask()
		self.set_rcadd()
		self.set_rcdel()
		self.set_cdtar()
		self.set_fstype()
		self.set_fsops()
		self.set_iso()
		self.set_packages()
		self.set_target_file()
		self.set_target_iso_path()
		

		# this next line checks to make sure that the specified variables exist on disk.
		file_locate(self.settings,["source_path","snapshot_path","distdir"],expand=0)
		
		# if we are using portage_confdir, check that as well
		if self.settings.has_key("portage_confdir"):
			file_locate(self.settings,["portage_confdir"],expand=0)
		
		# setup our mount points
		self.mounts=[ "/proc","/dev","/dev/pts","/usr/portage/distfiles" ]
		self.mountmap={"/proc":"/proc", "/dev":"/dev", "/dev/pts":"/dev/pts",\
			"/usr/portage/distfiles":self.settings["distdir"]}
		self.set_mounts()

		# configure any user specified options (either in catalyst.conf or on the cmdline)
		if self.settings.has_key("PKGCACHE"):
			self.settings["pkgcache_path"]=self.settings["storedir"]+"/packages/"+self.settings["target_subpath"]
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
		
	def override_chost(self):
		if os.environ.has_key("CHOST"):
		    self.settings["CHOST"] = os.environ["CHOST"]
		if self.settings.has_key("chost"):
		    self.settings["CHOST"]=list_to_string(self.settings["chost"])
		if self.makeconf.has_key("CHOST"):
		    print "Using CHOST setting from seed stage"
		    self.settings["CHOST"]=self.makeconf["CHOST"]
	
	def override_cflags(self):
		if os.environ.has_key("CFLAGS"):
		    self.settings["CFLAGS"] = os.environ["CFLAGS"]
		if self.settings.has_key("cflags"):
		    self.settings["CFLAGS"]=list_to_string(self.settings["cflags"])
		if self.makeconf.has_key("CFLAGS"):
		    print "Using CFLAGS setting from seed stage"
		    self.settings["CFLAGS"]=self.makeconf["CFLAGS"]

	def override_cxxflags(self):	
		if os.environ.has_key("CXXFLAGS"):
		    self.settings["CXXFLAGS"] = os.environ["CXXFLAGS"]
		if self.settings.has_key("cxxflags"):
		    self.settings["CXXFLAGS"]=list_to_string(self.settings["cxxflags"])
		if self.makeconf.has_key("CXXFLAGS"):
		    print "Using CXXFLAGS setting from seed stage"
		    self.settings["CXXFLAGS"]=self.makeconf["CXXFLAGS"]
	
	def set_install_mask(self):
		if self.settings.has_key("install_mask"):
			if type(self.settings["install_mask"]) != types.StringType:
				self.settings["install_mask"]=string.join(self.settings["install_mask"])
	
	def set_spec_prefix(self):
		self.settings["spec_prefix"]=self.settings["target"]

	def set_target_profile(self):
		self.settings["target_profile"]=self.settings["profile"]
	
	def set_target_subpath(self):
		self.settings["target_subpath"]=self.settings["rel_type"]+"/"+self.settings["target"]+\
			"-"+self.settings["subarch"]+"-"+self.settings["version_stamp"]

	def set_target_path(self):
		self.settings["target_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["autoresume_path"]+"setup_target_path"):
			print "Resume point detected, skipping target path setup operation..."
		else:
			# first clean up any existing target stuff
			if os.path.exists(self.settings["target_path"]):
				cmd("rm -rf "+self.settings["target_path"],
					"Could not remove existing directory: "+self.settings["target_path"])
		    	touch(self.settings["autoresume_path"]+"setup_target_path")
		
		if not os.path.exists(self.settings["target_path"]):
			os.makedirs(self.settings["target_path"])
	
	def set_target_file(self):
		if not os.path.exists(self.settings["target_path"]+"/tarball/"):
			os.makedirs(self.settings["target_path"]+"/tarball/")
		self.settings["target_file"]=self.settings["target_path"]+"/tarball/"+self.settings["target"]+"-"+self.settings["subarch"]+"-"+self.settings["version_stamp"]+".tar.bz2"
	
	def set_target_iso_path(self):
		if self.settings.has_key("iso"):
			print "setting up iso path"
			if not os.path.exists(self.settings["target_path"]+"/iso/"):
				os.makedirs(self.settings["target_path"]+"/iso/")
			self.settings["target_iso_path"]=self.settings["target_path"]+"/iso/"

	def set_fsscript(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/fsscript"):
			self.settings["fsscript"]=self.settings[self.settings["spec_prefix"]+"/fsscript"]
			del self.settings[self.settings["spec_prefix"]+"/fsscript"]
	
	def set_rcadd(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/rcadd"):
			self.settings["rcadd"]=self.settings[self.settings["spec_prefix"]+"/rcadd"]
			del self.settings[self.settings["spec_prefix"]+"/rcadd"]
	
	def set_rcdel(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/rcdel"):
			self.settings["rcdel"]=self.settings[self.settings["spec_prefix"]+"/rcdel"]
			del self.settings[self.settings["spec_prefix"]+"/rcdel"]

	def set_cdtar(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/cdtar"):
			self.settings["cdtar"]=self.settings[self.settings["spec_prefix"]+"/cdtar"]
			del self.settings[self.settings["spec_prefix"]+"/cdtar"]
	
	def set_iso(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/iso"):
			self.settings["iso"]=self.settings[self.settings["spec_prefix"]+"/iso"]
			del self.settings[self.settings["spec_prefix"]+"/iso"]

	def set_fstype(self):	
		if self.settings.has_key(self.settings["spec_prefix"]+"/cdfstype"):
			print "\n\n\nWarning!!!"+self.settings["spec_prefix"]+"/cdfstype" + "is deprecated and may be removed."
			print "\tUse "+self.settings["spec_prefix"]+"/fstype" + "instead.\n\n\n"
			self.settings["fstype"]=self.settings[self.settings["spec_prefix"]+"/cdfstype"]
			del self.settings[self.settings["spec_prefix"]+"/cdfstype"]
		
		if self.settings.has_key(self.settings["spec_prefix"]+"/fstype"):
			self.settings["fstype"]=self.settings[self.settings["spec_prefix"]+"/fstype"]
			del self.settings[self.settings["spec_prefix"]+"/fstype"]

		if not self.settings.has_key("fstype"):
			self.settings["fstype"]="normal"

	def set_fsops(self):
		if self.settings.has_key("fstype"):
			self.valid_values.append("fsops")
			if self.settings.has_key(self.settings["spec_prefix"]+"/fs-ops"):
				print "\n\n\nWarning!!!"+self.settings["spec_prefix"]+"/fs-ops" + "is deprecated and may be removed."
				print "\tUse "+self.settings["spec_prefix"]+"/fsops" + "instead.\n\n\n"
				self.settings["fsops"]=self.settings[self.settings["spec_prefix"]+"/fs-ops"]
				del self.settings[self.settings["spec_prefix"]+"/fs-ops"]
			
			if self.settings.has_key(self.settings["spec_prefix"]+"/fsops"):
				self.settings["fsops"]=self.settings[self.settings["spec_prefix"]+"/fsops"]
				del self.settings[self.settings["spec_prefix"]+"/fsops"]
	
	def set_source_path(self):
		self.settings["source_path"]=self.settings["storedir"]+"/builds/"+self.settings["source_subpath"]+".tar.bz2"
		if os.path.isfile(self.settings["source_path"]):
			if os.path.exists(self.settings["source_path"]):
				 self.settings["source_path_md5sum"]=calc_md5(self.settings["source_path"])
	
	def set_dest_path(self):
		self.settings["destpath"]=self.settings["chroot_path"]

	def set_cleanables(self):
		self.settings["cleanables"]=["/etc/resolv.conf","/var/tmp/*","/tmp/*","/root/*",\
						"/usr/portage"]

	def set_snapshot_path(self):
		self.settings["snapshot_path"]=self.settings["storedir"]+"/snapshots/portage-"+self.settings["snapshot"]+".tar.bz2"
		if os.path.exists(self.settings["snapshot_path"]):
		    self.settings["snapshot_path_md5sum"]=calc_md5(self.settings["snapshot_path"])
	
	def set_chroot_path(self):
		self.settings["chroot_path"]=self.settings["storedir"]+"/tmp/"+self.settings["target_subpath"]
	
	def set_autoresume_path(self):
		self.settings["autoresume_path"]=self.settings["storedir"]+"/tmp/"+self.settings["rel_type"]+"/"+\
			".autoresume-"+self.settings["target"]+"-"+self.settings["subarch"]+"-"+self.settings["version_stamp"]+"/"
		print "The autoresume path is " + self.settings["autoresume_path"]
		if not os.path.exists(self.settings["autoresume_path"]):
		    os.makedirs(self.settings["autoresume_path"],0755)
	
	def set_controller_file(self):
		self.settings["controller_file"]=self.settings["sharedir"]+"/targets/"+self.settings["target"]+"/"+self.settings["target"]+"-controller.sh"
	def set_iso_volume_id(self):
                if self.settings.has_key(self.settings["spec_prefix"]+"/volid"):
		    self.settings["iso_volume_id"] = string.join(self.settings[self.settings["spec_prefix"]+"/volid"])
		    if len(self.settings["iso_volume_id"])>32:
			raise CatalystError,"ISO VOLUME ID: volid must not exceed 32 characters."
		else:
		    self.settings["iso_volume_id"] = "catalyst " + self.settings["snapshot"] 
															
	def set_action_sequence(self):
		#Default action sequence for run method
		self.settings["action_sequence"]=["dir_setup","unpack","unpack_snapshot",\
				"config_profile_link","setup_confdir","bind","chroot_setup",\
				"setup_environment","run_local","preclean","unbind","clean","capture","clear_autoresume"]
	
	def set_use(self):
		if self.settings.has_key("use"):
			self.settings["use"]=self.settings[self.settings["spec_prefix"]+"/use"]
			del self.settings[self.settings["spec_prefix"]+"/use"]

	def set_stage_path(self):
			self.settings["stage_path"]=self.settings["chroot_path"]
	
	def set_mounts(self):
		pass

	def set_packages(self):
		pass

	def set_root_path(self):
		# ROOT= variable for emerges
		self.settings["root_path"]="/"

	def set_build_kernel_vars(self,addlargs):
		
	    if addlargs.has_key("boot/kernel"):
		if type(addlargs["boot/kernel"]) == types.StringType:
			loopy=[addlargs["boot/kernel"]]
		else:
			loopy=addlargs["boot/kernel"]
			    
		for x in loopy:
			self.required_values.append("boot/kernel/"+x+"/sources")
			self.required_values.append("boot/kernel/"+x+"/config")
			self.valid_values.append("boot/kernel/"+x+"/extraversion")
			self.valid_values.append("boot/kernel/"+x+"/packages")
			self.valid_values.append("boot/kernel/"+x+"/use")
			self.valid_values.append("boot/kernel/"+x+"/gk_kernargs")
			self.valid_values.append("boot/kernel/"+x+"/gk_action")
			self.valid_values.append("boot/kernel/"+x+"/initramfs_overlay")
	    		if self.settings.has_key("boot/kernel/"+x+"/postconf"):
	   			print "boot/kernel/"+x+"/postconf is deprecated"
				print "\tInternally moving these ebuilds to boot/kernel/"+x+"/packages"
				print "\tPlease move them to boot/kernel/"+x+"/packages in your specfile"
				if type(self.settings["boot/kernel/"+x+"/postconf"]) == types.StringType:
					loop2=[self.settings["boot/kernel/"+x+"/postconf"]]
				else:
					loop2=self.settings["boot/kernel/"+x+"/postconf"]
				
				for y in loop2:
					self.settings["boot/kernel/"+x+"/packages"].append(y)

	    if self.settings.has_key(self.settings["spec_prefix"]+"/devmanager"):
		self.settings["devmanager"]=self.settings[self.settings["spec_prefix"]+"/devmanager"]
		del self.settings[self.settings["spec_prefix"]+"/devmanager"]
	    
	    if self.settings.has_key(self.settings["spec_prefix"]+"/splashtype"):
		self.settings["splashtype"]=self.settings[self.settings["spec_prefix"]+"/splashtype"]
		del self.settings[self.settings["spec_prefix"]+"/splashtype"]
	    
	    if self.settings.has_key(self.settings["spec_prefix"]+"/gk_mainargs"):
		self.settings["gk_mainargs"]=self.settings[self.settings["spec_prefix"]+"/gk_mainargs"]
		del self.settings[self.settings["spec_prefix"]+"/gk_mainargs"]
	
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
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["autoresume_path"]+"dir_setup"):
			print "Resume point detected, skipping dir_setup operation..."
		else:
		    print "Setting up directories..."
		    self.mount_safety_check()
		
		    self.clear_chroot()

		    if not os.path.exists(self.settings["chroot_path"]+"/tmp"):
			    os.makedirs(self.settings["chroot_path"]+"/tmp",1777)
			
		    if not os.path.exists(self.settings["chroot_path"]):
			    os.makedirs(self.settings["chroot_path"],0755)
		
		    if self.settings.has_key("PKGCACHE"):	
			    if not os.path.exists(self.settings["pkgcache_path"]):
				    os.makedirs(self.settings["pkgcache_path"],0755)
	
		    touch(self.settings["autoresume_path"]+"dir_setup")
		
	def unpack(self):
			if os.path.exists(self.settings["autoresume_path"]+"unpack"):
				clst_unpack_md5sum=read_from_clst(self.settings["autoresume_path"]+"unpack")
			
			if self.settings.has_key("AUTORESUME") \
				and os.path.exists(self.settings["autoresume_path"]+"unpack") \
				and self.settings["source_path_md5sum"] != clst_unpack_md5sum:
				    print "InValid Resume point detected, cleaning up  ..."
				    os.remove(self.settings["autoresume_path"]+"dir_setup")	
				    os.remove(self.settings["autoresume_path"]+"unpack")	
				    self.dir_setup()	
			if self.settings.has_key("AUTORESUME") \
				and os.path.exists(self.settings["autoresume_path"]+"unpack") \
				and self.settings["source_path_md5sum"] == clst_unpack_md5sum:
				    print "Valid Resume point detected, skipping unpack  ..."
			else:
		    		print "Unpacking ..."
				if not os.path.exists(self.settings["chroot_path"]):
				    os.makedirs(self.settings["chroot_path"])

		    		cmd("tar xjpf "+self.settings["source_path"]+" -C "+self.settings["chroot_path"],\
			    		"Error unpacking ")

				if self.settings.has_key("source_path_md5sum"):
				    myf=open(self.settings["autoresume_path"]+"unpack","w")
				    myf.write(self.settings["source_path_md5sum"])
				    myf.close()
	
	def unpack_snapshot(self):			
		    	if os.path.exists(self.settings["autoresume_path"]+"unpack_portage"):
			    clst_unpack_portage_md5sum=read_from_clst(self.settings["autoresume_path"]+"unpack_portage")
			
			if self.settings.has_key("AUTORESUME") \
		    	and os.path.exists(self.settings["chroot_path"]+"/usr/portage/") \
		    	and os.path.exists(self.settings["autoresume_path"]+"unpack_portage") \
			and self.settings["snapshot_path_md5sum"] == clst_unpack_portage_md5sum:
				print "Valid Resume point detected, skipping unpack of portage tree..."
			else:
		    		if os.path.exists(self.settings["chroot_path"]+"/usr/portage"):
			   		print "Cleaning up existing portage tree ..."
			   	cmd("rm -rf "+self.settings["chroot_path"]+"/usr/portage",\
				    	"Error removing existing snapshot directory.")
			
		    		print "Unpacking portage tree ..."
		    		cmd("tar xjpf "+self.settings["snapshot_path"]+" -C "+\
				    self.settings["chroot_path"]+"/usr","Error unpacking snapshot")
				
				print "Setting snapshot autoresume point"
				myf=open(self.settings["autoresume_path"]+"unpack_portage","w")
				myf.write(self.settings["snapshot_path_md5sum"])
				myf.close()

	def config_profile_link(self):
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["autoresume_path"]+"config_profile_link"):
			print "Resume point detected, skipping config_profile_link operation..."
		else:
			print "Configuring profile link..."
			cmd("rm -f "+self.settings["chroot_path"]+"/etc/make.profile",\
					"Error zapping profile link")
	    		cmd("ln -sf ../usr/portage/profiles/"+self.settings["target_profile"]+\
		    		" "+self.settings["chroot_path"]+"/etc/make.profile","Error creating profile link")
		    	touch(self.settings["autoresume_path"]+"config_profile_link")
				       
	def setup_confdir(self):	
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["autoresume_path"]+"setup_confdir"):
			print "Resume point detected, skipping setup_confdir operation..."
		else:
	    		if self.settings.has_key("portage_confdir"):
				print "Configuring /etc/portage..."
				cmd("rm -rf "+self.settings["chroot_path"]+"/etc/portage","Error zapping /etc/portage")
				cmd("cp -R "+self.settings["portage_confdir"]+"/ "+self.settings["chroot_path"]+\
					"/etc/portage","Error copying /etc/portage")
		    		touch(self.settings["autoresume_path"]+"setup_confdir")
	
	def portage_overlay(self):	
	    # copy over the portage overlays
	    # Always copy over the overlay incase it has changed
	    if self.settings.has_key("portage_overlay"):
	    	if type(self.settings["portage_overlay"])==types.StringType:
			self.settings[self.settings["portage_overlay"]]=[self.settings["portage_overlay"]]
		
		for x in self.settings["portage_overlay"]: 
			if os.path.exists(x):
				print "Copying overlay dir " +x
				cmd("mkdir -p "+self.settings["chroot_path"]+x)
				cmd("cp -R "+x+"/* "+self.settings["chroot_path"]+x)
	
	def root_overlay(self):
	    # copy over the root_overlay
	    # Always copy over the overlay incase it has changed
		if self.settings.has_key(self.settings["spec_prefix"]+"/root_overlay"):
		    print "Copying root overlay ..."
		    cmd("rsync -a "+self.settings[self.settings["spec_prefix"]+"/root_overlay"]+"/* "+\
			self.settings["chroot_path"], self.settings["spec_prefix"]+"/root_overlay copy failed.")

	def bind(self):
		for x in self.mounts: 
			if not os.path.exists(self.settings["chroot_path"]+x):
				os.makedirs(self.settings["chroot_path"]+x,0755)
			
			if not os.path.exists(self.mountmap[x]):
				os.makedirs(self.mountmap[x],0755)
			
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
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["autoresume_path"]+"chroot_setup"):
			print "Resume point detected, skipping chroot_setup operation..."
		else:
		    print "Setting up chroot..."
		    
		    self.makeconf=read_makeconf(self.settings["chroot_path"]+"/etc/make.conf")
		    
		    cmd("cp /etc/resolv.conf "+self.settings["chroot_path"]+"/etc",\
			    "Could not copy resolv.conf into place.")
		
		    # copy over the envscript, if applicable
		    if self.settings.has_key("ENVSCRIPT"):
			    if not os.path.exists(self.settings["ENVSCRIPT"]):
				   raise CatalystError, "Can't find envscript "+self.settings["ENVSCRIPT"]
			    cmd("cp "+self.settings["ENVSCRIPT"]+" "+self.settings["chroot_path"]+"/tmp/envscript",\
				    "Could not copy envscript into place.")

		    # copy over /etc/hosts from the host in case there are any specialties in there
		    if os.path.exists("/etc/hosts"):
			    cmd("mv "+self.settings["chroot_path"]+"/etc/hosts "+self.settings["chroot_path"]+\
				    "/etc/hosts.bck", "Could not backup /etc/hosts")
			    cmd("cp /etc/hosts "+self.settings["chroot_path"]+"/etc/hosts", "Could not copy /etc/hosts")
		    self.override_chost()	
		    self.override_cflags()
		    self.override_cxxflags()	
		    # modify and write out make.conf (for the chroot)
		    cmd("rm -f "+self.settings["chroot_path"]+"/etc/make.conf")
		    myf=open(self.settings["chroot_path"]+"/etc/make.conf","w")
		    myf.write("# These settings were set by the catalyst build script that automatically built this stage\n")
		    myf.write("# Please consult /etc/make.conf.example for a more detailed example\n")
		    myf.write('CFLAGS="'+self.settings["CFLAGS"]+'"\n')
		    myf.write('CHOST="'+self.settings["CHOST"]+'"\n')
		    
		    if self.settings.has_key("CXXFLAGS"):
			    myf.write('CXXFLAGS="'+self.settings["CXXFLAGS"]+'"\n')
		    else:
			    myf.write('CXXFLAGS="${CFLAGS}"\n')
		    
		    # figure out what our USE vars are for building
		    myusevars=[]
		    if self.settings.has_key("HOSTUSE"):
			    myusevars.extend(self.settings["HOSTUSE"])
		
		    if self.settings.has_key("use"):
			    myusevars.extend(self.settings["use"])
			    myf.write('USE="'+string.join(myusevars)+'"\n')

		    # setup the portage overlay	
		    if self.settings.has_key("portage_overlay"):
				if type(self.settings["portage_overlay"])==types.StringType:
					self.settings[self.settings["portage_overlay"]]=[self.settings["portage_overlay"]]
					
				myf.write('PORTDIR_OVERLAY="'+string.join(self.settings["portage_overlay"])+'"\n')
		    myf.close()
		    touch(self.settings["autoresume_path"]+"chroot_setup")
	
	def fsscript(self):
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["autoresume_path"]+"fsscript"):
			print "Resume point detected, skipping fsscript operation..."
		else:
		    if self.settings.has_key("fsscript"):
			if os.path.exists(self.settings["controller_file"]):
			    cmd("/bin/bash "+self.settings["controller_file"]+" fsscript","fsscript script failed.")
			touch(self.settings["autoresume_path"]+"fsscript")

	def rcupdate(self):
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["autoresume_path"]+"rcupdate"):
			print "Resume point detected, skipping rcupdate operation..."
		else:
		    if self.settings.has_key("rcadd") or self.settings.has_key("rcdel"):
			    if os.path.exists(self.settings["controller_file"]):
				  cmd("/bin/bash "+self.settings["controller_file"]+" rc-update","rc-update script failed.")
			    touch(self.settings["autoresume_path"]+"rcupdate")

	def clean(self):
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["autoresume_path"]+"clean"):
			print "Resume point detected, skipping clean operation..."
		else:
		    for x in self.settings["cleanables"]: 
			    print "Cleaning chroot: "+x+"... "
			    cmd("rm -rf "+self.settings["destpath"]+x,"Couldn't clean "+x)

		    # put /etc/hosts back into place
		    if os.path.exists("/etc/hosts.bck"):
			    cmd("mv -f "+self.settings["chroot_path"]+"/etc/hosts.bck "+self.settings["chroot_path"]+\
					  "/etc/hosts", "Could not replace /etc/hosts")
	
		    if os.path.exists(self.settings["controller_file"]):
			cmd("/bin/bash "+self.settings["controller_file"]+" clean","clean script failed.")
			touch(self.settings["autoresume_path"]+"clean")
	
	def empty(self):		
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"empty"):
		print "Resume point detected, skipping empty operation..."
	    else:
		if self.settings.has_key(self.settings["spec_prefix"]+"/empty"):
		    if type(self.settings[self.settings["spec_prefix"]+"/empty"])==types.StringType:
			self.settings[self.settings["spec_prefix"]+"/empty"]=[self.settings[self.settings["spec_prefix"]+"/empty"]]
		    for x in self.settings[self.settings["spec_prefix"]+"/empty"]:
			myemp=self.settings["destpath"]+x
			if not os.path.isdir(myemp):
			    print x,"not a directory or does not exist, skipping 'empty' operation."
			    continue
			print "Emptying directory",x
			# stat the dir, delete the dir, recreate the dir and set
			# the proper perms and ownership
			mystat=os.stat(myemp)
			shutil.rmtree(myemp)
			os.makedirs(myemp,0755)
			os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
			os.chmod(myemp,mystat[ST_MODE])
		    touch(self.settings["autoresume_path"]+"empty")
	
	def remove(self):
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"remove"):
		print "Resume point detected, skipping remove operation..."
	    else:
		if self.settings.has_key(self.settings["spec_prefix"]+"/rm"):
		    if type(self.settings[self.settings["spec_prefix"]+"/rm"])==types.StringType:
			self.settings[self.settings["spec_prefix"]+"/rm"]=[self.settings[self.settings["spec_prefix"]+"/rm"]]
		    for x in self.settings[self.settings["spec_prefix"]+"/rm"]:
			# we're going to shell out for all these cleaning operations,
			# so we get easy glob handling
			print "livecd: removing "+x
			os.system("rm -rf "+self.settings["chroot_path"]+x)
		try:
		    if os.path.exists(self.settings["controller_file"]):
			    cmd("/bin/bash "+self.settings["controller_file"]+" clean",\
				"Clean runscript failed.")
			    touch(self.settings["autoresume_path"]+"remove")
		except:
		    self.unbind()
		    raise

	def clear_autoresume(self):
		# clean resume points since they are no longer needed
		if self.settings.has_key("AUTORESUME"):
			print "Removing AutoResume Points: ..."
			cmd("rm -rf "+self.settings["autoresume_path"],\
				"Couldn't remove resume points")
	
	def preclean(self):
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"preclean"):
		print "Resume point detected, skipping preclean operation..."
	    else:
		try:
			if os.path.exists(self.settings["controller_file"]):
		    		cmd("/bin/bash "+self.settings["controller_file"]+" preclean","preclean script failed.")
				touch(self.settings["autoresume_path"]+"preclean")
		
		except:
			self.unbind()
			raise CatalystError, "Build failed, could not execute preclean"

	def capture(self):
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"capture"):
		print "Resume point detected, skipping capture operation..."
	    else:
		"""capture target in a tarball"""
		mypath=self.settings["target_path"].split("/")
		# remove filename from path
		mypath=string.join(mypath[:-1],"/")
		
		# now make sure path exists
		if not os.path.exists(mypath):
			os.makedirs(mypath)

		print "Creating stage tarball..."
		
		cmd("tar cjf "+self.settings["target_file"]+" -C "+self.settings["stage_path"]+\
			" .","Couldn't create stage tarball")
		touch(self.settings["autoresume_path"]+"capture")

	def run_local(self):
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"run_local"):
		print "Resume point detected, skipping run_local operation..."
	    else:
		try:
			if os.path.exists(self.settings["controller_file"]):
		    		cmd("/bin/bash "+self.settings["controller_file"]+" run","run script failed.")
				touch(self.settings["autoresume_path"]+"run_local")

		except CatalystError:
			self.unbind()
			raise CatalystError,"Stage build aborting due to error."
	
	def setup_environment(self):
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
	
	def run(self):
		for x in self.settings["action_sequence"]:
			print "Running action sequence: "+x
			try:
				apply(getattr(self,x))
			except:
				self.unbind()
				raise
			#if x == 'chroot_setup':
			#	try:
			#		self.chroot_setup()
			#	except:
			#		self.unbind()
			#		raise
			#else:	
			#	apply(getattr(self,x))

        def unmerge(self):
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"unmerge"):
		    print "Resume point detected, skipping unmerge operation..."
	    else:
		if self.settings.has_key(self.settings["spec_prefix"]+"/unmerge"):
		    print "has key unmerge"
		    if type(self.settings[self.settings["spec_prefix"]+"/unmerge"])==types.StringType:
			self.settings[self.settings["spec_prefix"]+"/unmerge"]=[self.settings[self.settings["spec_prefix"]+"/unmerge"]]
			print "key is a string"
		    myunmerge=self.settings[self.settings["spec_prefix"]+"/unmerge"][:]
		    
		    for x in range(0,len(myunmerge)):
		    #surround args with quotes for passing to bash,
		    #allows things like "<" to remain intact
		        myunmerge[x]="'"+myunmerge[x]+"'"
		    myunmerge=string.join(myunmerge)
		    
		    #before cleaning, unmerge stuff:
		    try:
			cmd("/bin/bash "+self.settings["sharedir"]+"/targets/" \
				+self.settings["target"]+"/unmerge.sh "+myunmerge,"Unmerge script failed.")
			print "unmerge shell script"
		    except CatalystError:
			self.unbind()
			raise
		touch(self.settings["autoresume_path"]+"unmerge")

	def target_setup(self):
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"target_setup"):
		    print "Resume point detected, skipping target_setup operation..."
	    else:
		print "Setting up filesystems per filesystem type"
		cmd("/bin/bash "+self.settings["controller_file"]+" target_image_setup "+ self.settings["target_iso_path"],"target_image_setup script failed.")
		touch(self.settings["autoresume_path"]+"target_setup")
	
	def setup_overlay(self):	
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"setup_overlay"):
		    print "Resume point detected, skipping setup_overlay operation..."
	    else:
		if self.settings.has_key(self.settings["spec_prefix"]+"/overlay"):
			cmd("rsync -a "+self.settings[self.settings["spec_prefix"]+"/overlay"]+"/* "+\
			self.settings["target_iso_path"], self.settings["spec_prefix"]+"overlay copy failed.")
		touch(self.settings["autoresume_path"]+"setup_overlay")
	
	def create_iso(self):
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"create_iso"):
		    print "Resume point detected, skipping create_iso operation..."
	    else:
		# create the ISO - this is the preferred method (the iso scripts do not always work)
		if self.settings.has_key("iso"):
			cmd("/bin/bash "+self.settings["controller_file"]+" iso "+\
				self.settings["iso"],"ISO creation script failed.")
			touch(self.settings["autoresume_path"]+"create_iso")

        def build_packages(self):
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"build_packages"):
		    print "Resume point detected, skipping build_packages operation..."
	    else:
		if self.settings.has_key(self.settings["spec_prefix"]+"/packages"):
			if self.settings.has_key("AUTORESUME") \
				and os.path.exists(self.settings["autoresume_path"]+"build_packages"):
					print "Resume point detected, skipping build_packages operation..."
			else:
				mypack=list_bashify(self.settings[self.settings["spec_prefix"]+"/packages"])
				try:
					cmd("/bin/bash "+self.settings["controller_file"]+\
						" build_packages "+mypack)
					touch(self.settings["autoresume_path"]+"build_packages")
				except CatalystError:
					self.unbind()
					raise CatalystError,self.settings["spec_prefix"] + "build aborting due to error."
	
	def build_kernel(self):
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"build_kernel"):
		    print "Resume point detected, skipping build_kernel operation..."
	    else:
		if self.settings.has_key("boot/kernel"):
	        	try:
				mynames=self.settings["boot/kernel"]
				if type(mynames)==types.StringType:
					mynames=[mynames]
		
				for kname in mynames:
					try:
						if not os.path.exists(self.settings["boot/kernel/"+kname+"/config"]):
							self.unbind()
							raise CatalystError, "Can't find kernel config: " \
								+self.settings["boot/kernel/"+kname+"/config"]
			
					except TypeError:
						raise CatalystError, "Required value boot/kernel/config not specified"
			
					try:
						cmd("cp "+self.settings["boot/kernel/"+kname+"/config"]+" "+ \
							self.settings["chroot_path"]+"/var/tmp/"+kname+".config", \
							"Couldn't copy kernel config: "+self.settings["boot/kernel/"+kname+"/config"])
		
					except CatalystError:
						self.unbind()

					# If we need to pass special options to the bootloader
					# for this kernel put them into the environment.
					if self.settings.has_key("boot/kernel/"+kname+"/kernelopts"):
						myopts=self.settings["boot/kernel/"+kname+"/kernelopts"]
				
						if type(myopts) != types.StringType:
							myopts = string.join(myopts)
						os.putenv(kname+"_kernelopts", myopts)

					else:
						os.putenv(kname+"_kernelopts", "")

					if not self.settings.has_key("boot/kernel/"+kname+"/extraversion"):
						self.settings["boot/kernel/"+kname+"/extraversion"]=""

					os.putenv("clst_kextraversion", self.settings["boot/kernel/"+kname+"/extraversion"])
					if self.settings.has_key("boot/kernel/"+kname+"/initramfs_overlay"):
					    if os.path.exists(self.settings["boot/kernel/"+kname+"/initramfs_overlay"]):
						print "Copying initramfs_overlay dir " +self.settings["boot/kernel/"+kname+"/initramfs_overlay"]
						
						cmd("mkdir -p "+self.settings["chroot_path"]+"/tmp/initramfs_overlay/" + \
							self.settings["boot/kernel/"+kname+"/initramfs_overlay"])
						
						cmd("cp -R "+self.settings["boot/kernel/"+kname+"/initramfs_overlay"]+"/* " + \
							self.settings["chroot_path"] + "/tmp/initramfs_overlay/" + \
							self.settings["boot/kernel/"+kname+"/initramfs_overlay"])
	
					    
					# execute the script that builds the kernel
					cmd("/bin/bash "+self.settings["controller_file"]+" kernel "+kname,\
			    		"Runscript kernel build failed")
					
					if self.settings.has_key("boot/kernel/"+kname+"/initramfs_overlay"):
						print "Cleaning up temporary overlay dir"
						cmd("rm -R "+self.settings["chroot_path"]+"/tmp/initramfs_overlay/")

				touch(self.settings["autoresume_path"]+"build_kernel")
			
			except CatalystError:
				self.unbind()
				raise CatalystError,"build aborting due to kernel build error."

	def bootloader(self):
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"bootloader"):
		    print "Resume point detected, skipping bootloader operation..."
	    else:
		try:
			cmd("/bin/bash "+self.settings["controller_file"]+" bootloader " + self.settings["target_iso_path"],\
				"Bootloader runscript failed.")
			touch(self.settings["autoresume_path"]+"bootloader")
		except CatalystError:
			self.unbind()
			raise CatalystError,"Runscript aborting due to error."

        def livecd_update(self):
	    if self.settings.has_key("AUTORESUME") \
		and os.path.exists(self.settings["autoresume_path"]+"livecd_update"):
		    print "Resume point detected, skipping build_packages operation..."
	    else:
		try:
			cmd("/bin/bash "+self.settings["controller_file"]+" livecd-update",\
				"livecd-update failed.")
			touch(self.settings["autoresume_path"]+"livecd_update")
		
		except CatalystError:
			self.unbind()
			raise CatalystError,"build aborting due to livecd_update error."

	def clear_chroot(self):
		myemp=self.settings["chroot_path"]
		if not os.path.isdir(myemp):
		    print myemp,"not a directory or does not exist, skipping 'chroot purge' operation."
		else:
		    print "Emptying directory",myemp
		    # stat the dir, delete the dir, recreate the dir and set
		    # the proper perms and ownership
		    mystat=os.stat(myemp)
		    shutil.rmtree(myemp)
		    os.makedirs(myemp,0755)
	
	def clear_packages(self):
	    if self.settings.has_key("PKGCACHE"):
		print "purging the pkgcache ..."

		myemp=self.settings["pkgcache_path"]
		if not os.path.isdir(myemp):
		    print myemp,"not a directory or does not exist, skipping 'pkgcache purge' operation."
		else:
		    print "Emptying directory",myemp
		    # stat the dir, delete the dir, recreate the dir and set
		    # the proper perms and ownership
		    mystat=os.stat(myemp)
		    shutil.rmtree(myemp)
		    os.makedirs(myemp,0755)
	
	def purge(self):
	    countdown(10,"Purging Caches ...")
	    if self.settings.has_key("PURGE"):
		print "clearing autoresume ..."
		self.clear_autoresume()
		
		print "clearing chroot ..."
		self.clear_chroot()
		
		print "clearing package cache ..."
		self.clear_packages()
