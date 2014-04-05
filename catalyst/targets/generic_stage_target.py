import os,string,imp,types,shutil
from catalyst.support import *
from generic_target import *
from stat import *
from catalyst.lock import LockDir

from catalyst.defaults import (SOURCE_MOUNT_DEFAULTS, TARGET_MOUNT_DEFAULTS,
	PORT_LOGDIR_CLEAN)

# for convienience
pjoin = os.path.join


class generic_stage_target(generic_target):
	"""
	This class does all of the chroot setup, copying of files, etc. It is
	the driver class for pretty much everything that Catalyst does.
	"""
	def __init__(self,myspec,addlargs):
		self.required_values.extend(["version_stamp","target","subarch",\
			"rel_type","profile","snapshot","source_subpath"])

		self.valid_values.extend(["version_stamp","target","subarch",\
			"rel_type","profile","snapshot","source_subpath","portage_confdir",\
			"cflags","cxxflags","ldflags","cbuild","hostuse","portage_overlay",\
			"distcc_hosts","makeopts","pkgcache_path","kerncache_path"])

		self.set_valid_build_kernel_vars(addlargs)
		generic_target.__init__(self,myspec,addlargs)

		"""
		The semantics of subarchmap and machinemap changed a bit in 2.0.3 to
		work better with vapier's CBUILD stuff. I've removed the "monolithic"
		machinemap from this file and split up its contents amongst the
		various arch/foo.py files.

		When register() is called on each module in the arch/ dir, it now
		returns a tuple instead of acting on the subarchmap dict that is
		passed to it. The tuple contains the values that were previously
		added to subarchmap as well as a new list of CHOSTs that go along
		with that arch. This allows us to build machinemap on the fly based
		on the keys in subarchmap and the values of the 2nd list returned
		(tmpmachinemap).

		Also, after talking with vapier. I have a slightly better idea of what
		certain variables are used for and what they should be set to. Neither
		'buildarch' or 'hostarch' are used directly, so their value doesn't
		really matter. They are just compared to determine if we are
		cross-compiling. Because of this, they are just set to the name of the
		module in arch/ that the subarch is part of to make things simpler.
		The entire build process is still based off of 'subarch' like it was
		previously. -agaffney
		"""

		self.archmap = {}
		self.subarchmap = {}
		machinemap = {}
		arch_dir = self.settings["PythonDir"] + "/arch/"
		for x in [x[:-3] for x in os.listdir(arch_dir) if x.endswith(".py")]:
			if x == "__init__":
				continue
			try:
				fh=open(arch_dir + x + ".py")
				"""
				This next line loads the plugin as a module and assigns it to
				archmap[x]
				"""
				self.archmap[x]=imp.load_module(x,fh,"../arch/" + x + ".py",
					(".py", "r", imp.PY_SOURCE))
				"""
				This next line registers all the subarches supported in the
				plugin
				"""
				tmpsubarchmap, tmpmachinemap = self.archmap[x].register()
				self.subarchmap.update(tmpsubarchmap)
				for machine in tmpmachinemap:
					machinemap[machine] = x
				for subarch in tmpsubarchmap:
					machinemap[subarch] = x
				fh.close()
			except IOError:
				"""
				This message should probably change a bit, since everything in
				the dir should load just fine. If it doesn't, it's probably a
				syntax error in the module
				"""
				msg("Can't find/load " + x + ".py plugin in " + arch_dir)

		if "chost" in self.settings:
			hostmachine = self.settings["chost"].split("-")[0]
			if hostmachine not in machinemap:
				raise CatalystError, "Unknown host machine type "+hostmachine
			self.settings["hostarch"]=machinemap[hostmachine]
		else:
			hostmachine = self.settings["subarch"]
			if hostmachine in machinemap:
				hostmachine = machinemap[hostmachine]
			self.settings["hostarch"]=hostmachine
		if "cbuild" in self.settings:
			buildmachine = self.settings["cbuild"].split("-")[0]
		else:
			buildmachine = os.uname()[4]
		if buildmachine not in machinemap:
			raise CatalystError, "Unknown build machine type "+buildmachine
		self.settings["buildarch"]=machinemap[buildmachine]
		self.settings["crosscompile"]=(self.settings["hostarch"]!=\
			self.settings["buildarch"])

		""" Call arch constructor, pass our settings """
		try:
			self.arch=self.subarchmap[self.settings["subarch"]](self.settings)
		except KeyError:
			print "Invalid subarch: "+self.settings["subarch"]
			print "Choose one of the following:",
			for x in self.subarchmap:
				print x,
			print
			sys.exit(2)

		print "Using target:",self.settings["target"]
		""" Print a nice informational message """
		if self.settings["buildarch"]==self.settings["hostarch"]:
			print "Building natively for",self.settings["hostarch"]
		elif self.settings["crosscompile"]:
			print "Cross-compiling on",self.settings["buildarch"],\
				"for different machine type",self.settings["hostarch"]
		else:
			print "Building on",self.settings["buildarch"],\
				"for alternate personality type",self.settings["hostarch"]

		""" This must be set first as other set_ options depend on this """
		self.set_spec_prefix()

		""" Define all of our core variables """
		self.set_target_profile()
		self.set_target_subpath()
		self.set_source_subpath()

		""" Set paths """
		self.set_snapshot_path()
		self.set_root_path()
		self.set_source_path()
		self.set_snapcache_path()
		self.set_chroot_path()
		self.set_autoresume_path()
		self.set_dest_path()
		self.set_stage_path()
		self.set_target_path()

		self.set_controller_file()
		self.set_action_sequence()
		self.set_use()
		self.set_cleanables()
		self.set_iso_volume_id()
		self.set_build_kernel_vars()
		self.set_fsscript()
		self.set_install_mask()
		self.set_rcadd()
		self.set_rcdel()
		self.set_cdtar()
		self.set_fstype()
		self.set_fsops()
		self.set_iso()
		self.set_packages()
		self.set_rm()
		self.set_linuxrc()
		self.set_busybox_config()
		self.set_overlay()
		self.set_portage_overlay()
		self.set_root_overlay()

		"""
		This next line checks to make sure that the specified variables exist
		on disk.
		"""
		#pdb.set_trace()
		file_locate(self.settings,["source_path","snapshot_path","distdir"],\
			expand=0)
		""" If we are using portage_confdir, check that as well. """
		if "portage_confdir" in self.settings:
			file_locate(self.settings,["portage_confdir"],expand=0)

		""" Setup our mount points """
		# initialize our target mounts.
		self.target_mounts = TARGET_MOUNT_DEFAULTS.copy()

		self.mounts = ["proc", "dev", "portdir", "distdir", "port_tmpdir"]
		# initialize our source mounts
		self.mountmap = SOURCE_MOUNT_DEFAULTS.copy()
		# update them from settings
		self.mountmap["distdir"] = self.settings["distdir"]
		if "SNAPCACHE" not in self.settings:
			self.mounts.remove("portdir")
			self.mountmap["portdir"] = None
		else:
			self.mountmap["portdir"] = normpath("/".join([
				self.settings["snapshot_cache_path"],
				self.settings["repo_name"],
				]))
		if os.uname()[0] == "Linux":
			self.mounts.append("devpts")
			self.mounts.append("shm")

		self.set_mounts()

		"""
		Configure any user specified options (either in catalyst.conf or on
		the command line).
		"""
		if "PKGCACHE" in self.settings:
			self.set_pkgcache_path()
			print "Location of the package cache is "+\
				self.settings["pkgcache_path"]
			self.mounts.append("packagedir")
			self.mountmap["packagedir"] = self.settings["pkgcache_path"]

		if "KERNCACHE" in self.settings:
			self.set_kerncache_path()
			print "Location of the kerncache is "+\
				self.settings["kerncache_path"]
			self.mounts.append("kerncache")
			self.mountmap["kerncache"] = self.settings["kerncache_path"]

		if "CCACHE" in self.settings:
			if "CCACHE_DIR" in os.environ:
				ccdir=os.environ["CCACHE_DIR"]
				del os.environ["CCACHE_DIR"]
			else:
				ccdir="/root/.ccache"
			if not os.path.isdir(ccdir):
				raise CatalystError,\
					"Compiler cache support can't be enabled (can't find "+\
					ccdir+")"
			self.mounts.append("ccache")
			self.mountmap["ccache"] = ccdir
			""" for the chroot: """
			self.env["CCACHE_DIR"] = self.target_mounts["ccache"]

		if "ICECREAM" in self.settings:
			self.mounts.append("icecream")
			self.mountmap["icecream"] = self.settings["icecream"]
			self.env["PATH"] = self.target_mounts["icecream"] + ":" + \
				self.env["PATH"]

		if "port_logdir" in self.settings:
			self.mounts.append("port_logdir")
			self.mountmap["port_logdir"] = self.settings["port_logdir"]
			self.env["PORT_LOGDIR"] = self.settings["port_logdir"]
			self.env["PORT_LOGDIR_CLEAN"] = PORT_LOGDIR_CLEAN

	def override_cbuild(self):
		if "CBUILD" in self.makeconf:
			self.settings["CBUILD"]=self.makeconf["CBUILD"]

	def override_chost(self):
		if "CHOST" in self.makeconf:
			self.settings["CHOST"]=self.makeconf["CHOST"]

	def override_cflags(self):
		if "CFLAGS" in self.makeconf:
			self.settings["CFLAGS"]=self.makeconf["CFLAGS"]

	def override_cxxflags(self):
		if "CXXFLAGS" in self.makeconf:
			self.settings["CXXFLAGS"]=self.makeconf["CXXFLAGS"]

	def override_ldflags(self):
		if "LDFLAGS" in self.makeconf:
			self.settings["LDFLAGS"]=self.makeconf["LDFLAGS"]

	def set_install_mask(self):
		if "install_mask" in self.settings:
			if type(self.settings["install_mask"])!=types.StringType:
				self.settings["install_mask"]=\
					string.join(self.settings["install_mask"])

	def set_spec_prefix(self):
		self.settings["spec_prefix"]=self.settings["target"]

	def set_target_profile(self):
		self.settings["target_profile"]=self.settings["profile"]

	def set_target_subpath(self):
		self.settings["target_subpath"]=self.settings["rel_type"]+"/"+\
				self.settings["target"]+"-"+self.settings["subarch"]+"-"+\
				self.settings["version_stamp"]

	def set_source_subpath(self):
		if type(self.settings["source_subpath"])!=types.StringType:
			raise CatalystError,\
				"source_subpath should have been a string. Perhaps you have something wrong in your spec file?"

	def set_pkgcache_path(self):
		if "pkgcache_path" in self.settings:
			if type(self.settings["pkgcache_path"])!=types.StringType:
				self.settings["pkgcache_path"]=\
					normpath(string.join(self.settings["pkgcache_path"]))
		else:
			self.settings["pkgcache_path"]=\
				normpath(self.settings["storedir"]+"/packages/"+\
				self.settings["target_subpath"]+"/")

	def set_kerncache_path(self):
		if "kerncache_path" in self.settings:
			if type(self.settings["kerncache_path"])!=types.StringType:
				self.settings["kerncache_path"]=\
					normpath(string.join(self.settings["kerncache_path"]))
		else:
			self.settings["kerncache_path"]=normpath(self.settings["storedir"]+\
				"/kerncache/"+self.settings["target_subpath"]+"/")

	def set_target_path(self):
		self.settings["target_path"]=normpath(self.settings["storedir"]+\
			"/builds/"+self.settings["target_subpath"]+".tar.bz2")
		setup_target_path_resume = pjoin(self.settings["autoresume_path"],
			"setup_target_path")
		if "AUTORESUME" in self.settings and \
				os.path.exists(setup_target_path_resume):
			print \
				"Resume point detected, skipping target path setup operation..."
		else:
			""" First clean up any existing target stuff """
			# XXX WTF are we removing the old tarball before we start building the
			# XXX new one? If the build fails, you don't want to be left with
			# XXX nothing at all
