
"""
This class does all of the chroot setup, copying of files, etc. It is
the driver class for pretty much everything that Catalyst does.
"""

import os
import catalyst
from catalyst.output import *
from catalyst.spawn import cmd
from catalyst.error import *
from catalyst.target.generic import *

class generic_stage_target(generic_target):

	def __init__(self):
		generic_target.__init__(self)

		self.required_values.extend(["version_stamp","target","subarch",\
			"rel_type","profile","snapshot","source_subpath"])

		self.valid_values.extend(["version_stamp","target","subarch",\
			"rel_type","profile","snapshot","source_subpath","portage_confdir",\
			"cflags","cxxflags","ldflags","cbuild","hostuse","portage_overlay",\
			"distcc_hosts","makeopts","pkgcache_path","kerncache_path"])

		self.set_valid_build_kernel_vars()

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

		# XXX This should all be moved somewhere "higher" vvvvvvvvvvv
		self.subarchmap = {}
		machinemap = {}

		arches = catalyst.arch.get_arches()
		for x in arches:
			self.subarchmap.update(arches[x]._subarch_map)
			for machine in arches[x]._machine_map:
				machinemap[machine] = x
			for subarch in arches[x]._subarch_map:
				machinemap[subarch] = x

		if "chost" in self.settings:
			hostmachine = self.settings["chost"].split("-")[0]
			if not hostmachine in machinemap:
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
		if not buildmachine in machinemap:
			raise CatalystError, "Unknown build machine type "+buildmachine
		self.settings["buildarch"]=machinemap[buildmachine]
		self.settings["crosscompile"]=(self.settings["hostarch"]!=\
			self.settings["buildarch"])

		""" Call arch constructor, pass our settings """
		try:
			self.arch=self.subarchmap[self.settings["subarch"]](self.settings)
		except KeyError:
			msg("Invalid subarch: " + self.settings["subarch"])
			msg("Choose one of the following:")
			msg("\n".join(self.subarchmap.keys()))
			sys.exit(2)

		msg("Using target: " + self.settings["target"])
		""" Print a nice informational message """
		if self.settings["buildarch"]==self.settings["hostarch"]:
			msg("Building natively for " + self.settings["hostarch"])
		elif self.settings["crosscompile"]:
			msg("Cross-compiling on " + self.settings["buildarch"] + \
				"for different machine type " + self.settings["hostarch"])
		else:
			msg("Building on" + self.settings["buildarch"] + \
				"for alternate personality type " + self.settings["hostarch"])
		# XXX This should all be moved somewhere "higher" ^^^^^^^^^^^^^^

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
		self.set_install_mask()
		self.set_fstype()
		self.set_fsops()
		self.set_iso()
		self.set_packages()
		self.set_rm()
		self.set_overlay()
		self.set_portage_overlay()
		self.set_root_overlay()

		"""
		This next line checks to make sure that the specified variables exist
		on disk.
		"""
		#pdb.set_trace()
		catalyst.util.file_locate(self.settings,["source_path","snapshot_path","distdir"],\
			expand=0)
		""" If we are using portage_confdir, check that as well. """
		if "portage_confdir" in self.settings:
			catalyst.util.file_locate(self.settings,["portage_confdir"],expand=0)

		""" Setup our mount points """
		if "SNAPCACHE" in self.settings:
			self.mounts=["/proc","/dev","/usr/portage","/usr/portage/distfiles"]
			self.mountmap={"/proc":"/proc","/dev":"/dev","/dev/pts":"/dev/pts",\
				"/usr/portage":self.settings["snapshot_cache_path"]+"/portage",\
				"/usr/portage/distfiles":self.settings["distdir"]}
		else:
			self.mounts=["/proc","/dev","/usr/portage/distfiles"]
			self.mountmap={"/proc":"/proc","/dev":"/dev","/dev/pts":"/dev/pts",\
				"/usr/portage/distfiles":self.settings["distdir"]}
		if os.uname()[0] == "Linux":
			self.mounts.append("/dev/pts")

		self.set_mounts()

		"""
		Configure any user specified options (either in catalyst.conf or on
		the command line).
		"""
		if "PKGCACHE" in self.settings:
			self.set_pkgcache_path()
			msg("Location of the package cache is " + \
				self.settings["pkgcache_path"])
			self.mounts.append("/usr/portage/packages")
			self.mountmap["/usr/portage/packages"]=\
				self.settings["pkgcache_path"]

		if "KERNCACHE" in self.settings:
			self.set_kerncache_path()
			msg("Location of the kerncache is " + \
				self.settings["kerncache_path"])
			self.mounts.append("/tmp/kerncache")
			self.mountmap["/tmp/kerncache"]=self.settings["kerncache_path"]

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
			self.mounts.append("/var/tmp/ccache")
			self.mountmap["/var/tmp/ccache"]=ccdir
			""" for the chroot: """
			self.env["CCACHE_DIR"]="/var/tmp/ccache"

		if "ICECREAM" in self.settings:
			self.mounts.append("/var/cache/icecream")
			self.mountmap["/var/cache/icecream"]="/var/cache/icecream"
			self.env["PATH"]="/usr/lib/icecc/bin:"+self.env["PATH"]

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
			if not isinstance(self.settings["install_mask"], str):
				self.settings["install_mask"]=\
					" ".join(self.settings["install_mask"])

	def set_target_profile(self):
		self.settings["target_profile"]=self.settings["profile"]

	def set_target_subpath(self):
		self.settings["target_subpath"]=self.settings["rel_type"]+"/"+\
				self.settings["target"]+"-"+self.settings["subarch"]+"-"+\
				self.settings["version_stamp"]

	def set_source_subpath(self):
		if not 'source_subpath' in self.settings:
			subpaths = self.calculate_source_subpath()
			msg("Possible source_subpath settings are: " + ', '.join(subpaths))
		if  not isinstance(self.settings["source_subpath"], str):
			raise CatalystError,\
				"source_subpath should have been a string. Perhaps you have something wrong in your spec file?"

	def set_pkgcache_path(self):
		if "pkgcache_path" in self.settings:
			if not isinstance(self.settings["pkgcache_path"], str):
				self.settings["pkgcache_path"]=\
					catalyst.util.normpath(" ".join(self.settings["pkgcache_path"]))
		else:
			self.settings["pkgcache_path"]=\
				catalyst.util.normpath(self.settings["storedir"]+"/packages/"+\
				self.settings["target_subpath"]+"/")

	def set_kerncache_path(self):
		if "kerncache_path" in self.settings:
			if not isinstance(self.settings["kerncache_path"], str):
				self.settings["kerncache_path"]=\
					catalyst.util.normpath(" ".join(self.settings["kerncache_path"]))
		else:
			self.settings["kerncache_path"]=catalyst.util.normpath(self.settings["storedir"]+\
				"/kerncache/"+self.settings["target_subpath"]+"/")

	def set_target_path(self):
		self.settings["target_path"]=catalyst.util.normpath(self.settings["storedir"]+\
			"/builds/"+self.settings["target_subpath"]+".tar.bz2")
		if self.check_autoresume("setup_target_path"):
			msg("Resume point detected, skipping target path setup operation...")
		else:
			""" First clean up any existing target stuff """
			# XXX WTF are we removing the old tarball before we start building the
			# XXX new one? If the build fails, you don't want to be left with
			# XXX nothing at all
