# Distributed under the GNU General Public License version 2
# Copyright 2003-2004 Gentoo Technologies, Inc.
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/livecd_stage2_target.py,v 1.5 2004/05/20 21:16:56 zhen Exp $

"""
Builder class for a LiveCD stage2 build.
"""

import os,string,imp,types,shutil
from catalyst_support import *
from generic_stage_target import *
from stat import *

class livecd_stage2_target(generic_stage_target):
	def __init__(self,spec,addlargs):
		self.required_values=["boot/kernel","livecd/cdfstype","livecd/archscript","livecd/runscript"]
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
		self.valid_values.extend(self.required_values)
		self.valid_values.extend(["livecd/cdtar","livecd/empty","livecd/rm","livecd/unmerge","livecd/iso","livecd/gk_mainargs","livecd/type","livecd/motd","livecd/overlay","livecd/modblacklist"])
		
		generic_stage_target.__init__(self,spec,addlargs)
		file_locate(self.settings, ["livecd/cdtar","livecd/archscript","livecd/runscript"])
	
	def unpack_and_bind(self):
		if os.path.exists(self.settings["chroot_path"]):
			print "Removing previously-existing livecd-stage2 chroot directory..."
			cmd("rm -rf "+self.settings["chroot_path"],"Error removing livecd-stage2 chroot")
			os.makedirs(self.settings["chroot_path"])
		print "Copying livecd-stage1 result to new livecd-stage2 work directory..."
		cmd("cp -a "+self.settings["source_path"]+"/* "+self.settings["chroot_path"],"Error copying initial livecd-stage2")
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
		print "Configuring profile link..."
		cmd("rm -f "+self.settings["chroot_path"]+"/etc/make.profile","Error zapping profile link")
		cmd("ln -sf ../usr/portage/profiles/"+self.settings["target_profile"]+" "+self.settings["chroot_path"]+"/etc/make.profile","Error creating profile link")
		
	def unmerge(self):
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
				cmd("/bin/bash "+self.settings["sharedir"]+"/targets/"+self.settings["target"]+"/unmerge.sh "+myunmerge,"unmerge script failed.")
			except CatalystError:
				self.unbind()
				raise

	def clean(self):
		generic_stage_target.clean(self)
		try:
			cmd("/bin/bash "+self.settings["livecd/runscript"]+" clean","clean runscript failed.")
		except:
			self.unbind()
			raise

	def preclean(self):
		try:
			cmd("/bin/bash "+self.settings["livecd/runscript"]+" preclean","preclean runscript failed.")
		except:
			self.unbind()
			raise

	def cdroot_setup(self):
		cmd("/bin/bash "+self.settings["livecd/runscript"]+" cdfs","cdfs runscript failed.")
		if self.settings.has_key("livecd/overlay"):
			cmd("/bin/cp -a "+self.settings["livecd/overlay"]+"/* "+self.settings["cdroot_path"],
					"LiveCD overlay copy failed.") 
		if self.settings.has_key("livecd/iso"):
			cmd("/bin/bash "+self.settings["livecd/runscript"]+" iso "+self.settings["livecd/iso"],"iso runscript failed.")
		print "livecd-stage2: complete!"

	def run_local(self):
		#first clean up any existing cdroot stuff
		if os.path.exists(self.settings["cdroot_path"]):
			print "cleaning previous livecd-stage2 build"
			cmd("rm -rf "+self.settings["cdroot_path"],"Could not remove existing directory: "+self.settings["cdroot_path"])
		os.makedirs(self.settings["cdroot_path"])
		#now, start building the kernel
		mynames=self.settings["boot/kernel"]
		if type(mynames)==types.StringType:
			mynames=[mynames]
		args=[]
		args.append(`len(mynames)`)
		for kname in mynames:
			args.append(kname)
			args.append(self.settings["boot/kernel/"+kname+"/sources"])
			if not os.path.exists(self.settings["boot/kernel/"+kname+"/config"]):
				self.unbind()
				raise CatalystError, "Can't find kernel config: "+self.settings["boot/kernel/"+kname+"/config"]

			# We must support multiple configs for the same kernel,
			# so we must manually edit the EXTRAVERSION on the kernel to allow them to coexist.
			# The extraversion field gets appended to the current EXTRAVERSION
			# in the kernel Makefile.  Examples of this usage are UP vs SMP kernels,
			# and on PPC64 we need a seperate pSeries, iSeries, and PPC970 (G5) kernels,
			# all compiled off the same source, without having to release a seperate 
			# livecd for each (since other than the kernel, they are all binary compatible)
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
			for extra in ["use","packages","gk_kernargs"]:
				if self.settings.has_key("boot/kernel/"+kname+"/"+extra):
					myex=self.settings["boot/kernel/"+kname+"/"+extra]
					if type(myex)==types.ListType:
						myex=string.join(myex)
					try:
						myf=open(self.settings["chroot_path"]+"/var/tmp/"+kname+"."+extra,"w")
					except:
						self.unbind()
						raise CatalystError,"Couldn't create file /var/tmp/"+kname+"."+extra+" in chroot."
					if extra=="use":
						myf.write("export USE=\""+myex+"\"\n")
					if extra=="gk_kernargs":
						myf.write("export clst_livecd_gk_kernargs=\""+myex+"\"\n")
					else:
						myf.write(myex+"\n")
					myf.close()
					
			retval=os.system("cp "+self.settings["boot/kernel/"+kname+"/config"]+" "+self.settings["chroot_path"]+"/var/tmp/"+kname+".config")
			if retval!=0:
				self.unbind()
				raise CatalystError, "Couldn't copy kernel config: "+self.settings["boot/kernel/"+kname+"/config"]

			# If we need to pass special options to the bootloader for this kernel
			# put them into the environment.
			if self.settings.has_key("boot/kernel/"+kname+"/kernelopts"):
				myopts=self.settings["boot/kernel/"+kname+"/kernelopts"]
				if type(myopts) != types.StringType:
					myopts = string.join(myopts)
				os.putenv(kname+"_kernelopts", myopts)
			else:
				os.putenv(kname+"_kernelopts", "")
			
		try:
			cmd("/bin/bash "+self.settings["livecd/runscript"]+" kernel "+list_bashify(args),"runscript kernel build failed")
			cmd("/bin/bash "+self.settings["livecd/runscript"]+" bootloader","bootloader runscript failed.")
		except CatalystError:
			self.unbind()
			raise CatalystError,"runscript aborting due to error."

		# what modules do we want to blacklist?
		if self.settings.has_key("livecd/modblacklist"):
			mylist=self.settings["livecd/modblacklist"]
			if type(mylist)==types.StringType:
				mylist=[mylist]
				try:
					myf=open(self.settings["chroot_path"]+"/etc/hotplug/blacklist","a")
				except:
					self.unbind()
					raise CatalystError,"Couldn't open "+self.settings["chroot_path"]+"/etc/hotplug/blacklist."
				myf.write("\n#Added by Catalyst:")
				for x in mylist:
					myf.write("\n"+x+"\n")

def register(foo):
	foo.update({"livecd-stage2":livecd_stage2_target})
	return foo