#			if os.path.isfile(self.settings["target_path"]):
#				cmd("rm -f "+self.settings["target_path"],\
#					"Could not remove existing file: "\
#					+self.settings["target_path"],env=self.env)
			touch(setup_target_path_resume)

			if not os.path.exists(self.settings["storedir"]+"/builds/"):
				os.makedirs(self.settings["storedir"]+"/builds/")

	def set_fsscript(self):
		if self.settings["spec_prefix"]+"/fsscript" in self.settings:
			self.settings["fsscript"]=\
				self.settings[self.settings["spec_prefix"]+"/fsscript"]
			del self.settings[self.settings["spec_prefix"]+"/fsscript"]

	def set_rcadd(self):
		if self.settings["spec_prefix"]+"/rcadd" in self.settings:
			self.settings["rcadd"]=\
				self.settings[self.settings["spec_prefix"]+"/rcadd"]
			del self.settings[self.settings["spec_prefix"]+"/rcadd"]

	def set_rcdel(self):
		if self.settings["spec_prefix"]+"/rcdel" in self.settings:
			self.settings["rcdel"]=\
				self.settings[self.settings["spec_prefix"]+"/rcdel"]
			del self.settings[self.settings["spec_prefix"]+"/rcdel"]

	def set_cdtar(self):
		if self.settings["spec_prefix"]+"/cdtar" in self.settings:
			self.settings["cdtar"]=\
				normpath(self.settings[self.settings["spec_prefix"]+"/cdtar"])
			del self.settings[self.settings["spec_prefix"]+"/cdtar"]

	def set_iso(self):
		if self.settings["spec_prefix"]+"/iso" in self.settings:
			if self.settings[self.settings["spec_prefix"]+"/iso"].startswith('/'):
				self.settings["iso"]=\
					normpath(self.settings[self.settings["spec_prefix"]+"/iso"])
			else:
				# This automatically prepends the build dir to the ISO output path
				# if it doesn't start with a /
				self.settings["iso"] = normpath(self.settings["storedir"] + \
					"/builds/" + self.settings["rel_type"] + "/" + \
					self.settings[self.settings["spec_prefix"]+"/iso"])
			del self.settings[self.settings["spec_prefix"]+"/iso"]

	def set_fstype(self):
		if self.settings["spec_prefix"]+"/fstype" in self.settings:
			self.settings["fstype"]=\
				self.settings[self.settings["spec_prefix"]+"/fstype"]
			del self.settings[self.settings["spec_prefix"]+"/fstype"]

		if "fstype" not in self.settings:
			self.settings["fstype"]="normal"
			for x in self.valid_values:
				if x ==  self.settings["spec_prefix"]+"/fstype":
					print "\n"+self.settings["spec_prefix"]+\
						"/fstype is being set to the default of \"normal\"\n"

	def set_fsops(self):
		if "fstype" in self.settings:
			self.valid_values.append("fsops")
			if self.settings["spec_prefix"]+"/fsops" in self.settings:
				self.settings["fsops"]=\
					self.settings[self.settings["spec_prefix"]+"/fsops"]
				del self.settings[self.settings["spec_prefix"]+"/fsops"]

	def set_source_path(self):
		if "SEEDCACHE" in self.settings\
			and os.path.isdir(normpath(self.settings["storedir"]+"/tmp/"+\
				self.settings["source_subpath"]+"/")):
			self.settings["source_path"]=normpath(self.settings["storedir"]+\
				"/tmp/"+self.settings["source_subpath"]+"/")
		else:
			self.settings["source_path"]=normpath(self.settings["storedir"]+\
				"/builds/"+self.settings["source_subpath"]+".tar.bz2")
			if os.path.isfile(self.settings["source_path"]):
				# XXX: Is this even necessary if the previous check passes?
				if os.path.exists(self.settings["source_path"]):
					self.settings["source_path_hash"] = \
						self.settings["hash_map"].generate_hash(
							self.settings["source_path"],
							hash_ = self.settings["hash_function"],
							verbose = False)
		print "Source path set to "+self.settings["source_path"]
		if os.path.isdir(self.settings["source_path"]):
			print "\tIf this is not desired, remove this directory or turn off"
			print "\tseedcache in the options of catalyst.conf the source path"
			print "\twill then be "+\
				normpath(self.settings["storedir"]+"/builds/"+\
				self.settings["source_subpath"]+".tar.bz2\n")

	def set_dest_path(self):
		if "root_path" in self.settings:
			self.settings["destpath"]=normpath(self.settings["chroot_path"]+\
				self.settings["root_path"])
		else:
			self.settings["destpath"]=normpath(self.settings["chroot_path"])

	def set_cleanables(self):
		self.settings["cleanables"]=["/etc/resolv.conf","/var/tmp/*","/tmp/*",\
			"/root/*", self.settings["portdir"]]

	def set_snapshot_path(self):
		self.settings["snapshot_path"]=normpath(self.settings["storedir"]+\
			"/snapshots/" + self.settings["snapshot_name"] +
			self.settings["snapshot"] + ".tar.xz")

		if os.path.exists(self.settings["snapshot_path"]):
			self.settings["snapshot_path_hash"] = \
				self.settings["hash_map"].generate_hash(
					self.settings["snapshot_path"],
					hash_ = self.settings["hash_function"],
					verbose = False)
		else:
			self.settings["snapshot_path"]=normpath(self.settings["storedir"]+\
				"/snapshots/" + self.settings["snapshot_name"] +
				self.settings["snapshot"] + ".tar.bz2")

			if os.path.exists(self.settings["snapshot_path"]):
				self.settings["snapshot_path_hash"] = \
					self.settings["hash_map"].generate_hash(
						self.settings["snapshot_path"],
						hash_ = self.settings["hash_function"],
						verbose = False)

	def set_snapcache_path(self):
		if "SNAPCACHE" in self.settings:
			self.settings["snapshot_cache_path"] = \
				normpath(self.settings["snapshot_cache"] + "/" +
					self.settings["snapshot"])
			self.snapcache_lock=\
				LockDir(self.settings["snapshot_cache_path"])
			print "Caching snapshot to "+self.settings["snapshot_cache_path"]

	def set_chroot_path(self):
		"""
		NOTE: the trailing slash has been removed
		Things *could* break if you don't use a proper join()
		"""
		self.settings["chroot_path"]=normpath(self.settings["storedir"]+\
			"/tmp/"+self.settings["target_subpath"])
		self.chroot_lock=LockDir(self.settings["chroot_path"])

	def set_autoresume_path(self):
		self.settings["autoresume_path"] = normpath(pjoin(
			self.settings["storedir"], "tmp", self.settings["rel_type"],
			".autoresume-%s-%s-%s"
			%(self.settings["target"], self.settings["subarch"],
				self.settings["version_stamp"])
			))
		if "AUTORESUME" in self.settings:
			print "The autoresume path is " + self.settings["autoresume_path"]
		if not os.path.exists(self.settings["autoresume_path"]):
			os.makedirs(self.settings["autoresume_path"],0755)

	def set_controller_file(self):
		self.settings["controller_file"]=normpath(self.settings["sharedir"]+\
			"/targets/"+self.settings["target"]+"/"+self.settings["target"]+\
			"-controller.sh")

	def set_iso_volume_id(self):
		if self.settings["spec_prefix"]+"/volid" in self.settings:
			self.settings["iso_volume_id"]=\
				self.settings[self.settings["spec_prefix"]+"/volid"]
			if len(self.settings["iso_volume_id"])>32:
				raise CatalystError,\
					"ISO volume ID must not exceed 32 characters."
		else:
			self.settings["iso_volume_id"]="catalyst "+self.settings["snapshot"]

	def set_action_sequence(self):
		""" Default action sequence for run method """
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
				"setup_confdir","portage_overlay",\
				"base_dirs","bind","chroot_setup","setup_environment",\
				"run_local","preclean","unbind","clean"]