#			if os.path.isfile(self.settings["target_path"]):
#				cmd("rm -f "+self.settings["target_path"],\
#					"Could not remove existing file: "\
#					+self.settings["target_path"],env=self.env)
			self.set_autoresume("setup_target_path")

		if not os.path.exists(self.settings["storedir"]+"/builds/"):
			os.makedirs(self.settings["storedir"]+"/builds/")

	def set_iso(self):
		if not "iso" in self.settings:
			self.settings["iso"] = "livecd-" + self.settings["subarch"] + "-" + self.settings["version_stamp"] + ".iso"
		if self.settings["iso"].startswith('/'):
			self.settings["iso"]=\
				catalyst.util.normpath(self.settings["iso"])
		else:
			# This automatically prepends the build dir to the ISO output path
			# if it doesn't start with a /
			self.settings["iso"] = catalyst.util.normpath(self.settings["storedir"] + \
				"/builds/" + self.settings["rel_type"] + "/" + \
				self.settings["iso"])

	def set_fstype(self):
		if not "fstype" in self.settings:
			self.settings["fstype"]="normal"
			for x in self.valid_values:
				if x ==  "fstype":
					msg("fstype is being set to the default of 'normal'")

	def set_fsops(self):
		if "fstype" in self.settings:
			self.valid_values.append("fsops")

	def set_source_path(self):
		if "SEEDCACHE" in self.settings\
			and os.path.isdir(catalyst.util.normpath(self.settings["storedir"]+"/tmp/"+\
				self.settings["source_subpath"]+"/")):
			self.settings["source_path"]=catalyst.util.normpath(self.settings["storedir"]+\
				"/tmp/"+self.settings["source_subpath"]+"/")
		else:
			self.settings["source_path"]=catalyst.util.normpath(self.settings["storedir"]+\
				"/builds/"+self.settings["source_subpath"]+".tar.bz2")
			if os.path.isfile(self.settings["source_path"]):
				self.settings["source_path_hash"]=\
					catalyst.hash.generate_hash(self.settings["source_path"],\
					hash_function=self.settings["hash_function"],\
					verbose=False)
		msg("Source path set to " + self.settings["source_path"])
		if os.path.isdir(self.settings["source_path"]):
			msg("\tIf this is not desired, remove this directory or turn off")
			msg("\tseedcache in the options of catalyst.conf the source path")
			msg("\twill then be " + \
				catalyst.util.normpath(self.settings["storedir"] + "/builds/" + \
				self.settings["source_subpath"] + ".tar.bz2"))

	def set_dest_path(self):
		if "root_path" in self.settings:
			self.settings["destpath"]=catalyst.util.normpath(self.settings["chroot_path"]+\
				self.settings["root_path"])
		else:
			self.settings["destpath"]=catalyst.util.normpath(self.settings["chroot_path"])

	def set_cleanables(self):
		self.settings["cleanables"]=["/etc/resolv.conf","/var/tmp/*","/tmp/*",\
			"/root/*","/usr/portage"]

	def set_snapshot_path(self):
		self.settings["snapshot_path"]=catalyst.util.normpath(self.settings["storedir"]+\
			"/snapshots/portage-"+self.settings["snapshot"]+".tar.bz2")

		if os.path.exists(self.settings["snapshot_path"]):
			self.settings["snapshot_path_hash"]=\
				catalyst.hash.generate_hash(self.settings["snapshot_path"],\
				hash_function=self.settings["hash_function"],verbose=False)

	def set_snapcache_path(self):
		if "SNAPCACHE" in self.settings:
			self.settings["snapshot_cache_path"]=\
				catalyst.util.normpath(self.settings["snapshot_cache"]+"/"+\
				self.settings["snapshot"]+"/")
			self.snapcache_lock=\
				catalyst.lock.LockDir(self.settings["snapshot_cache_path"])
			msg("Caching snapshot to " + self.settings["snapshot_cache_path"])

	def set_chroot_path(self):
		"""
		NOTE: the trailing slash is very important!
		Things *will* break without it!
		"""
		self.settings["chroot_path"]=catalyst.util.normpath(self.settings["storedir"]+\
			"/tmp/"+self.settings["target_subpath"]+"/")
		self.chroot_lock=catalyst.lock.LockDir(self.settings["chroot_path"])

	def set_controller_file(self):
		self.settings["controller_file"]=catalyst.util.normpath(self.settings["sharedir"]+\
			"/targets/"+self.settings["target"]+"/"+self.settings["target"]+\
			"-controller.sh")

	def set_iso_volume_id(self):
		if "volid" in self.settings:
			self.settings["iso_volume_id"]=\
				self.settings["volid"]
			if len(self.settings["iso_volume_id"])>32:
				raise CatalystError,\
					"ISO volume ID must not exceed 32 characters."
		else:
			self.settings["iso_volume_id"]="catalyst "+self.settings["snapshot"]

	def set_action_sequence(self):
		""" Default action sequence for run method """
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
				"config_profile_link","setup_confdir","portage_overlay",\
				"base_dirs","bind","chroot_setup","setup_environment",\
				"run_local","preclean","unbind","clean"]
