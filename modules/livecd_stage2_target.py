# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/livecd_stage2_target.py,v 1.25 2004/12/16 23:13:24 wolf31o2 Exp $

"""
Builder class for a LiveCD stage2 build.
"""

import os,string,types,stat,shutil
from catalyst_support import *
from generic_stage_target import *

class livecd_stage2_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["boot/kernel","livecd/cdfstype",\
		"livecd/archscript","livecd/runscript"]
		
		self.valid_values=[]
		if not addlargs.has_key("boot/kernel"):
			raise CatalystError, "Required value boot/kernel not specified."
			
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
			self.valid_values.append("boot/kernel/"+x+"/postconf")
		
		self.valid_values.extend(self.required_values)
		self.valid_values.extend(["livecd/cdtar","livecd/empty","livecd/rm",\
			"livecd/unmerge","livecd/iso","livecd/gk_mainargs","livecd/type",\
			"livecd/motd","livecd/overlay","livecd/modblacklist","livecd/splash_theme",\
			"livecd/rcadd","livecd/rcdel","livecd/fsscript","livecd/xinitrc",\
			"livecd/root_overlay","livecd/devmanager","livecd/splash_type",\
			"gamecd/conf"])
		
		generic_stage_target.__init__(self,spec,addlargs)
		self.set_cdroot_path()
		file_locate(self.settings, ["livecd/cdtar","livecd/archscript","livecd/runscript"])
		if self.settings.has_key("portage_confdir"):
			file_locate(self.settings,["portage_confdir"],expand=0)
	
	def unpack_and_bind(self):
		if not os.path.exists(self.settings["chroot_path"]):
			os.makedirs(self.settings["chroot_path"])
				
		print "Copying livecd-stage1 result to new livecd-stage2 work directory..."
		cmd("rsync -a --delete "+self.settings["source_path"]+"/* "+self.settings["chroot_path"],\
			"Error copying initial livecd-stage2")
	
 		if os.path.exists(self.settings["chroot_path"]+"/usr/portage"):
 			print "Cleaning up existing portage tree snapshot..."
 			cmd("rm -rf "+self.settings["chroot_path"]+"/usr/portage",\
				"Error removing existing snapshot directory.")

 		print "Unpacking portage tree snapshot..."
 		cmd("tar xjpf "+self.settings["snapshot_path"]+" -C "+\
			self.settings["chroot_path"]+"/usr","Error unpacking snapshot")

		print "Configuring profile link..."
		cmd("rm -f "+self.settings["chroot_path"]+"/etc/make.profile","Error zapping profile link")
		cmd("ln -sf ../usr/portage/profiles/"+self.settings["target_profile"]+" "
			+self.settings["chroot_path"]+"/etc/make.profile","Error creating profile link")
	
		if self.settings.has_key("portage_confdir"):
			print "Configuring /etc/portage..."
			cmd("rm -rf "+self.settings["chroot_path"]+"/etc/portage","Error zapping /etc/portage")
			cmd("cp -R "+self.settings["portage_confdir"]+" "+self.settings["chroot_path"]+\
				"/etc/portage","Error copying /etc/portage")

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
        
	def set_target_path(self):
	    pass 
	    #self.settings["target_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]
	    	
	def set_source_path(self):
	    self.settings["source_path"]=self.settings["storedir"]+"/tmp/"+self.settings["source_subpath"]
	
	def set_cdroot_path(self):
	    self.settings["cdroot_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]

        def dir_setup(self):
                print "Setting up directories..."
                self.mount_safety_check()

                if not os.path.exists(self.settings["chroot_path"]+"/tmp"):
                        os.makedirs(self.settings["chroot_path"]+"/tmp")

                if not os.path.exists(self.settings["chroot_path"]):
                        os.makedirs(self.settings["chroot_path"])

                if self.settings.has_key("PKGCACHE"):
                        if not os.path.exists(self.settings["pkgcache_path"]):
                                os.makedirs(self.settings["pkgcache_path"])

	def unmerge(self):
		if self.settings.has_key("AUTORESUME") \
			and os.path.exists(self.settings["chroot_path"]+"/tmp/.clst_unmerge"):
			print "Resume point detected, skipping unmerge operation..."
		
		else:
			if self.settings.has_key("livecd/unmerge"):
				if type(self.settings["livecd/unmerge"])==types.StringType:
					self.settings["livecd/unmerge"]=[self.settings["livecd/unmerge"]]
				myunmerge=self.settings["livecd/unmerge"][:]
				
				for x in range(0,len(myunmerge)):
					#surround args with quotes for passing to bash, 
					#allows things like "<" to remain intact
					myunmerge[x]="'"+myunmerge[x]+"'"
				myunmerge=string.join(myunmerge)
				#before cleaning, unmerge stuff:
				
				try:
					cmd("/bin/bash "+self.settings["sharedir"]+"/targets/"
						+self.settings["target"]+"/unmerge.sh "+myunmerge,"Unmerge script failed.")
				
				except CatalystError:
					self.unbind()
					raise
				touch(self.settings["chroot_path"]+"/tmp/.clst_unmerge")

	def clean(self):
		if self.settings.has_key("livecd/empty"):
		
			if type(self.settings["livecd/empty"])==types.StringType:
				self.settings["livecd/empty"]=[self.settings["livecd/empty"]]
			
			for x in self.settings["livecd/empty"]:
				myemp=self.settings["chroot_path"]+x
				if not os.path.isdir(myemp):
					print x,"not a directory or does not exist, skipping 'empty' operation."
					continue
				print "Emptying directory",x
				# stat the dir, delete the dir, recreate the dir and set 
				# the proper perms and ownership
				mystat=os.stat(myemp)
				shutil.rmtree(myemp)
				os.makedirs(myemp)
				os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
				os.chmod(myemp,mystat[ST_MODE])
			
		if self.settings.has_key("livecd/rm"):	
				
			if type(self.settings["livecd/rm"])==types.StringType:
				self.settings["livecd/rm"]=[self.settings["livecd/rm"]]
			
			for x in self.settings["livecd/rm"]:
				# we're going to shell out for all these cleaning operations,
				# so we get easy glob handling
				print "livecd: removing "+x
				os.system("rm -rf "+self.settings["chroot_path"]+x)

		try:
			cmd("/bin/bash "+self.settings["livecd/runscript"]+" clean",\
				"Clean runscript failed.")
		except:
			self.unbind()
			raise

	def preclean(self):
		try:
			cmd("/bin/bash "+self.settings["livecd/runscript"]+" preclean",\
				"Preclean runscript failed.")
	
		except:
			self.unbind()
			raise

	def cdroot_setup(self):
		cmd("/bin/bash "+self.settings["livecd/runscript"]+" cdfs","CDFS runscript failed.")
		
		if self.settings.has_key("livecd/overlay"):
			cmd("rsync -a "+self.settings["livecd/overlay"]+"/* "+\
			self.settings["cdroot_path"],"LiveCD overlay copy failed.")
	
		# clean up the resume points
		if self.settings.has_key("AUTORESUME"):
			cmd("rm -f "+self.settings["chroot_path"]+"/tmp/.clst*",\
			"Couldn't remove resume points")
	
		# create the ISO - this is the preferred method (the iso scripts do not always work)
		if self.settings.has_key("livecd/iso"):
			cmd("/bin/bash "+self.settings["livecd/runscript"]+" iso "+\
				self.settings["livecd/iso"],"ISO creation runscript failed.")
		
		print "livecd-stage2: complete!"

	def build_kernel(self):
		mynames=self.settings["boot/kernel"]
		if type(mynames)==types.StringType:
			mynames=[mynames]
		args=[]
		args.append(`len(mynames)`)
		
		for kname in mynames:
			args.append(kname)
			args.append(self.settings["boot/kernel/"+kname+"/sources"])
			try:
				if not os.path.exists(self.settings["boot/kernel/"+kname+"/config"]):
					self.unbind()
					raise CatalystError, "Can't find kernel config: " \
						+self.settings["boot/kernel/"+kname+"/config"]
			
			except TypeError:
				raise CatalystError, "Required value boot/kernel/config not specified"
			
			"""
			We must support multiple configs for the same kernel,
			so we must manually edit the EXTRAVERSION on the kernel to allow them to coexist.
			The extraversion field gets appended to the current EXTRAVERSION
			in the kernel Makefile.  Examples of this usage are UP vs SMP kernels,
			and on PPC64 we need a seperate pSeries, iSeries, and PPC970 (G5) kernels,
			all compiled off the same source, without having to release a seperate 
			livecd for each (since other than the kernel, they are all binary compatible)
			"""
			if self.settings.has_key("boot/kernel/"+kname+"/extraversion"):
				# extraversion is now an optional parameter, so that don't need to
				# worry about it unless they have to
				args.append(self.settings["boot/kernel/"+kname+"/extraversion"])
			
			else:
				# this value will be detected on the bash side and indicate
				# that EXTRAVERSION processing
				# should be skipped
				args.append("NULL_VALUE")
			
			# write out /var/tmp/kname.(use|packages) files, used for kernel USE
			# and extra packages settings
			for extra in ["use","packages","postconf","gk_kernargs"]:
				if self.settings.has_key("boot/kernel/"+kname+"/"+extra):
					myex=self.settings["boot/kernel/"+kname+"/"+extra]
					if type(myex)==types.ListType:
						myex=string.join(myex)
					try:
						myf=open(self.settings["chroot_path"]+"/var/tmp/"+kname+"."+extra,"w")
					except:
						self.unbind()
						raise CatalystError,"Couldn't create file /var/tmp/"+kname+"."+extra+" in chroot."
					# write out to the file	
					if extra=="use":
						myf.write("export USE=\""+myex+"\"\n")
					if extra=="gk_kernargs":
						myf.write("export clst_livecd_gk_kernargs=\""+myex+"\"\n")
					else:
						myf.write(myex+"\n")
					myf.close()
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

		# execute the script that builds the kernel
		cmd("/bin/bash "+self.settings["livecd/runscript"]+" kernel "+list_bashify(args),\
			"Runscript kernel build failed")

	def run_local(self):
		# first clean up any existing cdroot stuff
		if os.path.exists(self.settings["cdroot_path"]):
			print "cleaning previous livecd-stage2 build"
			cmd("rm -rf "+self.settings["cdroot_path"],
				"Could not remove existing directory: "+self.settings["cdroot_path"])
			
		if not os.path.exists(self.settings["cdroot_path"]):
			os.makedirs(self.settings["cdroot_path"])
				
		# the runscripts do the real building, so execute them now
		# this is the part that we want to resume on since it is the most time consuming
		try:
			self.build_kernel()
			
			cmd("/bin/bash "+self.settings["livecd/runscript"]+" bootloader",\
				"Bootloader runscript failed.")
		
		except CatalystError:
			self.unbind()
			raise CatalystError,"Runscript aborting due to error."

		# what modules do we want to blacklist?
		if self.settings.has_key("livecd/modblacklist"):
			try:
				myf=open(self.settings["chroot_path"]+"/etc/hotplug/blacklist","a")
			except:
				self.unbind()
				raise CatalystError,"Couldn't open "+self.settings["chroot_path"]+"/etc/hotplug/blacklist."
			myf.write("\n#Added by Catalyst:")
			for x in self.settings["livecd/modblacklist"]:
				myf.write("\n"+x)
			myf.close()

		# copy over the livecd/root_overlay
		if self.settings.has_key("livecd/root_overlay"):
			cmd("rsync -a "+self.settings["livecd/root_overlay"]+"/* "+\
				self.settings["chroot_path"], "livecd/root_overlay copy failed.")
	def set_action_sequence(self):
		self.settings["action_sequence"]=["dir_setup","unpack_and_bind","chroot_setup",\
						"setup_environment","run_local","preclean","unmerge",\
						"unbind","clean","cdroot_setup"]

def register(foo):
	foo.update({"livecd-stage2":livecd_stage2_target})
	return foo