#		if "TARBALL" in self.settings or \
#			"FETCH" not in self.settings:
		if "FETCH" not in self.settings:
			self.settings["action_sequence"].append("capture")
		self.settings["action_sequence"].append("clear_autoresume")

	def set_use(self):
		if self.settings["spec_prefix"]+"/use" in self.settings:
			self.settings["use"]=\
				self.settings[self.settings["spec_prefix"]+"/use"]
			del self.settings[self.settings["spec_prefix"]+"/use"]
		if "use" not in self.settings:
			self.settings["use"]=""
		if type(self.settings["use"])==types.StringType:
			self.settings["use"]=self.settings["use"].split()

		# Force bindist when options ask for it
		if "BINDIST" in self.settings:
			self.settings["use"].append("bindist")

	def set_stage_path(self):
		self.settings["stage_path"]=normpath(self.settings["chroot_path"])

	def set_mounts(self):
		pass

	def set_packages(self):
		pass

	def set_rm(self):
		if self.settings["spec_prefix"]+"/rm" in self.settings:
			if type(self.settings[self.settings["spec_prefix"]+\
				"/rm"])==types.StringType:
				self.settings[self.settings["spec_prefix"]+"/rm"]=\
					self.settings[self.settings["spec_prefix"]+"/rm"].split()

	def set_linuxrc(self):
		if self.settings["spec_prefix"]+"/linuxrc" in self.settings:
			if type(self.settings[self.settings["spec_prefix"]+\
				"/linuxrc"])==types.StringType:
				self.settings["linuxrc"]=\
					self.settings[self.settings["spec_prefix"]+"/linuxrc"]
				del self.settings[self.settings["spec_prefix"]+"/linuxrc"]

	def set_busybox_config(self):
		if self.settings["spec_prefix"]+"/busybox_config" in self.settings:
			if type(self.settings[self.settings["spec_prefix"]+\
				"/busybox_config"])==types.StringType:
				self.settings["busybox_config"]=\
					self.settings[self.settings["spec_prefix"]+"/busybox_config"]
				del self.settings[self.settings["spec_prefix"]+"/busybox_config"]

	def set_portage_overlay(self):
		if "portage_overlay" in self.settings:
			if type(self.settings["portage_overlay"])==types.StringType:
				self.settings["portage_overlay"]=\
					self.settings["portage_overlay"].split()
			print "portage_overlay directories are set to: \""+\
				string.join(self.settings["portage_overlay"])+"\""

	def set_overlay(self):
		if self.settings["spec_prefix"]+"/overlay" in self.settings:
			if type(self.settings[self.settings["spec_prefix"]+\
				"/overlay"])==types.StringType:
				self.settings[self.settings["spec_prefix"]+"/overlay"]=\
					self.settings[self.settings["spec_prefix"]+\
					"/overlay"].split()

	def set_root_overlay(self):
		if self.settings["spec_prefix"]+"/root_overlay" in self.settings:
			if type(self.settings[self.settings["spec_prefix"]+\
				"/root_overlay"])==types.StringType:
				self.settings[self.settings["spec_prefix"]+"/root_overlay"]=\
					self.settings[self.settings["spec_prefix"]+\
					"/root_overlay"].split()

	def set_root_path(self):
		""" ROOT= variable for emerges """
		self.settings["root_path"]="/"

	def set_valid_build_kernel_vars(self,addlargs):
		if "boot/kernel" in addlargs:
			if type(addlargs["boot/kernel"])==types.StringType:
				loopy=[addlargs["boot/kernel"]]
			else:
				loopy=addlargs["boot/kernel"]

			for x in loopy:
				self.valid_values.append("boot/kernel/"+x+"/aliases")
				self.valid_values.append("boot/kernel/"+x+"/config")
				self.valid_values.append("boot/kernel/"+x+"/console")
				self.valid_values.append("boot/kernel/"+x+"/extraversion")
				self.valid_values.append("boot/kernel/"+x+"/gk_action")
				self.valid_values.append("boot/kernel/"+x+"/gk_kernargs")
				self.valid_values.append("boot/kernel/"+x+"/initramfs_overlay")
				self.valid_values.append("boot/kernel/"+x+"/machine_type")
				self.valid_values.append("boot/kernel/"+x+"/sources")
				self.valid_values.append("boot/kernel/"+x+"/softlevel")
				self.valid_values.append("boot/kernel/"+x+"/use")
				self.valid_values.append("boot/kernel/"+x+"/packages")
				if "boot/kernel/"+x+"/packages" in addlargs:
					if type(addlargs["boot/kernel/"+x+\
						"/packages"])==types.StringType:
						addlargs["boot/kernel/"+x+"/packages"]=\
							[addlargs["boot/kernel/"+x+"/packages"]]

	def set_build_kernel_vars(self):
		if self.settings["spec_prefix"]+"/gk_mainargs" in self.settings:
			self.settings["gk_mainargs"]=\
				self.settings[self.settings["spec_prefix"]+"/gk_mainargs"]
			del self.settings[self.settings["spec_prefix"]+"/gk_mainargs"]

	def kill_chroot_pids(self):
		print "Checking for processes running in chroot and killing them."

		"""
		Force environment variables to be exported so script can see them
		"""
		self.setup_environment()

		if os.path.exists(self.settings["sharedir"]+\
			"/targets/support/kill-chroot-pids.sh"):
			cmd("/bin/bash "+self.settings["sharedir"]+\
				"/targets/support/kill-chroot-pids.sh",\
				"kill-chroot-pids script failed.",env=self.env)

	def mount_safety_check(self):
		"""
		Check and verify that none of our paths in mypath are mounted. We don't
		want to clean up with things still mounted, and this allows us to check.
		Returns 1 on ok, 0 on "something is still mounted" case.
		"""

		if not os.path.exists(self.settings["chroot_path"]):
			return

		print "self.mounts =", self.mounts
		for x in self.mounts:
			target = normpath(self.settings["chroot_path"] + self.target_mounts[x])
			print "mount_safety_check() x =", x, target
			if not os.path.exists(target):
				continue

			if ismount(target):
				""" Something is still mounted "" """
				try:
					print target + " is still mounted; performing auto-bind-umount...",
					""" Try to umount stuff ourselves """
					self.unbind()
					if ismount(target):
						raise CatalystError, "Auto-unbind failed for " + target
					else:
						print "Auto-unbind successful..."
				except CatalystError:
					raise CatalystError, "Unable to auto-unbind " + target

	def unpack(self):
		unpack=True

		unpack_resume = pjoin(self.settings["autoresume_path"], "unpack")
		clst_unpack_hash=read_from_clst(unpack_resume)

		if "SEEDCACHE" in self.settings:
			if os.path.isdir(self.settings["source_path"]):
				""" SEEDCACHE Is a directory, use rsync """
				unpack_cmd="rsync -a --delete "+self.settings["source_path"]+\
					" "+self.settings["chroot_path"]
				display_msg="\nStarting rsync from "+\
					self.settings["source_path"]+"\nto "+\
					self.settings["chroot_path"]+\
					" (This may take some time) ...\n"
				error_msg="Rsync of "+self.settings["source_path"]+" to "+\
					self.settings["chroot_path"]+" failed."
			else:
				""" SEEDCACHE is a not a directory, try untar'ing """
				print "Referenced SEEDCACHE does not appear to be a directory, trying to untar..."
				display_msg="\nStarting tar extract from "+\
					self.settings["source_path"]+"\nto "+\
					self.settings["chroot_path"]+\
						" (This may take some time) ...\n"
				if "bz2" == self.settings["chroot_path"][-3:]:
					unpack_cmd="tar -I lbzip2 -xpf "+self.settings["source_path"]+" -C "+\
						self.settings["chroot_path"]
				else:
					unpack_cmd="tar -I lbzip2 -xpf "+self.settings["source_path"]+" -C "+\
						self.settings["chroot_path"]
				error_msg="Tarball extraction of "+\
					self.settings["source_path"]+" to "+\
					self.settings["chroot_path"]+" failed."
		else:
			""" No SEEDCACHE, use tar """
			display_msg="\nStarting tar extract from "+\
				self.settings["source_path"]+"\nto "+\
				self.settings["chroot_path"]+\
				" (This may take some time) ...\n"
			if "bz2" == self.settings["chroot_path"][-3:]:
				unpack_cmd="tar -I lbzip2 -xpf "+self.settings["source_path"]+" -C "+\
					self.settings["chroot_path"]
			else:
				unpack_cmd="tar -I lbzip2 -xpf "+self.settings["source_path"]+" -C "+\
					self.settings["chroot_path"]
			error_msg="Tarball extraction of "+self.settings["source_path"]+\
				" to "+self.settings["chroot_path"]+" failed."

		if "AUTORESUME" in self.settings:
			if os.path.isdir(self.settings["source_path"]) \
				and os.path.exists(unpack_resume):
				""" Autoresume is valid, SEEDCACHE is valid """
				unpack=False
				invalid_snapshot=False

			elif os.path.isfile(self.settings["source_path"]) \
				and self.settings["source_path_hash"]==clst_unpack_hash:
				""" Autoresume is valid, tarball is valid """
				unpack=False
				invalid_snapshot=True

			elif os.path.isdir(self.settings["source_path"]) \
				and not os.path.exists(unpack_resume):
				""" Autoresume is invalid, SEEDCACHE """
				unpack=True
				invalid_snapshot=False

			elif os.path.isfile(self.settings["source_path"]) \
				and self.settings["source_path_hash"]!=clst_unpack_hash:
				""" Autoresume is invalid, tarball """
				unpack=True
				invalid_snapshot=True
		else:
			""" No autoresume, SEEDCACHE """
			if "SEEDCACHE" in self.settings:
				""" SEEDCACHE so let's run rsync and let it clean up """
				if os.path.isdir(self.settings["source_path"]):
					unpack=True
					invalid_snapshot=False
				elif os.path.isfile(self.settings["source_path"]):
					""" Tarball so unpack and remove anything already there """
					unpack=True
					invalid_snapshot=True
				""" No autoresume, no SEEDCACHE """
			else:
				""" Tarball so unpack and remove anything already there """
				if os.path.isfile(self.settings["source_path"]):
					unpack=True
					invalid_snapshot=True
				elif os.path.isdir(self.settings["source_path"]):
					""" We should never reach this, so something is very wrong """
					raise CatalystError,\
						"source path is a dir but seedcache is not enabled"

		if unpack:
			self.mount_safety_check()

			if invalid_snapshot:
				if "AUTORESUME" in self.settings:
					print "No Valid Resume point detected, cleaning up..."

				self.clear_autoresume()
				self.clear_chroot()

			if not os.path.exists(self.settings["chroot_path"]):
				os.makedirs(self.settings["chroot_path"])

			if not os.path.exists(self.settings["chroot_path"]+"/tmp"):
				os.makedirs(self.settings["chroot_path"]+"/tmp",1777)

			if "PKGCACHE" in self.settings:
				if not os.path.exists(self.settings["pkgcache_path"]):
					os.makedirs(self.settings["pkgcache_path"],0755)

			if "KERNCACHE" in self.settings:
				if not os.path.exists(self.settings["kerncache_path"]):
					os.makedirs(self.settings["kerncache_path"],0755)

			print display_msg
			cmd(unpack_cmd,error_msg,env=self.env)

			if "source_path_hash" in self.settings:
				myf=open(unpack_resume,"w")
				myf.write(self.settings["source_path_hash"])
				myf.close()
			else:
				touch(unpack_resume)
		else:
			print "Resume point detected, skipping unpack operation..."

	def unpack_snapshot(self):
		unpack=True
		unpack_portage_resume = pjoin(self.settings["autoresume_path"],
			"unpack_portage")
		snapshot_hash=read_from_clst(unpack_portage_resume)

		if "SNAPCACHE" in self.settings:
			snapshot_cache_hash=\
				read_from_clst(self.settings["snapshot_cache_path"] + "/" +
					"catalyst-hash")
			destdir=self.settings["snapshot_cache_path"]
			if "bz2" == self.settings["chroot_path"][-3:]:
				unpack_cmd="tar -I lbzip2 -xpf "+self.settings["snapshot_path"]+" -C "+destdir
			else:
				unpack_cmd="tar xpf "+self.settings["snapshot_path"]+" -C "+destdir
			unpack_errmsg="Error unpacking snapshot"
			cleanup_msg="Cleaning up invalid snapshot cache at \n\t"+\
				self.settings["snapshot_cache_path"]+\
				" (This can take a long time)..."
			cleanup_errmsg="Error removing existing snapshot cache directory."
			self.snapshot_lock_object=self.snapcache_lock

			if self.settings["snapshot_path_hash"]==snapshot_cache_hash:
				print "Valid snapshot cache, skipping unpack of portage tree..."
				unpack=False
		else:
			destdir = normpath(self.settings["chroot_path"] + self.settings["portdir"])
			cleanup_errmsg="Error removing existing snapshot directory."
			cleanup_msg=\
				"Cleaning up existing portage tree (This can take a long time)..."
			if "bz2" == self.settings["chroot_path"][-3:]:
				unpack_cmd="tar -I lbzip2 -xpf "+self.settings["snapshot_path"]+" -C "+\
					self.settings["chroot_path"]+"/usr"
			else:
				unpack_cmd="tar xpf "+self.settings["snapshot_path"]+" -C "+\
					self.settings["chroot_path"]+"/usr"
			unpack_errmsg="Error unpacking snapshot"

			if "AUTORESUME" in self.settings \
				and os.path.exists(self.settings["chroot_path"]+\
					self.settings["portdir"]) \
				and os.path.exists(unpack_portage_resume) \
				and self.settings["snapshot_path_hash"] == snapshot_hash:
					print \
						"Valid Resume point detected, skipping unpack of portage tree..."
					unpack=False

		if unpack:
			if "SNAPCACHE" in self.settings:
				self.snapshot_lock_object.write_lock()
			if os.path.exists(destdir):
				print cleanup_msg
				cleanup_cmd="rm -rf "+destdir
				cmd(cleanup_cmd,cleanup_errmsg,env=self.env)
			if not os.path.exists(destdir):
				os.makedirs(destdir,0755)

			print "Unpacking portage tree (This can take a long time) ..."
			cmd(unpack_cmd,unpack_errmsg,env=self.env)

			if "SNAPCACHE" in self.settings:
				myf=open(self.settings["snapshot_cache_path"] +
					"/" + "catalyst-hash","w")
				myf.write(self.settings["snapshot_path_hash"])
				myf.close()
			else:
				print "Setting snapshot autoresume point"
				myf=open(unpack_portage_resume,"w")
				myf.write(self.settings["snapshot_path_hash"])
				myf.close()

			if "SNAPCACHE" in self.settings:
				self.snapshot_lock_object.unlock()

	def config_profile_link(self):
		config_protect_link_resume = pjoin(self.settings["autoresume_path"],
			"config_profile_link")
		if "AUTORESUME" in self.settings \
			and os.path.exists(config_protect_link_resume):
			print \
				"Resume point detected, skipping config_profile_link operation..."
		else:
			# TODO: zmedico and I discussed making this a directory and pushing
			# in a parent file, as well as other user-specified configuration.
			print "Configuring profile link..."
			cmd("rm -f "+self.settings["chroot_path"]+"/etc/portage/make.profile",\
					"Error zapping profile link",env=self.env)
			cmd("mkdir -p "+self.settings["chroot_path"]+"/etc/portage/")
			cmd("ln -sf ../.." + self.settings["portdir"] + "/profiles/" + \
				self.settings["target_profile"]+" "+\
				self.settings["chroot_path"]+"/etc/portage/make.profile",\
				"Error creating profile link",env=self.env)
			touch(config_protect_link_resume)

	def setup_confdir(self):
		setup_confdir_resume = pjoin(self.settings["autoresume_path"],
			"setup_confdir")
		if "AUTORESUME" in self.settings \
			and os.path.exists(setup_confdir_resume):
			print "Resume point detected, skipping setup_confdir operation..."
		else:
			if "portage_confdir" in self.settings:
				print "Configuring /etc/portage..."
				cmd("rsync -a "+self.settings["portage_confdir"]+"/ "+\
					self.settings["chroot_path"]+"/etc/portage/",\
					"Error copying /etc/portage",env=self.env)
				touch(setup_confdir_resume)

	def portage_overlay(self):
		""" We copy the contents of our overlays to /usr/local/portage """
		if "portage_overlay" in self.settings:
			for x in self.settings["portage_overlay"]:
				if os.path.exists(x):
					print "Copying overlay dir " +x
					cmd("mkdir -p "+self.settings["chroot_path"]+\
						self.settings["local_overlay"],\
						"Could not make portage_overlay dir",env=self.env)
					cmd("cp -R "+x+"/* "+self.settings["chroot_path"]+\
						self.settings["local_overlay"],\
						"Could not copy portage_overlay",env=self.env)

	def root_overlay(self):
		""" Copy over the root_overlay """
		if self.settings["spec_prefix"]+"/root_overlay" in self.settings:
			for x in self.settings[self.settings["spec_prefix"]+\
				"/root_overlay"]:
				if os.path.exists(x):
					print "Copying root_overlay: "+x
					cmd("rsync -a "+x+"/ "+\
						self.settings["chroot_path"],\
						self.settings["spec_prefix"]+"/root_overlay: "+x+\
						" copy failed.",env=self.env)

	def base_dirs(self):
		pass

	def bind(self):
		for x in self.mounts:
			#print "bind(); x =", x
			target = normpath(self.settings["chroot_path"] + self.target_mounts[x])
			if not os.path.exists(target):
				os.makedirs(target, 0755)

			if not os.path.exists(self.mountmap[x]):
				if self.mountmap[x] not in ["tmpfs", "shmfs"]:
					os.makedirs(self.mountmap[x], 0755)

			src=self.mountmap[x]
			#print "bind(); src =", src
			if "SNAPCACHE" in self.settings and x == "portdir":
				self.snapshot_lock_object.read_lock()
			if os.uname()[0] == "FreeBSD":
				if src == "/dev":
					cmd = "mount -t devfs none " + target
					retval=os.system(cmd)
				else:
					cmd = "mount_nullfs " + src + " " + target
					retval=os.system(cmd)
			else:
				if src == "tmpfs":
					if "var_tmpfs_portage" in self.settings:
						cmd = "mount -t tmpfs -o size=" + \
							self.settings["var_tmpfs_portage"] + "G " + \
							src + " " + target
						retval=os.system(cmd)
				elif src == "shmfs":
					cmd = "mount -t tmpfs -o noexec,nosuid,nodev shm " + target
					retval=os.system(cmd)
				else:
					cmd = "mount --bind " + src + " " + target
					#print "bind(); cmd =", cmd
					retval=os.system(cmd)
			if retval!=0:
				self.unbind()
				raise CatalystError,"Couldn't bind mount " + src

	def unbind(self):
		ouch=0
		mypath=self.settings["chroot_path"]
		myrevmounts=self.mounts[:]
		myrevmounts.reverse()
		""" Unmount in reverse order for nested bind-mounts """
		for x in myrevmounts:
			target = normpath(mypath + self.target_mounts[x])
			if not os.path.exists(target):
				continue

			if not ismount(target):
				continue

			retval=os.system("umount " + target)

			if retval!=0:
				warn("First attempt to unmount: " + target + " failed.")
				warn("Killing any pids still running in the chroot")

				self.kill_chroot_pids()

				retval2 = os.system("umount " + target)
				if retval2!=0:
					ouch=1
					warn("Couldn't umount bind mount: " + target)

			if "SNAPCACHE" in self.settings and x == "/usr/portage":
				try:
					"""
					It's possible the snapshot lock object isn't created yet.
					This is because mount safety check calls unbind before the
					target is fully initialized
					"""
					self.snapshot_lock_object.unlock()
				except:
					pass
		if ouch:
			"""
			if any bind mounts really failed, then we need to raise
			this to potentially prevent an upcoming bash stage cleanup script
			from wiping our bind mounts.
			"""
			raise CatalystError,\
				"Couldn't umount one or more bind-mounts; aborting for safety."

	def chroot_setup(self):
		self.makeconf=read_makeconf(self.settings["chroot_path"]+\
			"/etc/portage/make.conf")
		self.override_cbuild()
		self.override_chost()
		self.override_cflags()
		self.override_cxxflags()
		self.override_ldflags()
		chroot_setup_resume = pjoin(self.settings["autoresume_path"],
			"chroot_setup")
		if "AUTORESUME" in self.settings and os.path.exists(chroot_setup_resume):
			print "Resume point detected, skipping chroot_setup operation..."
		else:
			print "Setting up chroot..."

			#self.makeconf=read_makeconf(self.settings["chroot_path"]+"/etc/portage/make.conf")

			cmd("cp /etc/resolv.conf " + self.settings["chroot_path"] + "/etc/",
				"Could not copy resolv.conf into place.",env=self.env)

			""" Copy over the envscript, if applicable """
			if "ENVSCRIPT" in self.settings:
				if not os.path.exists(self.settings["ENVSCRIPT"]):
					raise CatalystError,\
						"Can't find envscript "+self.settings["ENVSCRIPT"]

				print "\nWarning!!!!"
				print "\tOverriding certain env variables may cause catastrophic failure."
				print "\tIf your build fails look here first as the possible problem."
				print "\tCatalyst assumes you know what you are doing when setting"
				print "\t\tthese variables."
				print "\tCatalyst Maintainers use VERY minimal envscripts if used at all"
				print "\tYou have been warned\n"

				cmd("cp "+self.settings["ENVSCRIPT"]+" "+\
					self.settings["chroot_path"]+"/tmp/envscript",\
					"Could not copy envscript into place.",env=self.env)

			"""
			Copy over /etc/hosts from the host in case there are any
			specialties in there
			"""
			if os.path.exists(self.settings["chroot_path"]+"/etc/hosts"):
				cmd("mv "+self.settings["chroot_path"]+"/etc/hosts "+\
					self.settings["chroot_path"]+"/etc/hosts.catalyst",\
					"Could not backup /etc/hosts",env=self.env)
				cmd("cp /etc/hosts "+self.settings["chroot_path"]+"/etc/hosts",\
					"Could not copy /etc/hosts",env=self.env)

			""" Modify and write out make.conf (for the chroot) """
			cmd("rm -f "+self.settings["chroot_path"]+"/etc/portage/make.conf",\
				"Could not remove "+self.settings["chroot_path"]+\
				"/etc/portage/make.conf",env=self.env)
			myf=open(self.settings["chroot_path"]+"/etc/portage/make.conf","w")
			myf.write("# These settings were set by the catalyst build script that automatically\n# built this stage.\n")
			myf.write("# Please consult /usr/share/portage/config/make.conf.example for a more\n# detailed example.\n")
			if "CFLAGS" in self.settings:
				myf.write('CFLAGS="'+self.settings["CFLAGS"]+'"\n')
			if "CXXFLAGS" in self.settings:
				if self.settings["CXXFLAGS"]!=self.settings["CFLAGS"]:
					myf.write('CXXFLAGS="'+self.settings["CXXFLAGS"]+'"\n')
				else:
					myf.write('CXXFLAGS="${CFLAGS}"\n')
			else:
				myf.write('CXXFLAGS="${CFLAGS}"\n')

			if "LDFLAGS" in self.settings:
				myf.write("# LDFLAGS is unsupported.  USE AT YOUR OWN RISK!\n")
				myf.write('LDFLAGS="'+self.settings["LDFLAGS"]+'"\n')
			if "CBUILD" in self.settings:
				myf.write("# This should not be changed unless you know exactly what you are doing.  You\n# should probably be using a different stage, instead.\n")
				myf.write('CBUILD="'+self.settings["CBUILD"]+'"\n')

			myf.write("# WARNING: Changing your CHOST is not something that should be done lightly.\n# Please consult http://www.gentoo.org/doc/en/change-chost.xml before changing.\n")
			myf.write('CHOST="'+self.settings["CHOST"]+'"\n')

			""" Figure out what our USE vars are for building """
			myusevars=[]
			if "HOSTUSE" in self.settings:
				myusevars.extend(self.settings["HOSTUSE"])

			if "use" in self.settings:
				myusevars.extend(self.settings["use"])

			if myusevars:
				myf.write("# These are the USE flags that were used in addition to what is provided by the\n# profile used for building.\n")
				myusevars = sorted(set(myusevars))
				myf.write('USE="'+string.join(myusevars)+'"\n')
				if '-*' in myusevars:
					print "\nWarning!!!  "
					print "\tThe use of -* in "+self.settings["spec_prefix"]+\
						"/use will cause portage to ignore"
					print "\tpackage.use in the profile and portage_confdir. You've been warned!"

			myf.write('PORTDIR="%s"\n' % self.settings['portdir'])
			myf.write('DISTDIR="%s"\n' % self.settings['distdir'])
			myf.write('PKGDIR="%s"\n' % self.settings['packagedir'])

			""" Setup the portage overlay """
			if "portage_overlay" in self.settings:
				myf.write('PORTDIR_OVERLAY="/usr/local/portage"\n')

			myf.close()
			cmd("cp "+self.settings["chroot_path"]+"/etc/portage/make.conf "+\
				self.settings["chroot_path"]+"/etc/portage/make.conf.catalyst",\
				"Could not backup /etc/portage/make.conf",env=self.env)
			touch(chroot_setup_resume)

	def fsscript(self):
		fsscript_resume = pjoin(self.settings["autoresume_path"], "fsscript")
		if "AUTORESUME" in self.settings and os.path.exists(fsscript_resume):
			print "Resume point detected, skipping fsscript operation..."
		else:
			if "fsscript" in self.settings:
				if os.path.exists(self.settings["controller_file"]):
					cmd("/bin/bash "+self.settings["controller_file"]+\
						" fsscript","fsscript script failed.",env=self.env)
					touch(fsscript_resume)

	def rcupdate(self):
		rcupdate_resume = pjoin(self.settings["autoresume_path"], "rcupdate")
		if "AUTORESUME" in self.settings \
			and os.path.exists(rcupdate_resume):
			print "Resume point detected, skipping rcupdate operation..."
		else:
			if os.path.exists(self.settings["controller_file"]):
				cmd("/bin/bash "+self.settings["controller_file"]+" rc-update",\
					"rc-update script failed.",env=self.env)
				touch(rcupdate_resume)

	def clean(self):
		clean_resume = pjoin(self.settings["autoresume_path"], "clean")
		if "AUTORESUME" in self.settings \
			and os.path.exists(clean_resume):
			print "Resume point detected, skipping clean operation..."
		else:
			for x in self.settings["cleanables"]:
				print "Cleaning chroot: "+x+"... "
				cmd("rm -rf "+self.settings["destpath"]+x,"Couldn't clean "+\
					x,env=self.env)

		""" Put /etc/hosts back into place """
		if os.path.exists(self.settings["chroot_path"]+"/etc/hosts.catalyst"):
			cmd("mv -f "+self.settings["chroot_path"]+"/etc/hosts.catalyst "+\
				self.settings["chroot_path"]+"/etc/hosts",\
				"Could not replace /etc/hosts",env=self.env)

		""" Remove our overlay """
		if os.path.exists(self.settings["chroot_path"] + self.settings["local_overlay"]):
			cmd("rm -rf " + self.settings["chroot_path"] + self.settings["local_overlay"],
				"Could not remove " + self.settings["local_overlay"], env=self.env)
			cmd("sed -i '/^PORTDIR_OVERLAY/d' "+self.settings["chroot_path"]+\
				"/etc/portage/make.conf",\
				"Could not remove PORTDIR_OVERLAY from make.conf",env=self.env)

		""" Clean up old and obsoleted files in /etc """
		if os.path.exists(self.settings["stage_path"]+"/etc"):
			cmd("find "+self.settings["stage_path"]+\
				"/etc -maxdepth 1 -name \"*-\" | xargs rm -f",\
				"Could not remove stray files in /etc",env=self.env)

		if os.path.exists(self.settings["controller_file"]):
			cmd("/bin/bash "+self.settings["controller_file"]+" clean",\
				"clean script failed.",env=self.env)
			touch(clean_resume)

	def empty(self):
		empty_resume = pjoin(self.settings["autoresume_path"], "empty")
		if "AUTORESUME" in self.settings and os.path.exists(empty_resume):
			print "Resume point detected, skipping empty operation..."
		else:
			if self.settings["spec_prefix"]+"/empty" in self.settings:
				if type(self.settings[self.settings["spec_prefix"]+\
					"/empty"])==types.StringType:
					self.settings[self.settings["spec_prefix"]+"/empty"]=\
						self.settings[self.settings["spec_prefix"]+\
						"/empty"].split()
				for x in self.settings[self.settings["spec_prefix"]+"/empty"]:
					myemp=self.settings["destpath"]+x
					if not os.path.isdir(myemp) or os.path.islink(myemp):
						print x,"not a directory or does not exist, skipping 'empty' operation."
						continue
					print "Emptying directory",x
					"""
					stat the dir, delete the dir, recreate the dir and set
					the proper perms and ownership
					"""
					mystat=os.stat(myemp)
					shutil.rmtree(myemp)
					os.makedirs(myemp,0755)
					os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
					os.chmod(myemp,mystat[ST_MODE])
			touch(empty_resume)

	def remove(self):
		remove_resume = pjoin(self.settings["autoresume_path"], "remove")
		if "AUTORESUME" in self.settings and os.path.exists(remove_resume):
			print "Resume point detected, skipping remove operation..."
		else:
			if self.settings["spec_prefix"]+"/rm" in self.settings:
				for x in self.settings[self.settings["spec_prefix"]+"/rm"]:
					"""
					We're going to shell out for all these cleaning
					operations, so we get easy glob handling.
					"""
					print "livecd: removing "+x
					os.system("rm -rf "+self.settings["chroot_path"]+x)
				try:
					if os.path.exists(self.settings["controller_file"]):
						cmd("/bin/bash "+self.settings["controller_file"]+\
							" clean","Clean  failed.",env=self.env)
						touch(remove_resume)
				except:
					self.unbind()
					raise

	def preclean(self):
		preclean_resume = pjoin(self.settings["autoresume_path"], "preclean")
		if "AUTORESUME" in self.settings and os.path.exists(preclean_resume):
			print "Resume point detected, skipping preclean operation..."
		else:
			try:
				if os.path.exists(self.settings["controller_file"]):
					cmd("/bin/bash "+self.settings["controller_file"]+\
						" preclean","preclean script failed.",env=self.env)
					touch(preclean_resume)

			except:
				self.unbind()
				raise CatalystError, "Build failed, could not execute preclean"

	def capture(self):
		capture_resume = pjoin(self.settings["autoresume_path"], "capture")
		if "AUTORESUME" in self.settings and os.path.exists(capture_resume):
			print "Resume point detected, skipping capture operation..."
		else:
			""" Capture target in a tarball """
			mypath=self.settings["target_path"].split("/")
			""" Remove filename from path """
			mypath=string.join(mypath[:-1],"/")

			""" Now make sure path exists """
			if not os.path.exists(mypath):
				os.makedirs(mypath)

			print "Creating stage tarball..."

			cmd("tar -I lbzip2 -cpf "+self.settings["target_path"]+" -C "+\
				self.settings["stage_path"]+" .",\
				"Couldn't create stage tarball",env=self.env)

			self.gen_contents_file(self.settings["target_path"])
			self.gen_digest_file(self.settings["target_path"])

			touch(capture_resume)

	def run_local(self):
		run_local_resume = pjoin(self.settings["autoresume_path"], "run_local")
		if "AUTORESUME" in self.settings and os.path.exists(run_local_resume):
			print "Resume point detected, skipping run_local operation..."
		else:
			try:
				if os.path.exists(self.settings["controller_file"]):
					cmd("/bin/bash "+self.settings["controller_file"]+" run",\
						"run script failed.",env=self.env)
					touch(run_local_resume)

			except CatalystError:
				self.unbind()
				raise CatalystError,"Stage build aborting due to error."

	def setup_environment(self):
		"""
		Modify the current environment. This is an ugly hack that should be
		fixed. We need this to use the os.system() call since we can't
		specify our own environ
		"""
		for x in self.settings.keys():
			""" Sanitize var names by doing "s|/-.|_|g" """
			varname="clst_"+string.replace(x,"/","_")
			varname=string.replace(varname,"-","_")
			varname=string.replace(varname,".","_")
			if type(self.settings[x])==types.StringType:
				""" Prefix to prevent namespace clashes """
				#os.environ[varname]=self.settings[x]
				self.env[varname]=self.settings[x]
			elif type(self.settings[x])==types.ListType:
				#os.environ[varname]=string.join(self.settings[x])
				self.env[varname]=string.join(self.settings[x])
			elif type(self.settings[x])==types.BooleanType:
				if self.settings[x]:
					self.env[varname]="true"
				else:
					self.env[varname]="false"
		if "makeopts" in self.settings:
			self.env["MAKEOPTS"]=self.settings["makeopts"]

	def run(self):
		self.chroot_lock.write_lock()

		""" Kill any pids in the chroot "" """
		self.kill_chroot_pids()

		""" Check for mounts right away and abort if we cannot unmount them """
		self.mount_safety_check()

		if "CLEAR_AUTORESUME" in self.settings:
			self.clear_autoresume()

		if "PURGETMPONLY" in self.settings:
			self.purge()
			return

		if "PURGEONLY" in self.settings:
			self.purge()
			return

		if "PURGE" in self.settings:
			self.purge()

		for x in self.settings["action_sequence"]:
			print "--- Running action sequence: "+x
			sys.stdout.flush()
			try:
				apply(getattr(self,x))
			except:
				self.mount_safety_check()
				raise

		self.chroot_lock.unlock()

	def unmerge(self):
		unmerge_resume = pjoin(self.settings["autoresume_path"], "unmerge")
		if "AUTORESUME" in self.settings and os.path.exists(unmerge_resume):
			print "Resume point detected, skipping unmerge operation..."
		else:
			if self.settings["spec_prefix"]+"/unmerge" in self.settings:
				if type(self.settings[self.settings["spec_prefix"]+\
					"/unmerge"])==types.StringType:
					self.settings[self.settings["spec_prefix"]+"/unmerge"]=\
						[self.settings[self.settings["spec_prefix"]+"/unmerge"]]
				myunmerge=\
					self.settings[self.settings["spec_prefix"]+"/unmerge"][:]

				for x in range(0,len(myunmerge)):
					"""
					Surround args with quotes for passing to bash, allows
					things like "<" to remain intact
					"""
					myunmerge[x]="'"+myunmerge[x]+"'"
				myunmerge=string.join(myunmerge)

				""" Before cleaning, unmerge stuff """
				try:
					cmd("/bin/bash "+self.settings["controller_file"]+\
						" unmerge "+ myunmerge,"Unmerge script failed.",\
						env=self.env)
					print "unmerge shell script"
				except CatalystError:
					self.unbind()
					raise
				touch(unmerge_resume)

	def target_setup(self):
		target_setup_resume = pjoin(self.settings["autoresume_path"],
			"target_setup")
		if "AUTORESUME" in self.settings and os.path.exists(target_setup_resume):
			print "Resume point detected, skipping target_setup operation..."
		else:
			print "Setting up filesystems per filesystem type"
			cmd("/bin/bash "+self.settings["controller_file"]+\
				" target_image_setup "+ self.settings["target_path"],\
				"target_image_setup script failed.",env=self.env)
			touch(target_setup_resume)

	def setup_overlay(self):
		setup_overlay_resume = pjoin(self.settings["autoresume_path"],
			"setup_overlay")
		if "AUTORESUME" in self.settings and \
				os.path.exists(setup_overlay_resume):
			print "Resume point detected, skipping setup_overlay operation..."
		else:
			if self.settings["spec_prefix"]+"/overlay" in self.settings:
				for x in self.settings[self.settings["spec_prefix"]+"/overlay"]:
					if os.path.exists(x):
						cmd("rsync -a "+x+"/ "+\
							self.settings["target_path"],\
							self.settings["spec_prefix"]+"overlay: "+x+\
							" copy failed.",env=self.env)
				touch(setup_overlay_resume)

	def create_iso(self):
		create_iso_resume = pjoin(self.settings["autoresume_path"], "create_iso")
		if "AUTORESUME" in self.settings and os.path.exists(create_iso_resume):
			print "Resume point detected, skipping create_iso operation..."
		else:
			""" Create the ISO """
			if "iso" in self.settings:
				cmd("/bin/bash "+self.settings["controller_file"]+" iso "+\
					self.settings["iso"],"ISO creation script failed.",\
					env=self.env)
				self.gen_contents_file(self.settings["iso"])
				self.gen_digest_file(self.settings["iso"])
				touch(create_iso_resume)
			else:
				print "WARNING: livecd/iso was not defined."
				print "An ISO Image will not be created."

	def build_packages(self):
		build_packages_resume = pjoin(self.settings["autoresume_path"],
			"build_packages")
		if "AUTORESUME" in self.settings and \
				os.path.exists(build_packages_resume):
			print "Resume point detected, skipping build_packages operation..."
		else:
			if self.settings["spec_prefix"]+"/packages" in self.settings:
				if "AUTORESUME" in self.settings \
					and os.path.exists(self.settings["autoresume_path"]+\
						"build_packages"):
					print "Resume point detected, skipping build_packages operation..."
				else:
					mypack=\
						list_bashify(self.settings[self.settings["spec_prefix"]\
						+"/packages"])
					try:
						cmd("/bin/bash "+self.settings["controller_file"]+\
							" build_packages "+mypack,\
							"Error in attempt to build packages",env=self.env)
						touch(build_packages_resume)
					except CatalystError:
						self.unbind()
						raise CatalystError,self.settings["spec_prefix"]+\
							"build aborting due to error."

	def build_kernel(self):
		"Build all configured kernels"
		build_kernel_resume = pjoin(self.settings["autoresume_path"],
			"build_kernel")
		if "AUTORESUME" in self.settings and os.path.exists(build_kernel_resume):
			print "Resume point detected, skipping build_kernel operation..."
		else:
			if "boot/kernel" in self.settings:
				try:
					mynames=self.settings["boot/kernel"]
					if type(mynames)==types.StringType:
						mynames=[mynames]
					"""
					Execute the script that sets up the kernel build environment
					"""
					cmd("/bin/bash "+self.settings["controller_file"]+\
						" pre-kmerge ","Runscript pre-kmerge failed",\
						env=self.env)
					for kname in mynames:
						self._build_kernel(kname=kname)
					touch(build_kernel_resume)
				except CatalystError:
					self.unbind()
					raise CatalystError,\
						"build aborting due to kernel build error."

	def _build_kernel(self, kname):
		"Build a single configured kernel by name"
		kname_resume = pjoin(self.settings["autoresume_path"],
			"build_kernel_" + kname)
		if "AUTORESUME" in self.settings and os.path.exists(kname_resume):
			print "Resume point detected, skipping build_kernel for "+kname+" operation..."
			return
		self._copy_kernel_config(kname=kname)

		"""
		If we need to pass special options to the bootloader
		for this kernel put them into the environment
		"""
		if "boot/kernel/"+kname+"/kernelopts" in self.settings:
			myopts=self.settings["boot/kernel/"+kname+\
				"/kernelopts"]

			if type(myopts) != types.StringType:
				myopts = string.join(myopts)
				self.env[kname+"_kernelopts"]=myopts

			else:
				self.env[kname+"_kernelopts"]=""

		if "boot/kernel/"+kname+"/extraversion" not in self.settings:
			self.settings["boot/kernel/"+kname+\
				"/extraversion"]=""

		self.env["clst_kextraversion"]=\
			self.settings["boot/kernel/"+kname+\
			"/extraversion"]

		self._copy_initramfs_overlay(kname=kname)

		""" Execute the script that builds the kernel """
		cmd("/bin/bash "+self.settings["controller_file"]+\
			" kernel "+kname,\
			"Runscript kernel build failed",env=self.env)

		if "boot/kernel/"+kname+"/initramfs_overlay" in self.settings:
			if os.path.exists(self.settings["chroot_path"]+\
				"/tmp/initramfs_overlay/"):
				print "Cleaning up temporary overlay dir"
				cmd("rm -R "+self.settings["chroot_path"]+\
					"/tmp/initramfs_overlay/",env=self.env)

		touch(kname_resume)

		"""
		Execute the script that cleans up the kernel build
		environment
		"""
		cmd("/bin/bash "+self.settings["controller_file"]+\
			" post-kmerge ",
			"Runscript post-kmerge failed",env=self.env)

	def _copy_kernel_config(self, kname):
		if "boot/kernel/"+kname+"/config" in self.settings:
			if not os.path.exists(self.settings["boot/kernel/"+kname+"/config"]):
				self.unbind()
				raise CatalystError,\
					"Can't find kernel config: "+\
					self.settings["boot/kernel/"+kname+\
					"/config"]

			try:
				cmd("cp "+self.settings["boot/kernel/"+kname+\
					"/config"]+" "+\
					self.settings["chroot_path"]+"/var/tmp/"+\
					kname+".config",\
					"Couldn't copy kernel config: "+\
					self.settings["boot/kernel/"+kname+\
					"/config"],env=self.env)

			except CatalystError:
				self.unbind()

	def _copy_initramfs_overlay(self, kname):
		if "boot/kernel/"+kname+"/initramfs_overlay" in self.settings:
			if os.path.exists(self.settings["boot/kernel/"+\
				kname+"/initramfs_overlay"]):
				print "Copying initramfs_overlay dir "+\
					self.settings["boot/kernel/"+kname+\
					"/initramfs_overlay"]

				cmd("mkdir -p "+\
					self.settings["chroot_path"]+\
					"/tmp/initramfs_overlay/"+\
					self.settings["boot/kernel/"+kname+\
					"/initramfs_overlay"],env=self.env)

				cmd("cp -R "+self.settings["boot/kernel/"+\
					kname+"/initramfs_overlay"]+"/* "+\
					self.settings["chroot_path"]+\
					"/tmp/initramfs_overlay/"+\
					self.settings["boot/kernel/"+kname+\
					"/initramfs_overlay"],env=self.env)

	def bootloader(self):
		bootloader_resume = pjoin(self.settings["autoresume_path"], "bootloader")
		if "AUTORESUME" in self.settings and os.path.exists(bootloader_resume):
			print "Resume point detected, skipping bootloader operation..."
		else:
			try:
				cmd("/bin/bash "+self.settings["controller_file"]+\
					" bootloader " + self.settings["target_path"],\
					"Bootloader script failed.",env=self.env)
				touch(bootloader_resume)
			except CatalystError:
				self.unbind()
				raise CatalystError,"Script aborting due to error."

	def livecd_update(self):
		livecd_update_resume = pjoin(self.settings["autoresume_path"],
			"livecd_update")
		if "AUTORESUME" in self.settings \
			and os.path.exists(livecd_update_resume):
			print "Resume point detected, skipping build_packages operation..."
		else:
			try:
				cmd("/bin/bash "+self.settings["controller_file"]+\
					" livecd-update","livecd-update failed.",env=self.env)
				touch(livecd_update_resume)

			except CatalystError:
				self.unbind()
				raise CatalystError,"build aborting due to livecd_update error."

	def clear_chroot(self):
		myemp=self.settings["chroot_path"]
		if os.path.isdir(myemp):
			print "Emptying directory",myemp
			"""
			stat the dir, delete the dir, recreate the dir and set
			the proper perms and ownership
			"""
			mystat=os.stat(myemp)
			#cmd("rm -rf "+myemp, "Could not remove existing file: "+myemp,env=self.env)
			""" There's no easy way to change flags recursively in python """
			if os.uname()[0] == "FreeBSD":
				os.system("chflags -R noschg "+myemp)
			shutil.rmtree(myemp)
			os.makedirs(myemp,0755)
			os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
			os.chmod(myemp,mystat[ST_MODE])

	def clear_packages(self):
		if "PKGCACHE" in self.settings:
			print "purging the pkgcache ..."

			myemp=self.settings["pkgcache_path"]
			if os.path.isdir(myemp):
				print "Emptying directory",myemp
				"""
				stat the dir, delete the dir, recreate the dir and set
				the proper perms and ownership
				"""
				mystat=os.stat(myemp)
				#cmd("rm -rf "+myemp, "Could not remove existing file: "+myemp,env=self.env)
				shutil.rmtree(myemp)
				os.makedirs(myemp,0755)
				os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
				os.chmod(myemp,mystat[ST_MODE])

	def clear_kerncache(self):
		if "KERNCACHE" in self.settings:
			print "purging the kerncache ..."

			myemp=self.settings["kerncache_path"]
			if os.path.isdir(myemp):
				print "Emptying directory",myemp
				"""
				stat the dir, delete the dir, recreate the dir and set
				the proper perms and ownership
				"""
				mystat=os.stat(myemp)
				#cmd("rm -rf "+myemp, "Could not remove existing file: "+myemp,env=self.env)
				shutil.rmtree(myemp)
				os.makedirs(myemp,0755)
				os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
				os.chmod(myemp,mystat[ST_MODE])

	def clear_autoresume(self):
		""" Clean resume points since they are no longer needed """
		if "AUTORESUME" in self.settings:
			print "Removing AutoResume Points: ..."
		myemp=self.settings["autoresume_path"]
		if os.path.isdir(myemp):
				if "AUTORESUME" in self.settings:
					print "Emptying directory",myemp
				"""
				stat the dir, delete the dir, recreate the dir and set
				the proper perms and ownership
				"""
				mystat=os.stat(myemp)
				if os.uname()[0] == "FreeBSD":
					cmd("chflags -R noschg "+myemp,\
						"Could not remove immutable flag for file "\
						+myemp)
				#cmd("rm -rf "+myemp, "Could not remove existing file: "+myemp,env-self.env)
				shutil.rmtree(myemp)
				os.makedirs(myemp,0755)
				os.chown(myemp,mystat[ST_UID],mystat[ST_GID])
				os.chmod(myemp,mystat[ST_MODE])

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
								hash = hash_map.generate_hash(f, hash_ = k,
									verbose = "VERBOSE" in self.settings)
								myf.write(hash)
						else:
							for j in array:
								hash = hash_map.generate_hash(f, hash_ = j,
									verbose = "VERBOSE" in self.settings)
								myf.write(hash)
				myf.close()

	def purge(self):
		countdown(10,"Purging Caches ...")
		if any(k in self.settings for k in ("PURGE","PURGEONLY","PURGETMPONLY")):
			print "clearing autoresume ..."
			self.clear_autoresume()

			print "clearing chroot ..."
			self.clear_chroot()

			if "PURGETMPONLY" not in self.settings:
				print "clearing package cache ..."
				self.clear_packages()

			print "clearing kerncache ..."
			self.clear_kerncache()

# vim: ts=4 sw=4 sta et sts=4 ai
