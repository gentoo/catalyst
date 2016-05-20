
import os
import imp
import shutil
import sys

from snakeoil import fileutils

from DeComp.compress import CompressMap

from catalyst import log
from catalyst.defaults import (SOURCE_MOUNT_DEFAULTS, TARGET_MOUNT_DEFAULTS,
	PORT_LOGDIR_CLEAN)
from catalyst.support import (CatalystError, file_locate, normpath,
	cmd, read_makeconf, ismount, file_check)
from catalyst.base.targetbase import TargetBase
from catalyst.base.clearbase import ClearBase
from catalyst.base.genbase import GenBase
from catalyst.lock import LockDir, LockInUse
from catalyst.fileops import ensure_dirs, pjoin, clear_dir, clear_path
from catalyst.base.resume import AutoResume

if sys.version_info[0] >= 3:
	py_input = input
else:
	py_input = raw_input  # pylint: disable=undefined-variable


class StageBase(TargetBase, ClearBase, GenBase):
	"""
	This class does all of the chroot setup, copying of files, etc. It is
	the driver class for pretty much everything that Catalyst does.
	"""
	def __init__(self,myspec,addlargs):
		self.required_values.extend(["version_stamp","target","subarch",\
			"rel_type","profile","snapshot","source_subpath"])

		self.valid_values.extend(["version_stamp","target","subarch",
			"rel_type","profile","snapshot","source_subpath","portage_confdir",
			"cflags","cxxflags","fcflags","fflags","ldflags","asflags","cbuild","hostuse","portage_overlay",
			"distcc_hosts","makeopts","pkgcache_path","kerncache_path",
			"compression_mode", "decompression_mode"])

		self.set_valid_build_kernel_vars(addlargs)
		TargetBase.__init__(self, myspec, addlargs)
		GenBase.__init__(self, myspec)
		ClearBase.__init__(self, myspec)

		# The semantics of subarchmap and machinemap changed a bit in 2.0.3 to
		# work better with vapier's CBUILD stuff. I've removed the "monolithic"
		# machinemap from this file and split up its contents amongst the
		# various arch/foo.py files.
		#
		# When register() is called on each module in the arch/ dir, it now
		# returns a tuple instead of acting on the subarchmap dict that is
		# passed to it. The tuple contains the values that were previously
		# added to subarchmap as well as a new list of CHOSTs that go along
		# with that arch. This allows us to build machinemap on the fly based
		# on the keys in subarchmap and the values of the 2nd list returned
		# (tmpmachinemap).
		#
		# Also, after talking with vapier. I have a slightly better idea of what
		# certain variables are used for and what they should be set to. Neither
		# 'buildarch' or 'hostarch' are used directly, so their value doesn't
		# really matter. They are just compared to determine if we are
		# cross-compiling. Because of this, they are just set to the name of the
		# module in arch/ that the subarch is part of to make things simpler.
		# The entire build process is still based off of 'subarch' like it was
		# previously. -agaffney

		self.makeconf = {}
		self.archmap = {}
		self.subarchmap = {}
		machinemap = {}
		arch_dir = self.settings["archdir"] + "/"
		for x in [x[:-3] for x in os.listdir(arch_dir) if x.endswith(".py") and x != "__init__.py"]:
			try:
				fh=open(arch_dir + x + ".py")
				# This next line loads the plugin as a module and assigns it to
				# archmap[x]
				self.archmap[x]=imp.load_module(x,fh, arch_dir + x + ".py",
					(".py", "r", imp.PY_SOURCE))
				# This next line registers all the subarches supported in the
				# plugin
				tmpsubarchmap, tmpmachinemap = self.archmap[x].register()
				self.subarchmap.update(tmpsubarchmap)
				for machine in tmpmachinemap:
					machinemap[machine] = x
				for subarch in tmpsubarchmap:
					machinemap[subarch] = x
				fh.close()
			except IOError:
				# This message should probably change a bit, since everything in
				# the dir should load just fine. If it doesn't, it's probably a
				# syntax error in the module
				log.warning("Can't find/load %s.py plugin in %s", x, arch_dir)

		if "chost" in self.settings:
			hostmachine = self.settings["chost"].split("-")[0]
			if hostmachine not in machinemap:
				raise CatalystError("Unknown host machine type "+hostmachine)
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
			raise CatalystError("Unknown build machine type "+buildmachine)
		self.settings["buildarch"]=machinemap[buildmachine]
		self.settings["crosscompile"]=(self.settings["hostarch"]!=\
			self.settings["buildarch"])

		# Call arch constructor, pass our settings
		try:
			self.arch=self.subarchmap[self.settings["subarch"]](self.settings)
		except KeyError:
			log.critical(
				'Invalid subarch: %s\n'
				'Choose one of the following:\n'
				' %s',
				self.settings['subarch'], ' '.join(self.subarchmap))

		log.notice('Using target: %s', self.settings['target'])
		# Print a nice informational message
		if self.settings["buildarch"]==self.settings["hostarch"]:
			log.info('Building natively for %s', self.settings['hostarch'])
		elif self.settings["crosscompile"]:
			log.info('Cross-compiling on %s for different machine type %s',
				self.settings['buildarch'], self.settings['hostarch'])
		else:
			log.info('Building on %s for alternate personality type %s',
				self.settings['buildarch'], self.settings['hostarch'])

		# This must be set first as other set_ options depend on this
		self.set_spec_prefix()

		# Initialize our (de)compressor's)
		self.decompressor = CompressMap(self.settings["decompress_definitions"],
			env=self.env,
			search_order=self.settings["decompressor_search_order"],
			comp_prog=self.settings["comp_prog"],
			decomp_opt=self.settings["decomp_opt"])
		self.accepted_extensions = self.decompressor.search_order_extensions(
			self.settings["decompressor_search_order"])
		log.notice("Source file specification matching setting is: %s",
			self.settings["source_matching"])
		log.notice("Accepted source file extensions search order: %s",
			self.accepted_extensions)
		# save resources, it is not always needed
		self.compressor = None

		# Define all of our core variables
		self.set_target_profile()
		self.set_target_subpath()
		self.set_source_subpath()

		# Set paths
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
		self.set_default_action_sequence()
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

		# This next line checks to make sure that the specified variables exist
		# on disk.
		#pdb.set_trace()
		file_locate(self.settings,["distdir"],\
			expand=0)
		# If we are using portage_confdir, check that as well.
		if "portage_confdir" in self.settings:
			file_locate(self.settings,["portage_confdir"],expand=0)

		# Setup our mount points.
		# initialize our target mounts.
		self.target_mounts = TARGET_MOUNT_DEFAULTS.copy()

		self.mounts = ["proc", "dev", "portdir", "distdir", "port_tmpdir"]
		# initialize our source mounts
		self.mountmap = SOURCE_MOUNT_DEFAULTS.copy()
		# update them from settings
		self.mountmap["distdir"] = self.settings["distdir"]
		if "snapcache" not in self.settings["options"]:
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

		# Configure any user specified options (either in catalyst.conf or on
		# the command line).
		if "pkgcache" in self.settings["options"]:
			self.set_pkgcache_path()
			log.info('Location of the package cache is %s', self.settings['pkgcache_path'])
			self.mounts.append("packagedir")
			self.mountmap["packagedir"] = self.settings["pkgcache_path"]

		if "kerncache" in self.settings["options"]:
			self.set_kerncache_path()
			log.info('Location of the kerncache is %s', self.settings['kerncache_path'])
			self.mounts.append("kerncache")
			self.mountmap["kerncache"] = self.settings["kerncache_path"]

		if "ccache" in self.settings["options"]:
			if "CCACHE_DIR" in os.environ:
				ccdir=os.environ["CCACHE_DIR"]
				del os.environ["CCACHE_DIR"]
			else:
				ccdir="/root/.ccache"
			if not os.path.isdir(ccdir):
				raise CatalystError(
					"Compiler cache support can't be enabled (can't find "+\
					ccdir+")")
			self.mounts.append("ccache")
			self.mountmap["ccache"] = ccdir
			# for the chroot:
			self.env["CCACHE_DIR"] = self.target_mounts["ccache"]

		if "icecream" in self.settings["options"]:
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

	def override_fcflags(self):
		if "FCFLAGS" in self.makeconf:
			self.settings["FCFLAGS"]=self.makeconf["FCFLAGS"]

	def override_fflags(self):
		if "FFLAGS" in self.makeconf:
			self.settings["FFLAGS"]=self.makeconf["FFLAGS"]

	def override_ldflags(self):
		if "LDFLAGS" in self.makeconf:
			self.settings["LDFLAGS"]=self.makeconf["LDFLAGS"]

	def override_asflags(self):
		if "ASFLAGS" in self.makeconf:
			self.settings["ASFLAGS"]=self.makeconf["ASFLAGS"]

	def set_install_mask(self):
		if "install_mask" in self.settings:
			if not isinstance(self.settings['install_mask'], str):
				self.settings["install_mask"]=\
					' '.join(self.settings["install_mask"])

	def set_spec_prefix(self):
		self.settings["spec_prefix"]=self.settings["target"]

	def set_target_profile(self):
		self.settings["target_profile"]=self.settings["profile"]

	def set_target_subpath(self):
		self.settings["target_subpath"]=self.settings["rel_type"]+"/"+\
				self.settings["target"]+"-"+self.settings["subarch"]+"-"+\
				self.settings["version_stamp"] +'/'

	def set_source_subpath(self):
		if not isinstance(self.settings['source_subpath'], str):
			raise CatalystError(
				"source_subpath should have been a string. Perhaps you have " +\
				"something wrong in your spec file?")

	def set_pkgcache_path(self):
		if "pkgcache_path" in self.settings:
			if not isinstance(self.settings['pkgcache_path'], str):
				self.settings["pkgcache_path"]=\
					normpath(self.settings["pkgcache_path"])
		else:
			self.settings["pkgcache_path"]=\
				normpath(self.settings["storedir"]+"/packages/"+\
				self.settings["target_subpath"]+"/")

	def set_kerncache_path(self):
		if "kerncache_path" in self.settings:
			if not isinstance(self.settings['kerncache_path'], str):
				self.settings["kerncache_path"]=\
					normpath(self.settings["kerncache_path"])
		else:
			self.settings["kerncache_path"]=normpath(self.settings["storedir"]+\
				"/kerncache/"+self.settings["target_subpath"])

	def set_target_path(self):
		self.settings["target_path"]=normpath(self.settings["storedir"]+\
			"/builds/"+self.settings["target_subpath"])
		if "autoresume" in self.settings["options"]\
			and self.resume.is_enabled("setup_target_path"):
			log.notice('Resume point detected, skipping target path setup operation...')
		else:
			self.resume.enable("setup_target_path")
			ensure_dirs(self.settings["storedir"] + "/builds")

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
					log.info('%s/fstype is being set to the default of "normal"',
						self.settings['spec_prefix'])

	def set_fsops(self):
		if "fstype" in self.settings:
			self.valid_values.append("fsops")
			if self.settings["spec_prefix"]+"/fsops" in self.settings:
				self.settings["fsops"]=\
					self.settings[self.settings["spec_prefix"]+"/fsops"]
				del self.settings[self.settings["spec_prefix"]+"/fsops"]

	def set_source_path(self):
		if "seedcache" in self.settings["options"]\
			and os.path.isdir(normpath(self.settings["storedir"]+"/tmp/"+\
				self.settings["source_subpath"]+"/")):
			self.settings["source_path"] = normpath(self.settings["storedir"] +
				"/tmp/" + self.settings["source_subpath"] + "/")
		else:
			log.debug('Checking source path existence and '
				'get the final filepath. subpath: %s',
				self.settings["source_subpath"])
			self.settings["source_path"] = file_check(
				normpath(self.settings["storedir"] + "/builds/" +
					self.settings["source_subpath"]),
				self.accepted_extensions,
				self.settings["source_matching"] in ["strict"]
				)
			log.debug('Source path returned from file_check is: %s',
				self.settings["source_path"])
			if os.path.isfile(self.settings["source_path"]):
				# XXX: Is this even necessary if the previous check passes?
				if os.path.exists(self.settings["source_path"]):
					self.settings["source_path_hash"] = \
						self.settings["hash_map"].generate_hash(
							self.settings["source_path"],
							hash_=self.settings["hash_function"])
		log.notice('Source path set to %s', self.settings['source_path'])

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
		self.settings["snapshot_path"]= file_check(
			normpath(self.settings["storedir"]+\
				"/snapshots/" + self.settings["snapshot_name"] +
				self.settings["snapshot"]),
			self.accepted_extensions,
			self.settings["source_matching"] is "strict"
			)
		log.info('SNAPSHOT_PATH set to: %s', self.settings['snapshot_path'])
		self.settings["snapshot_path_hash"] = \
			self.settings["hash_map"].generate_hash(
				self.settings["snapshot_path"],
				hash_=self.settings["hash_function"])

	def set_snapcache_path(self):
		self.settings["snapshot_cache_path"]=\
			normpath(pjoin(self.settings["snapshot_cache"],
				self.settings["snapshot"]))
		if "snapcache" in self.settings["options"]:
			self.settings["snapshot_cache_path"] = \
				normpath(pjoin(self.settings["snapshot_cache"],
					self.settings["snapshot"]))
			self.snapcache_lock=\
				LockDir(self.settings["snapshot_cache_path"])
			log.info('Setting snapshot cache to %s', self.settings['snapshot_cache_path'])

	def set_chroot_path(self):
		"""
		NOTE: the trailing slash has been removed
		Things *could* break if you don't use a proper join()
		"""
		self.settings["chroot_path"]=normpath(self.settings["storedir"]+\
			"/tmp/"+self.settings["target_subpath"].rstrip('/'))
		self.chroot_lock=LockDir(self.settings["chroot_path"])

	def set_autoresume_path(self):
		self.settings["autoresume_path"] = normpath(pjoin(
			self.settings["storedir"], "tmp", self.settings["rel_type"],
			".autoresume-%s-%s-%s"
			%(self.settings["target"], self.settings["subarch"],
				self.settings["version_stamp"])
			))
		if "autoresume" in self.settings["options"]:
			log.info('The autoresume path is %s', self.settings['autoresume_path'])
		self.resume = AutoResume(self.settings["autoresume_path"], mode=0o755)

	def set_controller_file(self):
		self.settings["controller_file"]=normpath(self.settings["sharedir"]+\
			"/targets/"+self.settings["target"]+"/"+self.settings["target"]+\
			"-controller.sh")

	def set_iso_volume_id(self):
		if self.settings["spec_prefix"]+"/volid" in self.settings:
			self.settings["iso_volume_id"]=\
				self.settings[self.settings["spec_prefix"]+"/volid"]
			if len(self.settings["iso_volume_id"])>32:
				raise CatalystError(
					"ISO volume ID must not exceed 32 characters.")
		else:
			self.settings["iso_volume_id"]="catalyst "+self.settings["snapshot"]

	def set_default_action_sequence(self):
		""" Default action sequence for run method.

		This method sets the optional purgeonly action sequence and returns.
		Or it calls the normal set_action_sequence() for the target stage.
		"""
		if "purgeonly" in self.settings["options"]:
			self.settings["action_sequence"] = ["remove_chroot"]
			return
		self.set_action_sequence()

	def set_action_sequence(self):
		"""Set basic stage1, 2, 3 action sequences"""
		self.settings["action_sequence"]=["unpack","unpack_snapshot",\
				"setup_confdir","portage_overlay",\
				"base_dirs","bind","chroot_setup","setup_environment",\
				"run_local","preclean","unbind","clean"]
		self.set_completion_action_sequences()

	def set_completion_action_sequences(self):
		if "fetch" not in self.settings["options"]:
			self.settings["action_sequence"].append("capture")
		if "keepwork" in self.settings["options"]:
			self.settings["action_sequence"].append("clear_autoresume")
		elif "seedcache" in self.settings["options"]:
			self.settings["action_sequence"].append("remove_autoresume")
		else:
			self.settings["action_sequence"].append("remove_autoresume")
			self.settings["action_sequence"].append("remove_chroot")
		return

	def set_use(self):
		if self.settings["spec_prefix"]+"/use" in self.settings:
			self.settings["use"]=\
				self.settings[self.settings["spec_prefix"]+"/use"]
			del self.settings[self.settings["spec_prefix"]+"/use"]
		if "use" not in self.settings:
			self.settings["use"]=""
		if isinstance(self.settings['use'], str):
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
			if isinstance(self.settings[self.settings['spec_prefix']+'/rm'], str):
				self.settings[self.settings["spec_prefix"]+"/rm"]=\
					self.settings[self.settings["spec_prefix"]+"/rm"].split()

	def set_linuxrc(self):
		if self.settings["spec_prefix"]+"/linuxrc" in self.settings:
			if isinstance(self.settings[self.settings['spec_prefix']+'/linuxrc'], str):
				self.settings["linuxrc"]=\
					self.settings[self.settings["spec_prefix"]+"/linuxrc"]
				del self.settings[self.settings["spec_prefix"]+"/linuxrc"]

	def set_busybox_config(self):
		if self.settings["spec_prefix"]+"/busybox_config" in self.settings:
			if isinstance(self.settings[self.settings['spec_prefix']+'/busybox_config'], str):
				self.settings["busybox_config"]=\
					self.settings[self.settings["spec_prefix"]+"/busybox_config"]
				del self.settings[self.settings["spec_prefix"]+"/busybox_config"]

	def set_portage_overlay(self):
		if "portage_overlay" in self.settings:
			if isinstance(self.settings['portage_overlay'], str):
				self.settings["portage_overlay"]=\
					self.settings["portage_overlay"].split()
			log.info('portage_overlay directories are set to: %s',
				' '.join(self.settings['portage_overlay']))

	def set_overlay(self):
		if self.settings["spec_prefix"]+"/overlay" in self.settings:
			if isinstance(self.settings[self.settings['spec_prefix']+'/overlay'], str):
				self.settings[self.settings["spec_prefix"]+"/overlay"]=\
					self.settings[self.settings["spec_prefix"]+\
					"/overlay"].split()

	def set_root_overlay(self):
		if self.settings["spec_prefix"]+"/root_overlay" in self.settings:
			if isinstance(self.settings[self.settings['spec_prefix']+'/root_overlay'], str):
				self.settings[self.settings["spec_prefix"]+"/root_overlay"]=\
					self.settings[self.settings["spec_prefix"]+\
					"/root_overlay"].split()

	def set_root_path(self):
		""" ROOT= variable for emerges """
		self.settings["root_path"]="/"

	def set_valid_build_kernel_vars(self,addlargs):
		if "boot/kernel" in addlargs:
			if isinstance(addlargs['boot/kernel'], str):
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
				self.valid_values.append("boot/kernel/"+x+"/kernelopts")
				if "boot/kernel/"+x+"/packages" in addlargs:
					if isinstance(addlargs['boot/kernel/'+x+'/packages'], str):
						addlargs["boot/kernel/"+x+"/packages"]=\
							[addlargs["boot/kernel/"+x+"/packages"]]

	def set_build_kernel_vars(self):
		if self.settings["spec_prefix"]+"/gk_mainargs" in self.settings:
			self.settings["gk_mainargs"]=\
				self.settings[self.settings["spec_prefix"]+"/gk_mainargs"]
			del self.settings[self.settings["spec_prefix"]+"/gk_mainargs"]

	def kill_chroot_pids(self):
		log.info('Checking for processes running in chroot and killing them.')

		# Force environment variables to be exported so script can see them
		self.setup_environment()

		killcmd = normpath(self.settings["sharedir"] +
			self.settings["shdir"] + "/support/kill-chroot-pids.sh")
		if os.path.exists(killcmd):
			cmd([killcmd], env=self.env)

	def mount_safety_check(self):
		"""
		Check and verify that none of our paths in mypath are mounted. We don't
		want to clean up with things still mounted, and this allows us to check.
		Returns 1 on ok, 0 on "something is still mounted" case.
		"""

		if not os.path.exists(self.settings["chroot_path"]):
			return

		log.debug('self.mounts = %s', self.mounts)
		for x in self.mounts:
			target = normpath(self.settings["chroot_path"] + self.target_mounts[x])
			log.debug('mount_safety_check() x = %s %s', x, target)
			if not os.path.exists(target):
				continue

			if ismount(target):
				# Something is still mounted
				try:
					log.warning('%s is still mounted; performing auto-bind-umount...', target)
					# Try to umount stuff ourselves
					self.unbind()
					if ismount(target):
						raise CatalystError("Auto-unbind failed for " + target)
					else:
						log.notice('Auto-unbind successful...')
				except CatalystError:
					raise CatalystError("Unable to auto-unbind " + target)

	def unpack(self):
		_unpack=True

		clst_unpack_hash = self.resume.get("unpack")

		unpack_info = self.decompressor.create_infodict(
			source=self.settings["source_path"],
			destination=self.settings["chroot_path"],
			arch=self.settings["compressor_arch"],
			other_options=self.settings["compressor_options"],
			)

		display_msg = (
			'Starting %(mode)s from %(source)s\nto '
			'%(destination)s (this may take some time) ..')

		error_msg="'%(mode)s' extraction of %(source)s to %(destination)s failed."

		if "seedcache" in self.settings["options"]:
			if os.path.isdir(unpack_info["source"]):
				# SEEDCACHE Is a directory, use rsync
				unpack_info['mode'] = "rsync"
			else:
				# SEEDCACHE is a not a directory, try untar'ing
				log.notice('Referenced SEEDCACHE does not appear to be a directory, trying to untar...')
				unpack_info['source'] = file_check(unpack_info['source'])
		else:
			# No SEEDCACHE, use tar
			unpack_info['source'] = file_check(unpack_info['source'])
		# endif "seedcache"

		if "autoresume" in self.settings["options"]:
			if os.path.isdir(self.settings["source_path"]) \
				and self.resume.is_enabled("unpack"):
				# Autoresume is valid, SEEDCACHE is valid
				_unpack=False
				invalid_snapshot=False

			elif os.path.isfile(self.settings["source_path"]) \
				and self.settings["source_path_hash"]==clst_unpack_hash:
				# Autoresume is valid, tarball is valid
				_unpack=False
				invalid_snapshot=False

			elif os.path.isdir(self.settings["source_path"]) \
				and self.resume.is_disabled("unpack"):
				# Autoresume is invalid, SEEDCACHE
				_unpack=True
				invalid_snapshot=True

			elif os.path.isfile(self.settings["source_path"]) \
				and self.settings["source_path_hash"]!=clst_unpack_hash:
				# Autoresume is invalid, tarball
				_unpack=True
				invalid_snapshot=True
				unpack_info['source'] = file_check(unpack_info['source'])

		else:
			# No autoresume, SEEDCACHE
			if "seedcache" in self.settings["options"]:
				# SEEDCACHE so let's run rsync and let it clean up
				if os.path.isdir(self.settings["source_path"]):
					_unpack=True
					invalid_snapshot=False
				elif os.path.isfile(self.settings["source_path"]):
					# Tarball so unpack and remove anything already there
					_unpack=True
					invalid_snapshot=True
				# No autoresume, no SEEDCACHE
			else:
				# Tarball so unpack and remove anything already there
				if os.path.isfile(self.settings["source_path"]):
					_unpack=True
					invalid_snapshot=True
				elif os.path.isdir(self.settings["source_path"]):
					# We should never reach this, so something is very wrong
					raise CatalystError(
						"source path is a dir but seedcache is not enabled: %s"
						% self.settings["source_path"])

		if _unpack:
			self.mount_safety_check()

			if invalid_snapshot:
				if "autoresume" in self.settings["options"]:
					log.notice('No Valid Resume point detected, cleaning up...')

				self.clear_autoresume()
				self.clear_chroot()

			ensure_dirs(self.settings["chroot_path"])

			ensure_dirs(self.settings["chroot_path"]+"/tmp",mode=1777)

			if "pkgcache" in self.settings["options"]:
				ensure_dirs(self.settings["pkgcache_path"],mode=0o755)

			if "kerncache" in self.settings["options"]:
				ensure_dirs(self.settings["kerncache_path"],mode=0o755)

			log.notice('%s', display_msg % unpack_info)

			# now run the decompressor
			if not self.decompressor.extract(unpack_info):
				log.error('%s', error_msg % unpack_info)

			if "source_path_hash" in self.settings:
				self.resume.enable("unpack",
					data=self.settings["source_path_hash"])
			else:
				self.resume.enable("unpack")
		else:
			log.notice('Resume point detected, skipping unpack operation...')

	def unpack_snapshot(self):
		unpack=True
		snapshot_hash = self.resume.get("unpack_portage")

		unpack_errmsg="Error unpacking snapshot using mode %(mode)s"

		unpack_info = self.decompressor.create_infodict(
			source=self.settings["snapshot_path"],
			destination=self.settings["snapshot_cache_path"],
			arch=self.settings["compressor_arch"],
			other_options=self.settings["compressor_options"],
			)

		target_portdir = normpath(self.settings["chroot_path"] +
			self.settings["repo_basedir"] + "/" + self.settings["repo_name"])
		log.info('%s', self.settings['chroot_path'])
		log.info('unpack(), target_portdir = %s', target_portdir)
		if "snapcache" in self.settings["options"]:
			snapshot_cache_hash_path = pjoin(
				self.settings['snapshot_cache_path'], 'catalyst-hash')
			snapshot_cache_hash = fileutils.readfile(snapshot_cache_hash_path, True)
			unpack_info['mode'] = self.decompressor.determine_mode(
				unpack_info['source'])

			cleanup_msg="Cleaning up invalid snapshot cache at \n\t"+\
				self.settings["snapshot_cache_path"]+\
				" (this can take a long time)..."

			if self.settings["snapshot_path_hash"]==snapshot_cache_hash:
				log.info('Valid snapshot cache, skipping unpack of portage tree...')
				unpack=False
		else:
			cleanup_msg=\
				'Cleaning up existing portage tree (this can take a long time)...'
			unpack_info['destination'] = normpath(
				self.settings["chroot_path"] + self.settings["repo_basedir"])
			unpack_info['mode'] = self.decompressor.determine_mode(
				unpack_info['source'])

			if "autoresume" in self.settings["options"] \
				and os.path.exists(target_portdir) \
				and self.resume.is_enabled("unpack_portage") \
				and self.settings["snapshot_path_hash"] == snapshot_hash:
				log.notice('Valid Resume point detected, skipping unpack of portage tree...')
				unpack = False

		if unpack:
			if "snapcache" in self.settings["options"]:
				self.snapcache_lock.write_lock()
			if os.path.exists(target_portdir):
				log.info('%s', cleanup_msg)
			clear_dir(target_portdir)

			log.notice('Unpacking portage tree (this can take a long time) ...')
			if not self.decompressor.extract(unpack_info):
				log.error('%s', unpack_errmsg % unpack_info)

			if "snapcache" in self.settings["options"]:
				with open(snapshot_cache_hash_path, 'w') as myf:
					myf.write(self.settings["snapshot_path_hash"])
			else:
				log.info('Setting snapshot autoresume point')
				self.resume.enable("unpack_portage",
					data=self.settings["snapshot_path_hash"])

			if "snapcache" in self.settings["options"]:
				self.snapcache_lock.unlock()

	def config_profile_link(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("config_profile_link"):
			log.notice('Resume point detected, skipping config_profile_link operation...')
		else:
			# TODO: zmedico and I discussed making this a directory and pushing
			# in a parent file, as well as other user-specified configuration.
			log.info('Configuring profile link...')
			clear_path(self.settings['chroot_path'] +
				self.settings['port_conf'] + '/make.profile')
			ensure_dirs(self.settings['chroot_path'] + self.settings['port_conf'])
			cmd(['ln', '-sf',
				'../..' + self.settings['portdir'] + '/profiles/' + self.settings['target_profile'],
				self.settings['chroot_path'] + self.settings['port_conf'] + '/make.profile'],
				env=self.env)
			self.resume.enable("config_profile_link")

	def setup_confdir(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("setup_confdir"):
			log.notice('Resume point detected, skipping setup_confdir operation...')
		else:
			if "portage_confdir" in self.settings:
				log.info('Configuring %s...', self.settings['port_conf'])
				dest = normpath(self.settings['chroot_path'] + '/' + self.settings['port_conf'])
				ensure_dirs(dest)
				# The trailing slashes on both paths are important:
				# We want to make sure rsync copies the dirs into each
				# other and not as subdirs.
				cmd(['rsync', '-a', self.settings['portage_confdir'] + '/', dest + '/'],
					env=self.env)
				self.resume.enable("setup_confdir")

	def portage_overlay(self):
		""" We copy the contents of our overlays to /usr/local/portage """
		if "portage_overlay" in self.settings:
			for x in self.settings["portage_overlay"]:
				if os.path.exists(x):
					log.info('Copying overlay dir %s', x)
					ensure_dirs(self.settings['chroot_path'] + self.settings['local_overlay'])
					cmd("cp -a "+x+"/* "+self.settings["chroot_path"]+\
						self.settings["local_overlay"],\
						env=self.env)

	def root_overlay(self):
		""" Copy over the root_overlay """
		if self.settings["spec_prefix"]+"/root_overlay" in self.settings:
			for x in self.settings[self.settings["spec_prefix"]+\
				"/root_overlay"]:
				if os.path.exists(x):
					log.info('Copying root_overlay: %s', x)
					cmd(['rsync', '-a', x + '/', self.settings['chroot_path']],
						env=self.env)

	def base_dirs(self):
		pass

	def bind(self):
		for x in self.mounts:
			log.debug('bind(); x = %s', x)
			target = normpath(self.settings["chroot_path"] + self.target_mounts[x])
			ensure_dirs(target, mode=0o755)

			if not os.path.exists(self.mountmap[x]):
				if self.mountmap[x] not in ["tmpfs", "shmfs"]:
					ensure_dirs(self.mountmap[x], mode=0o755)

			src=self.mountmap[x]
			log.debug('bind(); src = %s', src)
			if "snapcache" in self.settings["options"] and x == "portdir":
				self.snapcache_lock.read_lock()
			_cmd = None
			if os.uname()[0] == "FreeBSD":
				if src == "/dev":
					_cmd = ['mount', '-t', 'devfs', 'none', target]
				else:
					_cmd = ['mount_nullfs', src, target]
			else:
				if src == "tmpfs":
					if "var_tmpfs_portage" in self.settings:
						_cmd = ['mount', '-t', 'tmpfs',
							'-o', 'size=' + self.settings['var_tmpfs_portage'] + 'G',
							src, target]
				elif src == "shmfs":
					_cmd = ['mount', '-t', 'tmpfs', '-o', 'noexec,nosuid,nodev', 'shm', target]
				else:
					_cmd = ['mount', '--bind', src, target]
			if _cmd:
				log.debug('bind(); _cmd = %s', _cmd)
				cmd(_cmd, env=self.env, fail_func=self.unbind)
		log.debug('bind(); finished :D')

	def unbind(self):
		ouch=0
		mypath=self.settings["chroot_path"]
		myrevmounts=self.mounts[:]
		myrevmounts.reverse()
		# Unmount in reverse order for nested bind-mounts
		for x in myrevmounts:
			target = normpath(mypath + self.target_mounts[x])
			if not os.path.exists(target):
				continue

			if not ismount(target):
				continue

			try:
				cmd(['umount', target])
			except CatalystError:
				log.warning('First attempt to unmount failed: %s', target)
				log.warning('Killing any pids still running in the chroot')

				self.kill_chroot_pids()

				try:
					cmd(['umount', target])
				except CatalystError:
					ouch=1
					log.warning("Couldn't umount bind mount: %s", target)

			if "snapcache" in self.settings["options"] and x == "/usr/portage":
				try:
					# It's possible the snapshot lock object isn't created yet.
					# This is because mount safety check calls unbind before the
					# target is fully initialized
					self.snapcache_lock.unlock()
				except Exception:
					pass
		if ouch:
			# if any bind mounts really failed, then we need to raise
			# this to potentially prevent an upcoming bash stage cleanup script
			# from wiping our bind mounts.
			raise CatalystError(
				"Couldn't umount one or more bind-mounts; aborting for safety.")

	def chroot_setup(self):
		self.makeconf=read_makeconf(normpath(self.settings["chroot_path"]+
			self.settings["make_conf"]))
		self.override_cbuild()
		self.override_chost()
		self.override_cflags()
		self.override_cxxflags()
		self.override_fcflags()
		self.override_fflags()
		self.override_ldflags()
		self.override_asflags()
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("chroot_setup"):
			log.notice('Resume point detected, skipping chroot_setup operation...')
		else:
			log.notice('Setting up chroot...')

			shutil.copy('/etc/resolv.conf', self.settings['chroot_path'] + '/etc/')

			# Copy over the envscript, if applicable
			if "envscript" in self.settings:
				if not os.path.exists(self.settings["envscript"]):
					raise CatalystError(
						"Can't find envscript " + self.settings["envscript"],
						print_traceback=True)

				log.warning(
					'Overriding certain env variables may cause catastrophic failure.\n'
					'If your build fails look here first as the possible problem.\n'
					'Catalyst assumes you know what you are doing when setting these variables.\n'
					'Catalyst Maintainers use VERY minimal envscripts, if used at all.\n'
					'You have been warned.')

				shutil.copy(self.settings['envscript'],
					self.settings['chroot_path'] + '/tmp/envscript')

			# Copy over /etc/hosts from the host in case there are any
			# specialties in there
			hosts_file = self.settings['chroot_path'] + '/etc/hosts'
			if os.path.exists(hosts_file):
				os.rename(hosts_file, hosts_file + '.catalyst')
				shutil.copy('/etc/hosts', hosts_file)

			# Modify and write out make.conf (for the chroot)
			makepath = normpath(self.settings["chroot_path"] +
				self.settings["make_conf"])
			clear_path(makepath)
			myf=open(makepath, "w")
			myf.write("# These settings were set by the catalyst build script "
					"that automatically\n# built this stage.\n")
			myf.write("# Please consult "
					"/usr/share/portage/config/make.conf.example "
					"for a more\n# detailed example.\n")

			for flags in ["CFLAGS", "CXXFLAGS", "FCFLAGS", "FFLAGS", "LDFLAGS",
						"ASFLAGS"]:
				if not flags in self.settings:
					continue
				if flags in ["LDFLAGS", "ASFLAGS"]:
					myf.write("# %s is unsupported.  USE AT YOUR OWN RISK!\n"
							% flags)
				if (flags is not "CFLAGS" and
					self.settings[flags] == self.settings["CFLAGS"]):
					myf.write('%s="${CFLAGS}"\n' % flags)
				elif isinstance(self.settings[flags], list):
					myf.write('%s="%s"\n'
							% (flags, ' '.join(self.settings[flags])))
				else:
					myf.write('%s="%s"\n'
							% (flags, self.settings[flags]))

			if "CBUILD" in self.settings:
				myf.write("# This should not be changed unless you know exactly"
					" what you are doing.  You\n# should probably be "
					"using a different stage, instead.\n")
				myf.write('CBUILD="'+self.settings["CBUILD"]+'"\n')

			if "CHOST" in self.settings:
				myf.write("# WARNING: Changing your CHOST is not something "
					"that should be done lightly.\n# Please consult "
					"https://wiki.gentoo.org/wiki/Changing_the_CHOST_variable "
					"before changing.\n")
				myf.write('CHOST="'+self.settings["CHOST"]+'"\n')

			# Figure out what our USE vars are for building
			myusevars=[]
			if "HOSTUSE" in self.settings:
				myusevars.extend(self.settings["HOSTUSE"])

			if "use" in self.settings:
				myusevars.extend(self.settings["use"])

			if myusevars:
				myf.write("# These are the USE and USE_EXPAND flags that were "
						"used for\n# building in addition to what is provided "
						"by the profile.\n")
				myusevars = sorted(set(myusevars))
				myf.write('USE="' + ' '.join(myusevars) + '"\n')
				if '-*' in myusevars:
					log.warning(
						'The use of -* in %s/use will cause portage to ignore\n'
						'package.use in the profile and portage_confdir.\n'
						"You've been warned!", self.settings['spec_prefix'])

			myuseexpandvars={}
			if "HOSTUSEEXPAND" in self.settings:
				for hostuseexpand in self.settings["HOSTUSEEXPAND"]:
					myuseexpandvars.update({hostuseexpand:self.settings["HOSTUSEEXPAND"][hostuseexpand]})

			if myuseexpandvars:
				for hostuseexpand in myuseexpandvars:
					myf.write(hostuseexpand + '="' + ' '.join(myuseexpandvars[hostuseexpand]) + '"\n')

			myf.write('PORTDIR="%s"\n' % self.settings['portdir'])
			myf.write('DISTDIR="%s"\n' % self.settings['distdir'])
			myf.write('PKGDIR="%s"\n' % self.settings['packagedir'])

			# Setup the portage overlay
			if "portage_overlay" in self.settings:
				myf.write('PORTDIR_OVERLAY="%s"\n' %  self.settings["local_overlay"])

			# Set default locale for system responses. #478382
			myf.write(
				'\n'
				'# This sets the language of build output to English.\n'
				'# Please keep this setting intact when reporting bugs.\n'
				'LC_MESSAGES=C\n')

			myf.close()
			self.resume.enable("chroot_setup")

	def fsscript(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("fsscript"):
			log.notice('Resume point detected, skipping fsscript operation...')
		else:
			if "fsscript" in self.settings:
				if os.path.exists(self.settings["controller_file"]):
					cmd([self.settings['controller_file'], 'fsscript'],
						env=self.env)
					self.resume.enable("fsscript")

	def rcupdate(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("rcupdate"):
			log.notice('Resume point detected, skipping rcupdate operation...')
		else:
			if os.path.exists(self.settings["controller_file"]):
				cmd([self.settings['controller_file'], 'rc-update'],
					env=self.env)
				self.resume.enable("rcupdate")

	def clean(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("clean"):
			log.notice('Resume point detected, skipping clean operation...')
		else:
			for x in self.settings["cleanables"]:
				log.notice('Cleaning chroot: %s', x)
				clear_path(self.settings["destpath"] + x)

		# Put /etc/hosts back into place
		hosts_file = self.settings['chroot_path'] + '/etc/hosts'
		if os.path.exists(hosts_file + '.catalyst'):
			os.rename(hosts_file + '.catalyst', hosts_file)

		# Remove our overlay
		if os.path.exists(self.settings["chroot_path"] + self.settings["local_overlay"]):
			clear_path(self.settings["chroot_path"] + self.settings["local_overlay"])

			make_conf = self.settings['chroot_path'] + self.settings['make_conf']
			try:
				with open(make_conf) as f:
					data = f.readlines()
				data = ''.join(x for x in data if not x.startswith('PORTDIR_OVERLAY'))
				with open(make_conf, 'w') as f:
					f.write(data)
			except OSError as e:
				raise CatalystError('Could not update %s: %s' % (make_conf, e))

		# Clean up old and obsoleted files in /etc
		if os.path.exists(self.settings["stage_path"]+"/etc"):
			cmd(['find', self.settings['stage_path'] + '/etc',
				'-maxdepth', '1', '-name', '*-', '-delete'],
				env=self.env)

		if os.path.exists(self.settings["controller_file"]):
			cmd([self.settings['controller_file'], 'clean'], env=self.env)
			self.resume.enable("clean")

	def empty(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("empty"):
			log.notice('Resume point detected, skipping empty operation...')
		else:
			if self.settings["spec_prefix"]+"/empty" in self.settings:
				if isinstance(self.settings[self.settings['spec_prefix']+'/empty'], str):
					self.settings[self.settings["spec_prefix"]+"/empty"]=\
						self.settings[self.settings["spec_prefix"]+\
						"/empty"].split()
				for x in self.settings[self.settings["spec_prefix"]+"/empty"]:
					myemp=self.settings["destpath"]+x
					if not os.path.isdir(myemp) or os.path.islink(myemp):
						log.warning('not a directory or does not exist, skipping "empty" operation: %s', x)
						continue
					log.info('Emptying directory %s', x)
					clear_dir(myemp)
			self.resume.enable("empty")

	def remove(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("remove"):
			log.notice('Resume point detected, skipping remove operation...')
		else:
			if self.settings["spec_prefix"]+"/rm" in self.settings:
				for x in self.settings[self.settings["spec_prefix"]+"/rm"]:
					# We're going to shell out for all these cleaning
					# operations, so we get easy glob handling.
					log.notice('livecd: removing %s', x)
					clear_path(self.settings["chroot_path"] + x)
				try:
					if os.path.exists(self.settings["controller_file"]):
						cmd([self.settings['controller_file'], 'clean'],
							env=self.env)
						self.resume.enable("remove")
				except:
					self.unbind()
					raise

	def preclean(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("preclean"):
			log.notice('Resume point detected, skipping preclean operation...')
		else:
			try:
				if os.path.exists(self.settings["controller_file"]):
					cmd([self.settings['controller_file'], 'preclean'],
						env=self.env)
					self.resume.enable("preclean")

			except:
				self.unbind()
				raise CatalystError("Build failed, could not execute preclean")

	def capture(self):
		# initialize it here so it doesn't use
		# resources if it is not needed
		if not self.compressor:
			self.compressor = CompressMap(self.settings["compress_definitions"],
				env=self.env, default_mode=self.settings['compression_mode'],
				comp_prog=self.settings['comp_prog'])

		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("capture"):
			log.notice('Resume point detected, skipping capture operation...')
		else:
			log.notice('Capture target in a tarball')
			# Remove filename from path
			mypath = os.path.dirname(self.settings["target_path"].rstrip('/'))

			# Now make sure path exists
			ensure_dirs(mypath)

			pack_info = self.compressor.create_infodict(
				source=".",
				basedir=self.settings["stage_path"],
				filename=self.settings["target_path"].rstrip('/'),
				mode=self.settings["compression_mode"],
				auto_extension=True,
				arch=self.settings["compressor_arch"],
				other_options=self.settings["compressor_options"],
				)
			target_filename = ".".join([self.settings["target_path"].rstrip('/'),
				self.compressor.extension(pack_info['mode'])])

			log.notice('Creating stage tarball... mode: %s',
				self.settings['compression_mode'])

			if self.compressor.compress(pack_info):
				self.gen_contents_file(target_filename)
				self.gen_digest_file(target_filename)
				self.resume.enable("capture")
			else:
				log.warning("Couldn't create stage tarball: %s", target_filename)

	def run_local(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("run_local"):
			log.notice('Resume point detected, skipping run_local operation...')
		else:
			try:
				if os.path.exists(self.settings["controller_file"]):
					log.info('run_local() starting controller script...')
					cmd([self.settings['controller_file'], 'run'],
						env=self.env)
					self.resume.enable("run_local")
				else:
					log.info('run_local() no controller_file found... %s',
						self.settings['controller_file'])

			except CatalystError:
				self.unbind()
				raise CatalystError("Stage build aborting due to error.",
					print_traceback=False)

	def setup_environment(self):
		"""
		Modify the current environment. This is an ugly hack that should be
		fixed. We need this to use the os.system() call since we can't
		specify our own environ
		"""
		log.debug('setup_environment(); settings = %r', self.settings)
		for x in list(self.settings):
			log.debug('setup_environment(); processing: %s', x)
			if x == "options":
				#self.env['clst_' + x] = ' '.join(self.settings[x])
				for opt in self.settings[x]:
					self.env['clst_' + opt.upper()] = "true"
				continue
			# Sanitize var names by doing "s|/-.|_|g"
			varname = "clst_" + x.replace("/", "_")
			varname = varname.replace("-", "_")
			varname = varname.replace(".", "_")
			if isinstance(self.settings[x], str):
				# Prefix to prevent namespace clashes
				#os.environ[varname] = self.settings[x]
				if "path" in x:
					self.env[varname] = self.settings[x].rstrip("/")
				else:
					self.env[varname] = self.settings[x]
			elif isinstance(self.settings[x], list):
				#os.environ[varname] = ' '.join(self.settings[x])
				self.env[varname] = ' '.join(self.settings[x])
			elif isinstance(self.settings[x], bool):
				if self.settings[x]:
					self.env[varname] = "true"
				else:
					self.env[varname] = "false"
			# This handles a dictionary of objects just one level deep and no deeper!
			# Its currently used only for USE_EXPAND flags which are dictionaries of
			# lists in arch/amd64.py and friends.  If we wanted self.settigs[var]
			# of any depth, we should make this function recursive.
			elif isinstance(self.settings[x], dict):
				if x in ["compress_definitions",
					"decompress_definitions"]:
					continue
				self.env[varname] = ' '.join(self.settings[x].keys())
				for y in self.settings[x].keys():
					varname2 = "clst_" + y.replace("/", "_")
					varname2 = varname2.replace("-", "_")
					varname2 = varname2.replace(".", "_")
					if isinstance(self.settings[x][y], str):
						self.env[varname2] = self.settings[x][y]
					elif isinstance(self.settings[x][y], list):
						self.env[varname2] = ' '.join(self.settings[x][y])
					elif isinstance(self.settings[x][y], bool):
						if self.settings[x][y]:
							self.env[varname] = "true"
						else:
							self.env[varname] = "false"

		if "makeopts" in self.settings:
			self.env["MAKEOPTS"]=self.settings["makeopts"]
		log.debug('setup_environment(); env = %r', self.env)

	def run(self):
		self.chroot_lock.write_lock()

		# Kill any pids in the chroot
		self.kill_chroot_pids()

		# Check for mounts right away and abort if we cannot unmount them
		self.mount_safety_check()

		if "clear-autoresume" in self.settings["options"]:
			self.clear_autoresume()

		if "purgetmponly" in self.settings["options"]:
			self.purge()
			return

		if "purgeonly" in self.settings["options"]:
			log.info('StageBase: run() purgeonly')
			self.purge()

		if "purge" in self.settings["options"]:
			log.info('StageBase: run() purge')
			self.purge()

		failure = False
		for x in self.settings["action_sequence"]:
			log.notice('--- Running action sequence: %s', x)
			sys.stdout.flush()
			try:
				getattr(self, x)()
			except LockInUse:
				log.error('Unable to aquire the lock...')
				failure = True
				break
			except Exception:
				log.error('Exception running action sequence %s', x, exc_info=True)
				failure = True
				break

		if failure:
			log.notice('Cleaning up... Running unbind()')
			self.unbind()
			return False
		return True


	def unmerge(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("unmerge"):
			log.notice('Resume point detected, skipping unmerge operation...')
		else:
			if self.settings["spec_prefix"]+"/unmerge" in self.settings:
				if isinstance(self.settings[self.settings['spec_prefix']+'/unmerge'], str):
					self.settings[self.settings["spec_prefix"]+"/unmerge"]=\
						[self.settings[self.settings["spec_prefix"]+"/unmerge"]]

				# Before cleaning, unmerge stuff
				try:
					cmd([self.settings['controller_file'], 'unmerge'] +
						self.settings[self.settings['spec_prefix'] + '/unmerge'],
						env=self.env)
					log.info('unmerge shell script')
				except CatalystError:
					self.unbind()
					raise
				self.resume.enable("unmerge")

	def target_setup(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("target_setup"):
			log.notice('Resume point detected, skipping target_setup operation...')
		else:
			log.notice('Setting up filesystems per filesystem type')
			cmd([self.settings['controller_file'], 'target_image_setup',
				self.settings['target_path']], env=self.env)
			self.resume.enable("target_setup")

	def setup_overlay(self):
		if "autoresume" in self.settings["options"] \
		and self.resume.is_enabled("setup_overlay"):
			log.notice('Resume point detected, skipping setup_overlay operation...')
		else:
			if self.settings["spec_prefix"]+"/overlay" in self.settings:
				for x in self.settings[self.settings["spec_prefix"]+"/overlay"]:
					if os.path.exists(x):
						cmd(['rsync', '-a', x + '/', self.settings['target_path']],
							env=self.env)
				self.resume.enable("setup_overlay")

	def create_iso(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("create_iso"):
			log.notice('Resume point detected, skipping create_iso operation...')
		else:
			# Create the ISO
			if "iso" in self.settings:
				cmd([self.settings['controller_file'], 'iso', self.settings['iso']],
					env=self.env)
				self.gen_contents_file(self.settings["iso"])
				self.gen_digest_file(self.settings["iso"])
				self.resume.enable("create_iso")
			else:
				log.warning('livecd/iso was not defined.  An ISO Image will not be created.')

	def build_packages(self):
		build_packages_resume = pjoin(self.settings["autoresume_path"],
			"build_packages")
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("build_packages"):
			log.notice('Resume point detected, skipping build_packages operation...')
		else:
			if self.settings["spec_prefix"]+"/packages" in self.settings:
				if "autoresume" in self.settings["options"] \
					and self.resume.is_enabled("build_packages"):
					log.notice('Resume point detected, skipping build_packages operation...')
				else:
					try:
						cmd([self.settings['controller_file'], 'build_packages'] +
							self.settings[self.settings["spec_prefix"] + '/packages'],
							env=self.env)
						fileutils.touch(build_packages_resume)
						self.resume.enable("build_packages")
					except CatalystError:
						self.unbind()
						raise CatalystError(self.settings["spec_prefix"]+\
							"build aborting due to error.")

	def build_kernel(self):
		'''Build all configured kernels'''
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("build_kernel"):
			log.notice('Resume point detected, skipping build_kernel operation...')
		else:
			if "boot/kernel" in self.settings:
				try:
					mynames=self.settings["boot/kernel"]
					if isinstance(mynames, str):
						mynames=[mynames]
					# Execute the script that sets up the kernel build environment
					cmd([self.settings['controller_file'], 'pre-kmerge'],
						env=self.env)
					for kname in mynames:
						self._build_kernel(kname=kname)
					self.resume.enable("build_kernel")
				except CatalystError:
					self.unbind()
					raise CatalystError(
						"build aborting due to kernel build error.",
						print_traceback=True)

	def _build_kernel(self, kname):
		"Build a single configured kernel by name"
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("build_kernel_"+kname):
			log.notice('Resume point detected, skipping build_kernel for %s operation...', kname)
			return
		self._copy_kernel_config(kname=kname)

		# If we need to pass special options to the bootloader
		# for this kernel put them into the environment
		key = 'boot/kernel/' + kname + '/kernelopts'
		if key in self.settings:
			myopts = self.settings[key]

			if not isinstance(myopts, str):
				myopts = ' '.join(myopts)
				self.env[kname+"_kernelopts"]=myopts
			else:
				self.env[kname+"_kernelopts"]=""

		key = 'boot/kernel/' + kname + '/extraversion'
		self.settings.setdefault(key, '')
		self.env["clst_kextraversion"] = self.settings[key]

		self._copy_initramfs_overlay(kname=kname)

		# Execute the script that builds the kernel
		cmd([self.settings['controller_file'], 'kernel', kname],
			env=self.env)

		if "boot/kernel/"+kname+"/initramfs_overlay" in self.settings:
			log.notice('Cleaning up temporary overlay dir')
			clear_dir(self.settings['chroot_path'] + '/tmp/initramfs_overlay/')

		self.resume.is_enabled("build_kernel_"+kname)

		# Execute the script that cleans up the kernel build environment
		cmd([self.settings['controller_file'], 'post-kmerge'],
			env=self.env)

	def _copy_kernel_config(self, kname):
		key = 'boot/kernel/' + kname + '/config'
		if key in self.settings:
			if not os.path.exists(self.settings[key]):
				self.unbind()
				raise CatalystError("Can't find kernel config: %s" %
					self.settings[key])

			try:
				shutil.copy(self.settings[key],
					self.settings['chroot_path'] + '/var/tmp/' + kname + '.config')

			except IOError:
				self.unbind()

	def _copy_initramfs_overlay(self, kname):
		key = 'boot/kernel/' + kname + '/initramfs_overlay'
		if key in self.settings:
			if os.path.exists(self.settings[key]):
				log.notice('Copying initramfs_overlay dir %s', self.settings[key])

				ensure_dirs(
					self.settings['chroot_path'] +
					'/tmp/initramfs_overlay/' + self.settings[key])

				cmd('cp -R ' + self.settings[key] + '/* ' +
					self.settings['chroot_path'] +
					'/tmp/initramfs_overlay/' + self.settings[key], env=self.env)

	def bootloader(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("bootloader"):
			log.notice('Resume point detected, skipping bootloader operation...')
		else:
			try:
				cmd([self.settings['controller_file'], 'bootloader',
					self.settings['target_path'].rstrip('/')],
					env=self.env)
				self.resume.enable("bootloader")
			except CatalystError:
				self.unbind()
				raise CatalystError("Script aborting due to error.")

	def livecd_update(self):
		if "autoresume" in self.settings["options"] \
			and self.resume.is_enabled("livecd_update"):
			log.notice('Resume point detected, skipping build_packages operation...')
		else:
			try:
				cmd([self.settings['controller_file'], 'livecd-update'],
					env=self.env)
				self.resume.enable("livecd_update")

			except CatalystError:
				self.unbind()
				raise CatalystError("build aborting due to livecd_update error.")

	@staticmethod
	def _debug_pause_():
		py_input("press any key to continue: ")

# vim: ts=4 sw=4 sta et sts=4 ai