#		if "TARBALL" in self.settings or \
#			not "FETCH" in self.settings:
		if not "FETCH" in self.settings:
			self.settings["action_sequence"].append("capture")
		self.settings["action_sequence"].append("clear_autoresume")

	def set_use(self):
		if "use" in self.settings:
			if isinstance(self.settings["use"], str):
				self.settings["use"]=self.settings["use"].split()
				self.settings["use"].append("bindist")

	def set_stage_path(self):
		self.settings["stage_path"]=catalyst.util.normpath(self.settings["chroot_path"])

	def set_mounts(self):
		pass

	def set_packages(self):
		pass

	def set_rm(self):
		if "rm" in self.settings:
			if isinstance(self.settings["rm"], str):
				self.settings["rm"]=\
					self.settings["rm"].split()

	def set_portage_overlay(self):
		if "portage_overlay" in self.settings:
			if isinstance(self.settings["portage_overlay"], str):
				self.settings["portage_overlay"]=\
					self.settings["portage_overlay"].split()
			msg("portage_overlay directories are set to: '" + \
				"".join(self.settings["portage_overlay"]) + "'")

	def set_overlay(self):
		if "overlay" in self.settings:
			if isinstance(self.settings["overlay"], str):
				self.settings["overlay"]=\
					self.settings["overlay"].split()

	def set_root_overlay(self):
		if "root_overlay" in self.settings:
			if isinstance(self.settings["root_overlay"], str):
				self.settings["root_overlay"]=\
					self.settings["root_overlay"].split()

	def set_root_path(self):
		""" ROOT= variable for emerges """
		self.settings["root_path"]="/"

	def set_valid_build_kernel_vars(self):
		if "boot/kernel" in self.settings:
			if isinstance(self.settings["boot/kernel"], str):
				loopy=[self.settings["boot/kernel"]]
			else:
				loopy=self.settings["boot/kernel"]

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
				if "boot/kernel/"+x+"/packages" in self.settings:
					if isinstance(self.settings["boot/kernel/" + x + "/packages"], str):
						self.settings["boot/kernel/"+x+"/packages"]=\
							[self.settings["boot/kernel/"+x+"/packages"]]

	def kill_chroot_pids(self):
		msg("Checking for processes running in chroot and killing them.")

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
		mypath=self.settings["chroot_path"]

		"""
		Check and verify that none of our paths in mypath are mounted. We don't
		want to clean up with things still mounted, and this allows us to check.
		Returns 1 on ok, 0 on "something is still mounted" case.
		"""

		if not os.path.exists(mypath):
			return

		for x in self.mounts:
			if not os.path.exists(mypath+x):
				continue

			if catalyst.util.ismount(mypath+x):
				""" Something is still mounted "" """
				try:
					msg(x + " is still mounted; performing auto-bind-umount...")
					""" Try to umount stuff ourselves """
					self.unbind()
					if catalyst.util.ismount(mypath+x):
						raise CatalystError("Auto-unbind failed for " + x)
					else:
						msg("Auto-unbind successful...")
				except CatalystError:
					raise CatalystError, "Unable to auto-unbind "+x

	def unpack(self):
		if self.check_autoresume("unpack"):
			msg("Resume point detected, skipping unpack operation...")
			return

		self.mount_safety_check()

		self.clear_chroot()

		if not os.path.exists(self.settings["chroot_path"]):
			catalyst.util.mkdir(self.settings["chroot_path"])

		if not os.path.exists(self.settings["chroot_path"]+"/tmp"):
			catalyst.util.mkdir(self.settings["chroot_path"]+"/tmp", 1777)

		if "PKGCACHE" in self.settings:
			if not os.path.exists(self.settings["pkgcache_path"]):
				catalyst.util.mkdir(self.settings["pkgcache_path"])

		if "KERNCACHE" in self.settings:
			if not os.path.exists(self.settings["kerncache_path"]):
				catalyst.util.mkdir(self.settings["kerncache_path"])

		if "SEEDCACHE" in self.settings and os.path.isdir(self.settings["source_path"]):
			catalyst.util.rsync(self.settings["source_path"], self.settings["chroot_path"], delete=True)
		else:
			catalyst.util.unpack_tarball(self.settings["source_path"], self.settings["chroot_path"])

		self.set_autoresume("unpack", self.settings["source_path"])

	def unpack_snapshot(self):
		if "SNAPCACHE" in self.settings:
			snapshot_cache_hash = catalyst.util.readfile(self.settings["snapshot_cache_path"] + "catalyst-hash")
			if snapshot_cache_hash == self.settings["snapshot_path_hash"]:
				msg("Valid snapshot cache, skipping unpack of portage tree...")
				return

		if self.check_autoresume("unpack_snapshot"):
			msg("Valid Resume point detected, skipping unpack of portage tree...")
			return

		msg("Unpacking portage tree (This can take a long time) ...")

		if "SNAPCACHE" in self.settings:
			self.snapcache_lock.write_lock()
			if os.path.exists(self.settings["snapshot_cache_path"]):
				catalyst.util.remove_path(self.settings["snapshot_cache_path"])
			catalyst.util.mkdir(self.settings["snapshot_cache_path"])
			catalyst.util.unpack_tarball(self.settings["snapshot_path"], self.settings["snapshot_cache_path"])
			self.snapcache_lock.unlock()
		else:
			if os.path.exists(self.settings["chroot_path"] + "/usr/portage"):
				catalyst.util.remove_path(self.settings["chroot_path"] + "/usr/portage")
			catalyst.util.mkdir(self.settings["chroot_path"] + "/usr/portage")
			catalyst.util.unpack_tarball(self.settings["snapshot_path"], self.settings["chroot_path"] + "/usr/portage")

		self.set_autoresume("unpack_portage", self.settings["snapshot_path"])
		myf = open(self.settings["snapshot_cache_path"] + "catalyst-hash")
		myf.write(self.settings["snapshot_path_hash"])
		myf.close()

	def config_profile_link(self):
		if self.check_autoresume("config_profile_link"):
			msg("Resume point detected, skipping config_profile_link operation...")
		else:
			# TODO: zmedico and I discussed making this a directory and pushing
			# in a parent file, as well as other user-specified configuration.
			msg("Configuring profile link...")
			catalyst.util.create_symlink("../usr/portage/profiles/" + self.settings["target_profile"], \
				self.settings["chroot_path"] + "/etc/make.profile", True)
			self.set_autoresume("config_profile_link")

	def setup_confdir(self):
		if self.check_autoresume("setup_confdir"):
			msg("Resume point detected, skipping setup_confdir operation...")
		else:
			if "portage_confdir" in self.settings:
				msg("Configuring /etc/portage...")
				catalyst.util.remove_path(self.settings["chroot_path"] + "/etc/portage")
				catalyst.util.copy(self.settings["portage_confdir"] + "/", self.settings["chroot_path"] + "/etc/portage", recursive=True)
				self.set_autoresume("setup_confdir")

	def portage_overlay(self):
		""" We copy the contents of our overlays to /usr/local/portage """
		if "portage_overlay" in self.settings:
			for x in self.settings["portage_overlay"]:
				if os.path.exists(x):
					msg("Copying overlay dir " + x)
					catalyst.util.mkdir(self.settings["chroot_path"] + "/usr/local/portage")
					# Perhaps we should use rsync here?
					catalyst.util.copy(x + "/*", self.settings["chroot_path"] + "/usr/local/portage", recursive=True)

	def root_overlay(self):
		""" Copy over the root_overlay """
		if "root_overlay" in self.settings:
			for x in self.settings["root_overlay"]:
				if os.path.exists(x):
					msg("Copying root_overlay: " + x)
					catalyst.util.rsync(x + "/", self.settings["chroot_path"])

	def base_dirs(self):
		pass

	def bind(self):
		for x in self.mounts:
			if not os.path.exists(self.settings["chroot_path"]+x):
				os.makedirs(self.settings["chroot_path"]+x,0755)

			if not os.path.exists(self.mountmap[x]):
				os.makedirs(self.mountmap[x],0755)

			src=self.mountmap[x]
			if "SNAPCACHE" in self.settings and x == "/usr/portage":
				self.snapcache_lock.read_lock()
			if os.uname()[0] == "FreeBSD":
				if src == "/dev":
					retval=os.system("mount -t devfs none "+\
						self.settings["chroot_path"]+x)
				else:
					retval=os.system("mount_nullfs "+src+" "+\
						self.settings["chroot_path"]+x)
			else:
				retval=os.system("mount --bind "+src+" "+\
					self.settings["chroot_path"]+x)
			if retval!=0:
				self.unbind()
				raise CatalystError,"Couldn't bind mount "+src

	def unbind(self):
		ouch=0
		mypath=self.settings["chroot_path"]
		myrevmounts=self.mounts[:]
		myrevmounts.reverse()
		""" Unmount in reverse order for nested bind-mounts """
		for x in myrevmounts:
			if not os.path.exists(mypath+x):
				continue

			if not catalyst.util.ismount(mypath+x):
				continue

			retval=os.system("umount "+\
				os.path.join(mypath,x.lstrip(os.path.sep)))

			if retval!=0:
				warn("First attempt to unmount: "+mypath+x+" failed.")
				warn("Killing any pids still running in the chroot")

				self.kill_chroot_pids()

				retval2=os.system("umount "+mypath+x)
				if retval2!=0:
					ouch=1
					warn("Couldn't umount bind mount: "+mypath+x)

			if "SNAPCACHE" in self.settings and x == "/usr/portage":
				try:
					"""
					It's possible the snapshot lock object isn't created yet.
					This is because mount safety check calls unbind before the
					target is fully initialized
					"""
					self.snapcache_lock.unlock()
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
		self.makeconf=catalyst.util.read_makeconf(self.settings["chroot_path"]+\
			"/etc/make.conf")
		self.override_cbuild()
		self.override_chost()
		self.override_cflags()
		self.override_cxxflags()
		self.override_ldflags()
		if self.check_autoresume("chroot_setup"):
			msg("Resume point detected, skipping chroot_setup operation...")
		else:
			msg("Setting up chroot...")

			#self.makeconf=catalyst.util.read_makeconf(self.settings["chroot_path"]+"/etc/make.conf")

			catalyst.util.copy("/etc/resolv.conf", self.settings["chroot_path"] + "/etc")

			""" Copy over the envscript, if applicable """
			if "ENVSCRIPT" in self.settings:
				if not os.path.exists(self.settings["ENVSCRIPT"]):
					raise CatalystError,\
						"Can't find envscript "+self.settings["ENVSCRIPT"]

				msg("\nWarning!!!!")
				msg("\tOverriding certain env variables may cause catastrophic failure.")
				msg("\tIf your build fails look here first as the possible problem.")
				msg("\tCatalyst assumes you know what you are doing when setting")
				msg("\t\tthese variables.")
				msg("\tCatalyst Maintainers use VERY minimal envscripts if used at all")
				msg("\tYou have been warned\n")

				catalyst.util.copy(self.settings["ENVSCRIPT"], self.settings["chroot_path"] + "/tmp/envscript")

			"""
			Copy over /etc/hosts from the host in case there are any
			specialties in there
			"""
			if os.path.exists(self.settings["chroot_path"]+"/etc/hosts"):
				catalyst.util.move(self.settings["chroot_path"] + "/etc/hosts", \
					self.settings["chroot_path"] + "/etc/hosts.catalyst")
				catalyst.util.copy("/etc/hosts", self.settings["chroot_path"] + "/etc/hosts")

			""" Modify and write out make.conf (for the chroot) """
			catalyst.util.remove_path(self.settings["chroot_path"] + "/etc/make.conf")
			myf=open(self.settings["chroot_path"]+"/etc/make.conf","w")
			myf.write("# These settings were set by the catalyst build script that automatically\n# built this stage.\n")
			myf.write("# Please consult /usr/share/portage/config/make.conf.example for a more\n# detailed example.\n")
			if "CFLAGS" in self.settings:
				myf.write('CFLAGS="'+self.settings["CFLAGS"]+'"\n')
			if "CXXFLAGS" in self.settings:
				myf.write('CXXFLAGS="'+self.settings["CXXFLAGS"]+'"\n')
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
				myf.write('USE="' + " ".join(myusevars)+'"\n')
				if '-*' in myusevars:
					msg("\nWarning!!!  ")
					msg("\tThe use of -* in " + "use will cause portage to ignore")
					msg("\tpackage.use in the profile and portage_confdir. You've been warned!")

			""" Setup the portage overlay """
			if "portage_overlay" in self.settings:
				myf.write('PORTDIR_OVERLAY="/usr/local/portage"\n')

			myf.close()
			catalyst.util.copy(self.settings["chroot_path"] + "/etc/make.conf", \
				self.settings["chroot_path"] + "/etc/make.conf.catalyst")
			self.set_autoresume("chroot_setup")

	def fsscript(self):
		if self.check_autoresume("fsscript"):
			msg("Resume point detected, skipping fsscript operation...")
		else:
			if "fsscript" in self.settings:
				self.run_controller_action("fsscript")
				self.set_autoresume("fsscript")

	def rcupdate(self):
		if self.check_autoresume("rcupdate"):
			msg("Resume point detected, skipping rcupdate operation...")
		else:
			self.run_controller_action("rc-update")
			self.set_autoresume("rcupdate")

	def clean(self):
		if self.check_autoresume("clean"):
			msg("Resume point detected, skipping clean operation...")
		else:
			for x in self.settings["cleanables"]:
				msg("Cleaning chroot: " + x +"...")
				catalyst.util.remove_path(self.settings["destpath"] + x)

		""" Put /etc/hosts back into place """
		if os.path.exists(self.settings["chroot_path"]+"/etc/hosts.catalyst"):
			catalyst.util.move(self.settings["chroot_path"] + "/etc/hosts.catalyst", \
				self.settings["chroot_path"]+"/etc/hosts", force=True)

		""" Remove our overlay """
		if os.path.exists(self.settings["chroot_path"]+"/usr/local/portage"):
			catalyst.util.remove_path(self.settings["chroot_path"] + "/usr/local/portage")
			cmd("sed -i '/^PORTDIR_OVERLAY/d' "+self.settings["chroot_path"]+\
				"/etc/make.conf",\
				"Could not remove PORTDIR_OVERLAY from make.conf",env=self.env)

		""" Clean up old and obsoleted files in /etc """
		if os.path.exists(self.settings["stage_path"]+"/etc"):
			cmd("find "+self.settings["stage_path"]+\
				"/etc -maxdepth 1 -name \"*-\" | xargs rm -f",\
				"Could not remove stray files in /etc",env=self.env)

		self.run_controller_action("clean")
		self.set_autoresume("clean")

	def empty(self):
		if self.check_autoresume("empty"):
			msg("Resume point detected, skipping empty operation...")
		else:
			if "empty" in self.settings:
				if isinstance(self.settings["empty"], str):
					self.settings["empty"]=\
						self.settings["empty"].split()
				for x in self.settings["empty"]:
					myemp=self.settings["destpath"]+x
					if not os.path.isdir(myemp):
						msg(x + " not a directory or does not exist, skipping 'empty' operation.")
						continue
					msg("Emptying directory" + x)
					catalyst.util.empty_dir(myemp)
			self.set_autoresume("empty")

	def remove(self):
		if self.check_autoresume("remove"):
			msg("Resume point detected, skipping remove operation...")
		else:
			if "rm" in self.settings:
				for x in self.settings["rm"]:
					"""
					We're going to shell out for all these cleaning
					operations, so we get easy glob handling.
					"""
					msg("livecd: removing " + x)
					try:
						catalyst.util.remove_path(self.settings["chroot_path"] + x)
					except:
						pass
				try:
					self.run_controller_action("clean")
					self.set_autoresume("remove")
				except:
					self.unbind()
					raise

	def preclean(self):
		if self.check_autoresume("preclean"):
			msg("Resume point detected, skipping preclean operation...")
		else:
			try:
				self.run_controller_action("preclean")
				self.set_autoresume("preclean")

			except:
				self.unbind()
				raise CatalystError, "Build failed, could not execute preclean"

	def capture(self):
		if self.check_autoresume("capture"):
			msg("Resume point detected, skipping capture operation...")
		else:
			""" Capture target in a tarball """
			mypath=self.settings["target_path"].split("/")
			""" Remove filename from path """
			mypath = " ".join(mypath[:-1],"/")

			""" Now make sure path exists """
			if not os.path.exists(mypath):
				os.makedirs(mypath)

			msg("Creating stage tarball...")

			catalyst.util.create_tarball(self.settings["target_path"], ".", working_dir=self.settings["stage_path"], keep_perm=True)

			catalyst.hash.gen_contents_file(self.settings["target_path"], self.settings)
			catalyst.hash.gen_digest_file(self.settings["target_path"], self.settings)

			self.set_autoresume("capture")

	def run_local(self):
		if self.check_autoresume("run_local"):
			msg("Resume point detected, skipping run_local operation...")
		else:
			try:
				self.run_controller_action("run")
				self.set_autoresume("run_local")

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
			if isinstance(self.settings[x], str):
				""" Prefix to prevent namespace clashes """
				#os.environ[varname]=self.settings[x]
				self.env[varname]=self.settings[x]
			elif isinstance(self.settings[x], list):
				#os.environ[varname] = " ".join(self.settings[x])
				self.env[varname] = " ".join(self.settings[x])
			elif isinstance(self.settings[x], bool):
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

		if "PURGEONLY" in self.settings:
			self.purge()
			return

		if "PURGE" in self.settings:
			self.purge()

		for x in self.settings["action_sequence"]:
			msg("--- Running action sequence: " + x)
			sys.stdout.flush()
			try:
				func = getattr(self, x)
				func()
			except:
				self.mount_safety_check()
				raise

		self.chroot_lock.unlock()

	def unmerge(self):
		if self.check_autoresume("unmerge"):
			msg("Resume point detected, skipping unmerge operation...")
		else:
			if "unmerge" in self.settings:
				if isinstance(self.settings["unmerge"], str):
					self.settings["unmerge"]=\
						[self.settings["unmerge"]]
				myunmerge=\
					self.settings["unmerge"][:]

				for x in range(0,len(myunmerge)):
					"""
					Surround args with quotes for passing to bash, allows
					things like "<" to remain intact
					"""
					myunmerge[x]="'"+myunmerge[x]+"'"
				myunmerge = " ".join(myunmerge)

				""" Before cleaning, unmerge stuff """
				try:
					self.run_controller_action("unmerge")
					msg("unmerge shell script")
				except CatalystError:
					self.unbind()
					raise
				self.set_autoresume("unmerge")

	def target_setup(self):
		if self.check_autoresume("target_setup"):
			msg("Resume point detected, skipping target_setup operation...")
		else:
			msg("Setting up filesystems per filesystem type")
			self.run_controller_action("target_image_setup")
			self.set_autoresume("target_setup")

	def setup_overlay(self):
		if self.check_autoresume("setup_overlay"):
			msg("Resume point detected, skipping setup_overlay operation...")
		else:
			if "overlay" in self.settings:
				for x in self.settings["overlay"]:
					if os.path.exists(x):
						catalyst.util.rsync(x + "/", self.settings["target_path"])
				self.set_autoresume("setup_overlay")

	def create_iso(self):
		if self.check_autoresume("create_iso"):
			msg("Resume point detected, skipping create_iso operation...")
		else:
			""" Create the ISO """
			if "iso" in self.settings:
				self.run_controller_action("iso", self.settings["iso"])
				catalyst.hash.gen_contents_file(self.settings["iso"], self.settings)
				catalyst.hash.gen_digest_file(self.settings["iso"], self.settings)
				self.set_autoresume("create_iso")
			else:
				msg("WARNING: livecd/iso was not defined.")
				msg("An ISO Image will not be created.")

	def build_packages(self):
		if "packages" in self.settings:
			if self.check_autoresume("build_packages"):
				msg("Resume point detected, skipping build_packages operation...")
			else:
				mypack = \
					catalyst.util.list_bashify(self.settings["packages"])
				try:
					self.run_controller_action("build_packages", mypack)
					self.set_autoresume("build_packages")
				except CatalystError:
					self.unbind()
					raise CatalystError("build aborting due to error")

	def build_kernel(self):
		if self.check_autoresume("build_kernel"):
			msg("Resume point detected, skipping build_kernel operation...")
		else:
			if "boot/kernel" in self.settings:
				try:
					mynames=self.settings["boot/kernel"]
					if isinstance(mynames, str):
						mynames=[mynames]
					"""
					Execute the script that sets up the kernel build environment
					"""
					self.run_controller_action("pre-kmerge")

					for kname in mynames:
						if self.check_autoresume("build_kernel_" + kname):
							msg("Resume point detected, skipping build_kernel for " + kname + " operation...")
						else: # TODO: make this not require a kernel config
							try:
								if not os.path.exists(self.settings["boot/kernel/"+kname+"/config"]):
									self.unbind()
									raise CatalystError,\
										"Can't find kernel config: "+\
										self.settings["boot/kernel/"+kname+\
										"/config"]

							except TypeError:
								raise CatalystError,\
									"Required value boot/kernel/config not specified"

							try:
								catalyst.util.copy(self.settings["boot/kernel/" + kname + "/config"],
									self.settings["chroot_path"] + "/var/tmp/" + kname + ".config")

							except CatalystError:
								self.unbind()

							"""
							If we need to pass special options to the bootloader
							for this kernel put them into the environment
							"""
							if self.settings.has_key("boot/kernel/"+kname+\
								"/kernelopts"):
								myopts=self.settings["boot/kernel/"+kname+\
									"/kernelopts"]

								if not isinstance(myopts, str):
									myopts = " ".join(myopts)
									self.env[kname+"_kernelopts"]=myopts

								else:
									self.env[kname+"_kernelopts"]=""

							if not self.settings.has_key("boot/kernel/"+kname+\
								"/extraversion"):
								self.settings["boot/kernel/"+kname+\
									"/extraversion"]=""

							self.env["clst_kextraversion"]=\
								self.settings["boot/kernel/"+kname+\
								"/extraversion"]

							if self.settings.has_key("boot/kernel/"+kname+\
								"/initramfs_overlay"):
								if os.path.exists(self.settings["boot/kernel/"+\
									kname+"/initramfs_overlay"]):
									msg("Copying initramfs_overlay dir " + \
										self.settings["boot/kernel/" + kname + \
										"/initramfs_overlay"])

									catalyst.util.mkdir(self.settings["chroot_path"] + \
										"/tmp/initramfs_overlay/" + \
										self.settings["boot/kernel/" + kname + \
										"/initramfs_overlay"])

									catalyst.util.copy(self.settings["boot/kernel/" + kname + "/initramfs_overlay"] + "/*",
										self.settings["chroot_path"] + "/tmp/initramfs_overlay/" + \
										self.settings["boot/kernel/" + kname + "/initramfs_overlay"], \
										recursive=True)

							""" Execute the script that builds the kernel """
							self.run_controller_action("kernel", kname)

							if self.settings.has_key("boot/kernel/"+kname+\
								"/initramfs_overlay"):
								if os.path.exists(self.settings["chroot_path"]+\
									"/tmp/initramfs_overlay/"):
									msg("Cleaning up temporary overlay dir")
									catalyst.util.remove_path(self.settings["chroot_path"] + \
										"/tmp/initramfs_overlay/")

							self.set_autoresume("build_kernel_" + kname)

							"""
							Execute the script that cleans up the kernel build
							environment
							"""
							self.run_controller_action("post-kmerge")

					self.set_autoresume("build_kernel")

				except CatalystError:
					self.unbind()
					raise CatalystError,\
						"build aborting due to kernel build error."

	def bootloader(self):
		if self.check_autoresume("bootloader"):
			msg("Resume point detected, skipping bootloader operation...")
		else:
			try:
				self.run_controller_action("bootloader", self.settings["target_path"])
				self.set_autoresume("bootloader")
			except CatalystError:
				self.unbind()
				raise CatalystError,"Script aborting due to error."

	def livecd_update(self):
		if self.check_autoresume("livecd_update"):
			msg("Resume point detected, skipping build_packages operation...")
		else:
			try:
				self.run_controller_action("livecd-update")

			except CatalystError:
				self.unbind()
				raise CatalystError,"build aborting due to livecd_update error."

	def clear_chroot(self):
		myemp=self.settings["chroot_path"]
		if os.path.isdir(myemp):
			msg("Emptying directory " + myemp)
			catalyst.util.empty_dir(myemp)

	def clear_packages(self):
		if "PKGCACHE" in self.settings:
			msg("purging the pkgcache...")

			myemp=self.settings["pkgcache_path"]
			if os.path.isdir(myemp):
				msg("Emptying directory " + myemp)
				catalyst.util.empty_dir(myemp)

	def clear_kerncache(self):
		if "KERNCACHE" in self.settings:
			msg("purging the kerncache...")

			myemp=self.settings["kerncache_path"]
			if os.path.isdir(myemp):
				msg("Emptying directory " + myemp)
				catalyst.util.empty_dir(myemp)

	def clear_autoresume(self):
		""" Clean resume points since they are no longer needed """
		if self.check_autoresume():
			msg("Removing AutoResume Points: ...")
			myemp=self.settings["autoresume_path"]
			if os.path.isdir(myemp):
				msg("Emptying directory " + myemp)
				catalyst.util.empty_dir(myemp)

	def purge(self):
		catalyst.util.countdown(10, "Purging Caches ...")
		if "PURGE" in self.settings or "PURGEONLY" in self.settings:
			msg("clearing autoresume ...")
			self.clear_autoresume()

			msg("clearing chroot ...")
			self.clear_chroot()

			msg("clearing package cache ...")
			self.clear_packages()

			msg("clearing kerncache ...")
			self.clear_kerncache()

# vim: ts=4 sw=4 sta noet sts=4 ai
