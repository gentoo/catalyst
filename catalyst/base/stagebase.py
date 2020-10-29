
import os
import platform
import shutil
import sys

from pathlib import Path

import libmount
import toml

from snakeoil import fileutils
from snakeoil.osutils import pjoin

from DeComp.compress import CompressMap

from catalyst import log
from catalyst.context import namespace
from catalyst.defaults import (confdefaults, MOUNT_DEFAULTS, PORT_LOGDIR_CLEAN)
from catalyst.support import (CatalystError, file_locate, normpath,
                              cmd, read_makeconf, ismount, file_check,
                              sanitize_name)
from catalyst.base.targetbase import TargetBase
from catalyst.base.clearbase import ClearBase
from catalyst.base.genbase import GenBase
from catalyst.lock import LockDir, LockInUse
from catalyst.fileops import ensure_dirs, clear_dir, clear_path
from catalyst.base.resume import AutoResume


class StageBase(TargetBase, ClearBase, GenBase):
    """
    This class does all of the chroot setup, copying of files, etc. It is
    the driver class for pretty much everything that Catalyst does.
    """

    def __init__(self, myspec, addlargs):
        self.required_values |= frozenset([
            "profile",
            "rel_type",
            "snapshot_treeish",
            "source_subpath",
            "subarch",
            "target",
            "version_stamp",
        ])
        self.valid_values |= self.required_values | frozenset([
            "asflags",
            "catalyst_use",
            "cbuild",
            "cflags",
            "common_flags",
            "compression_mode",
            "cxxflags",
            "decompressor_search_order",
            "fcflags",
            "fflags",
            "hostuse",
            "install_mask",
            "interpreter",
            "kerncache_path",
            "ldflags",
            "pkgcache_path",
            "portage_confdir",
            "portage_overlay",
            "portage_prefix",
        ])
        self.prepare_sequence = []
        self.build_sequence = []
        self.finish_sequence = []

        self.set_valid_build_kernel_vars(addlargs)
        TargetBase.__init__(self, myspec, addlargs)
        GenBase.__init__(self, myspec)
        ClearBase.__init__(self, myspec)

        self.makeconf = {}

        if "chost" in self.settings:
            host = self.settings["chost"].split("-")[0]
        else:
            host = self.settings["subarch"]
        self.settings["hostarch"] = host

        if "cbuild" in self.settings:
            build = self.settings["cbuild"].split("-")[0]
        else:
            build = platform.machine()
        self.settings["buildarch"] = build

        arch_dir = normpath(self.settings['sharedir'] + '/arch/')

        log.debug("Searching arch definitions...")
        for x in [x for x in os.listdir(arch_dir) if x.endswith('.toml')]:
            log.debug("\tTrying %s", x)
            name = x[:-len('.toml')]

            with open(arch_dir + x) as file:
                arch_config = toml.load(file)

                # Search for a subarchitecture in each arch in the arch_config
                for arch in [x for x in arch_config if x.startswith(name) and host in arch_config[x]]:
                    self.settings.update(arch_config[arch][host])
                    setarch = arch_config.get('setarch', {}).get(host, {})
                    break
                else:
                    # Didn't find a matching subarchitecture, keep searching
                    continue

            break
        else:
            raise CatalystError("Unknown host machine type " + host)

        if setarch.get('if_build', '') == platform.machine():
            chroot = f'setarch {setarch["arch"]} chroot'
        else:
            chroot = 'chroot'
        self.settings["CHROOT"] = chroot

        log.notice('Using target: %s', self.settings['target'])
        # Print a nice informational message
        if chroot.startswith('setarch'):
            log.info('Building on %s for alternate personality type %s',
                     build, host)
        else:
            log.info('Building natively for %s', host)

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
        log.notice("Accepted source file extensions search order: %s",
                   self.accepted_extensions)
        # save resources, it is not always needed
        self.compressor = None

        # Define all of our core variables
        self.set_target_profile()
        self.set_target_subpath()
        self.set_source_subpath()

        # Set paths
        self.set_snapshot()
        self.set_root_path()
        self.set_source_path()
        self.set_chroot_path()
        self.set_autoresume_path()
        self.set_dest_path()
        self.set_stage_path()
        self.set_target_path()

        self.set_controller_file()
        self.set_default_action_sequence()
        self.set_use()
        self.set_catalyst_use()
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

        # This next line checks to make sure that the specified variables exist on disk.
        # pdb.set_trace()
        file_locate(self.settings, ["distdir"], expand=0)
        # If we are using portage_confdir, check that as well.
        if "portage_confdir" in self.settings:
            file_locate(self.settings, ["portage_confdir"], expand=0)

        # Setup our mount points.
        self.mount = MOUNT_DEFAULTS.copy()

        self.mount['portdir']['source'] = self.snapshot
        self.mount['portdir']['target'] = self.settings['repo_basedir'] + '/' + self.settings['repo_name']
        self.mount['distdir']['source'] = self.settings['distdir']
        self.mount["distdir"]['target'] = self.settings['target_distdir']

        # Configure any user specified options (either in catalyst.conf or on
        # the command line).
        if "pkgcache" in self.settings["options"]:
            self.set_pkgcache_path()
            self.mount['pkgdir']['enable'] = True
            self.mount['pkgdir']['source'] = self.settings['pkgcache_path']
            self.mount['pkgdir']['target'] = self.settings["target_pkgdir"]
            log.info('Location of the package cache is %s',
                     self.settings['pkgcache_path'])

        if "kerncache" in self.settings["options"]:
            self.set_kerncache_path()
            self.mount['kerncache']['enable'] = True
            self.mount['kerncache']['source'] = self.settings["kerncache_path"]
            log.info('Location of the kerncache is %s',
                     self.settings['kerncache_path'])

        if "ccache" in self.settings["options"]:
            if "CCACHE_DIR" in os.environ:
                ccdir = os.environ["CCACHE_DIR"]
                del os.environ["CCACHE_DIR"]
            else:
                ccdir = "/var/tmp/ccache"
            if not os.path.isdir(ccdir):
                raise CatalystError(
                    "Compiler cache support can't be enabled (can't find " + ccdir+")")
            self.mount['ccache']['enable'] = True
            self.mount['ccache']['source'] = ccdir
            self.env["CCACHE_DIR"] = self.mount['ccache']['target']

        if "icecream" in self.settings["options"]:
            self.mount['icecream']['enable'] = True
            self.mount['icecream']['source'] = self.settings['icecream']
            self.env["PATH"] = self.mount['icecream']['target'] + \
                ":" + self.env["PATH"]

        if "port_logdir" in self.settings:
            self.mount['port_logdir']['enable'] = True
            self.mount['port_logdir']['source'] = self.settings['port_logdir']
            self.env["PORT_LOGDIR"] = self.settings["port_logdir"]
            self.env["PORT_LOGDIR_CLEAN"] = PORT_LOGDIR_CLEAN

    def override_cbuild(self):
        if "CBUILD" in self.makeconf:
            self.settings["CBUILD"] = self.makeconf["CBUILD"]

    def override_chost(self):
        if "CHOST" in self.makeconf:
            self.settings["CHOST"] = self.makeconf["CHOST"]

    def override_cflags(self):
        if "CFLAGS" in self.makeconf:
            self.settings["CFLAGS"] = self.makeconf["CFLAGS"]

    def override_cxxflags(self):
        if "CXXFLAGS" in self.makeconf:
            self.settings["CXXFLAGS"] = self.makeconf["CXXFLAGS"]

    def override_fcflags(self):
        if "FCFLAGS" in self.makeconf:
            self.settings["FCFLAGS"] = self.makeconf["FCFLAGS"]

    def override_fflags(self):
        if "FFLAGS" in self.makeconf:
            self.settings["FFLAGS"] = self.makeconf["FFLAGS"]

    def override_ldflags(self):
        if "LDFLAGS" in self.makeconf:
            self.settings["LDFLAGS"] = self.makeconf["LDFLAGS"]

    def override_asflags(self):
        if "ASFLAGS" in self.makeconf:
            self.settings["ASFLAGS"] = self.makeconf["ASFLAGS"]

    def override_common_flags(self):
        if "COMMON_FLAGS" in self.makeconf:
            self.settings["COMMON_FLAGS"] = self.makeconf["COMMON_FLAGS"]

    def set_install_mask(self):
        if "install_mask" in self.settings:
            if not isinstance(self.settings['install_mask'], str):
                self.settings["install_mask"] = \
                    ' '.join(self.settings["install_mask"])

    def set_spec_prefix(self):
        self.settings["spec_prefix"] = self.settings["target"]

    def set_target_profile(self):
        self.settings["target_profile"] = self.settings["profile"]

    def set_target_subpath(self):
        common = self.settings["rel_type"] + "/" + \
            self.settings["target"] + "-" + self.settings["subarch"]
        self.settings["target_subpath"] = \
            common + \
            "-" + self.settings["version_stamp"] + \
            "/"
        self.settings["target_subpath_unversioned"] = \
            common + \
            "/"

    def set_source_subpath(self):
        if not isinstance(self.settings['source_subpath'], str):
            raise CatalystError(
                "source_subpath should have been a string. Perhaps you have " +
                "something wrong in your spec file?")

    def set_pkgcache_path(self):
        if "pkgcache_path" in self.settings:
            if not isinstance(self.settings['pkgcache_path'], str):
                self.settings["pkgcache_path"] = \
                    normpath(self.settings["pkgcache_path"])
        elif "versioned_cache" in self.settings["options"]:
            self.settings["pkgcache_path"] = \
                normpath(self.settings["storedir"] + "/packages/" +
                         self.settings["target_subpath"] + "/")
        else:
            self.settings["pkgcache_path"] = \
                normpath(self.settings["storedir"] + "/packages/" +
                         self.settings["target_subpath_unversioned"] + "/")

    def set_kerncache_path(self):
        if "kerncache_path" in self.settings:
            if not isinstance(self.settings['kerncache_path'], str):
                self.settings["kerncache_path"] = \
                    normpath(self.settings["kerncache_path"])
        elif "versioned_cache" in self.settings["options"]:
            self.settings["kerncache_path"] = normpath(self.settings["storedir"] +
                                                       "/kerncache/" + self.settings["target_subpath"])
        else:
            self.settings["kerncache_path"] = normpath(self.settings["storedir"] +
                                                       "/kerncache/" + self.settings["target_subpath_unversioned"])

    def set_target_path(self):
        self.settings["target_path"] = normpath(self.settings["storedir"] +
                                                "/builds/" + self.settings["target_subpath"])
        if "autoresume" in self.settings["options"]\
                and self.resume.is_enabled("setup_target_path"):
            log.notice(
                'Resume point detected, skipping target path setup operation...')
            return

        self.resume.enable("setup_target_path")
        ensure_dirs(self.settings["storedir"] + "/builds")

    def set_fsscript(self):
        if self.settings["spec_prefix"] + "/fsscript" in self.settings:
            self.settings["fsscript"] = \
                self.settings[self.settings["spec_prefix"] + "/fsscript"]
            del self.settings[self.settings["spec_prefix"] + "/fsscript"]

    def set_rcadd(self):
        if self.settings["spec_prefix"] + "/rcadd" in self.settings:
            self.settings["rcadd"] = \
                self.settings[self.settings["spec_prefix"] + "/rcadd"]
            del self.settings[self.settings["spec_prefix"] + "/rcadd"]

    def set_rcdel(self):
        if self.settings["spec_prefix"] + "/rcdel" in self.settings:
            self.settings["rcdel"] = \
                self.settings[self.settings["spec_prefix"] + "/rcdel"]
            del self.settings[self.settings["spec_prefix"] + "/rcdel"]

    def set_cdtar(self):
        if self.settings["spec_prefix"] + "/cdtar" in self.settings:
            self.settings["cdtar"] = \
                normpath(
                    self.settings[self.settings["spec_prefix"] + "/cdtar"])
            del self.settings[self.settings["spec_prefix"] + "/cdtar"]

    def set_iso(self):
        if self.settings["spec_prefix"] + "/iso" in self.settings:
            if self.settings[self.settings["spec_prefix"] + "/iso"].startswith('/'):
                self.settings["iso"] = \
                    normpath(
                        self.settings[self.settings["spec_prefix"] + "/iso"])
            else:
                # This automatically prepends the build dir to the ISO output path
                # if it doesn't start with a /
                self.settings["iso"] = normpath(self.settings["storedir"] +
                                                "/builds/" + self.settings["rel_type"] + "/" +
                                                self.settings[self.settings["spec_prefix"] + "/iso"])
            del self.settings[self.settings["spec_prefix"] + "/iso"]

    def set_fstype(self):
        if self.settings["spec_prefix"] + "/fstype" in self.settings:
            self.settings["fstype"] = \
                self.settings[self.settings["spec_prefix"] + "/fstype"]
            del self.settings[self.settings["spec_prefix"] + "/fstype"]

        if "fstype" not in self.settings:
            self.settings["fstype"] = "squashfs"
            for x in self.valid_values:
                if x == self.settings["spec_prefix"] + "/fstype":
                    log.info('%s/fstype is being set to the default of "squashfs"',
                             self.settings['spec_prefix'])

    def set_fsops(self):
        if "fstype" in self.settings:
            self.valid_values |= {"fsops"}
            if self.settings["spec_prefix"] + "/fsops" in self.settings:
                self.settings["fsops"] = \
                    self.settings[self.settings["spec_prefix"] + "/fsops"]
                del self.settings[self.settings["spec_prefix"] + "/fsops"]

    def set_source_path(self):
        if "seedcache" in self.settings["options"]\
                and os.path.isdir(normpath(self.settings["storedir"] + "/tmp/" +
                                           self.settings["source_subpath"] + "/")):
            self.settings["source_path"] = normpath(self.settings["storedir"] +
                                                    "/tmp/" + self.settings["source_subpath"] + "/")
            log.debug("source_subpath is: %s", self.settings["source_path"])
        else:
            log.debug('Checking source path existence and '
                      'get the final filepath. subpath: %s',
                      self.settings["source_subpath"])
            self.settings["source_path"] = file_check(
                normpath(self.settings["storedir"] + "/builds/" +
                         self.settings["source_subpath"]),
                self.accepted_extensions,
            )
            log.debug('Source path returned from file_check is: %s',
                      self.settings["source_path"])
            if os.path.isfile(self.settings["source_path"]):
                # XXX: Is this even necessary if the previous check passes?
                if os.path.exists(self.settings["source_path"]):
                    self.settings["source_path_hash"] = \
                        self.generate_hash(self.settings["source_path"], "sha1")
        log.notice('Source path set to %s', self.settings['source_path'])

    def set_dest_path(self):
        if "root_path" in self.settings:
            self.settings["destpath"] = normpath(self.settings["chroot_path"] +
                                                 self.settings["root_path"])
        else:
            self.settings["destpath"] = normpath(self.settings["chroot_path"])

    def set_cleanables(self):
        self.settings['cleanables'] = [
            "/etc/resolv.conf",
            "/var/tmp/*",
            "/tmp/*",
        ]

    def set_chroot_path(self):
        """
        NOTE: the trailing slash has been removed
        Things *could* break if you don't use a proper join()
        """
        self.settings["chroot_path"] = normpath(self.settings["storedir"] +
                                                "/tmp/" + self.settings["target_subpath"].rstrip('/'))
        self.chroot_lock = LockDir(self.settings["chroot_path"])

    def set_autoresume_path(self):
        self.settings["autoresume_path"] = normpath(pjoin(
            self.settings["storedir"], "tmp", self.settings["rel_type"],
            ".autoresume-%s-%s-%s"
            % (self.settings["target"], self.settings["subarch"],
               self.settings["version_stamp"])
        ))
        if "autoresume" in self.settings["options"]:
            log.info('The autoresume path is %s',
                     self.settings['autoresume_path'])
        self.resume = AutoResume(self.settings["autoresume_path"], mode=0o755)

    def set_controller_file(self):
        self.settings["controller_file"] = normpath(self.settings["sharedir"] +
                                                    "/targets/" + self.settings["target"] + "/" + "controller.sh")

    def set_iso_volume_id(self):
        if self.settings["spec_prefix"] + "/volid" in self.settings:
            self.settings["iso_volume_id"] = \
                self.settings[self.settings["spec_prefix"] + "/volid"]
            if len(self.settings["iso_volume_id"]) > 32:
                raise CatalystError(
                    "ISO volume ID must not exceed 32 characters.")
        else:
            self.settings["iso_volume_id"] = "catalyst " + \
                self.settings['snapshot_treeish']

    def set_default_action_sequence(self):
        """ Default action sequence for run method.

        This method sets the optional purgeonly action sequence and returns.
        Or it calls the normal set_action_sequence() for the target stage.
        """
        if "purgeonly" in self.settings["options"]:
            self.build_sequence.append("remove_chroot")
            return
        self.set_action_sequence()

    def set_action_sequence(self):
        """Set basic stage1, 2, 3 action sequences"""
        self.prepare_sequence.extend([
            "unpack",
            "setup_confdir",
            "portage_overlay",
        ])
        self.build_sequence.extend([
            "bind",
            "chroot_setup",
            "setup_environment",
            "run_local",
            "preclean",
            "unbind",
        ])
        self.finish_sequence.extend([
            "clean",
        ])
        self.set_completion_action_sequences()

    def set_completion_action_sequences(self):
        if "fetch" not in self.settings["options"]:
            self.finish_sequence.append("capture")
        if "keepwork" in self.settings["options"]:
            self.finish_sequence.append("clear_autoresume")
        elif "seedcache" in self.settings["options"]:
            self.finish_sequence.append("remove_autoresume")
        else:
            self.finish_sequence.append("remove_autoresume")
            self.finish_sequence.append("remove_chroot")

    def set_use(self):
        use = self.settings["spec_prefix"] + "/use"
        if use in self.settings:
            if isinstance(self.settings[use], str):
                self.settings["use"] = self.settings[use].split()
            else:
                self.settings["use"] = self.settings[use]
            del self.settings[use]
        else:
            self.settings["use"] = []

    def set_catalyst_use(self):
        catalyst_use = self.settings["spec_prefix"] + "/catalyst_use"
        if catalyst_use in self.settings:
            if isinstance(self.settings[catalyst_use], str):
                self.settings["catalyst_use"] = self.settings[catalyst_use].split()
            else:
                self.settings["catalyst_use"] = self.settings[catalyst_use]
            del self.settings[catalyst_use]
        else:
            self.settings["catalyst_use"] = []

        # Force bindist when options ask for it
        if "bindist" in self.settings["options"]:
            log.debug("Enabling bindist USE flag")
            self.settings["catalyst_use"].append("bindist")

    def set_stage_path(self):
        self.settings["stage_path"] = normpath(self.settings["chroot_path"])

    def set_packages(self):
        pass

    def set_rm(self):
        if self.settings["spec_prefix"] + "/rm" in self.settings:
            if isinstance(self.settings[self.settings['spec_prefix'] + '/rm'], str):
                self.settings[self.settings["spec_prefix"] + "/rm"] = \
                    self.settings[self.settings["spec_prefix"] + "/rm"].split()

    def set_linuxrc(self):
        if self.settings["spec_prefix"] + "/linuxrc" in self.settings:
            if isinstance(self.settings[self.settings['spec_prefix'] + '/linuxrc'], str):
                self.settings["linuxrc"] = \
                    self.settings[self.settings["spec_prefix"] + "/linuxrc"]
                del self.settings[self.settings["spec_prefix"] + "/linuxrc"]

    def set_busybox_config(self):
        if self.settings["spec_prefix"] + "/busybox_config" in self.settings:
            if isinstance(self.settings[self.settings['spec_prefix'] + '/busybox_config'], str):
                self.settings["busybox_config"] = \
                    self.settings[self.settings["spec_prefix"] +
                                  "/busybox_config"]
                del self.settings[self.settings["spec_prefix"] +
                                  "/busybox_config"]

    def set_portage_overlay(self):
        if "portage_overlay" in self.settings:
            if isinstance(self.settings['portage_overlay'], str):
                self.settings["portage_overlay"] = \
                    self.settings["portage_overlay"].split()
            log.info('portage_overlay directories are set to: %s',
                     ' '.join(self.settings['portage_overlay']))

    def set_overlay(self):
        if self.settings["spec_prefix"] + "/overlay" in self.settings:
            if isinstance(self.settings[self.settings['spec_prefix'] + '/overlay'], str):
                self.settings[self.settings["spec_prefix"] + "/overlay"] = \
                    self.settings[self.settings["spec_prefix"] +
                                  "/overlay"].split()

    def set_root_overlay(self):
        if self.settings["spec_prefix"] + "/root_overlay" in self.settings:
            if isinstance(self.settings[self.settings['spec_prefix'] + '/root_overlay'], str):
                self.settings[self.settings["spec_prefix"] + "/root_overlay"] = \
                    self.settings[self.settings["spec_prefix"] +
                                  "/root_overlay"].split()

    def set_root_path(self):
        """ ROOT= variable for emerges """
        self.settings["root_path"] = "/"

    def set_valid_build_kernel_vars(self, addlargs):
        if "boot/kernel" in addlargs:
            if isinstance(addlargs['boot/kernel'], str):
                loopy = [addlargs["boot/kernel"]]
            else:
                loopy = addlargs["boot/kernel"]

            for x in loopy:
                self.valid_values |= frozenset([
                    "boot/kernel/" + x + "/aliases",
                    "boot/kernel/" + x + "/config",
                    "boot/kernel/" + x + "/console",
                    "boot/kernel/" + x + "/extraversion",
                    "boot/kernel/" + x + "/gk_action",
                    "boot/kernel/" + x + "/gk_kernargs",
                    "boot/kernel/" + x + "/initramfs_overlay",
                    "boot/kernel/" + x + "/kernelopts",
                    "boot/kernel/" + x + "/packages",
                    "boot/kernel/" + x + "/softlevel",
                    "boot/kernel/" + x + "/sources",
                    "boot/kernel/" + x + "/use",
                ])
                if "boot/kernel/" + x + "/packages" in addlargs:
                    if isinstance(addlargs['boot/kernel/' + x + '/packages'], str):
                        addlargs["boot/kernel/" + x + "/packages"] = \
                                [addlargs["boot/kernel/" + x + "/packages"]]

    def set_build_kernel_vars(self):
        prefix = self.settings["spec_prefix"]

        gk_mainargs = prefix + "/gk_mainargs"
        if gk_mainargs in self.settings:
            self.settings["gk_mainargs"] = self.settings[gk_mainargs]
            del self.settings[gk_mainargs]

        # Ask genkernel to include b2sum if <target>/verify is set
        verify = prefix + "/verify"
        if verify in self.settings:
            assert self.settings[verify] == "blake2"
            self.settings.setdefault("gk_mainargs", []).append("--b2sum")

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

        log.debug('self.mount = %s', self.mount)
        for x in [x for x in self.mount if self.mount[x]['enable']]:
            target = normpath(self.settings['chroot_path'] +
                              self.mount[x]['target'])
            log.debug('mount_safety_check() x = %s %s', x, target)
            if not os.path.exists(target):
                continue

            if ismount(target):
                # Something is still mounted
                try:
                    log.warning(
                        '%s is still mounted; performing auto-bind-umount...', target)
                    # Try to umount stuff ourselves
                    self.unbind()
                    if ismount(target):
                        raise CatalystError("Auto-unbind failed for " + target)
                    log.notice('Auto-unbind successful...')
                except CatalystError:
                    raise CatalystError("Unable to auto-unbind " + target)

    def unpack(self):

        clst_unpack_hash = self.resume.get("unpack")

        # Set up all unpack info settings
        unpack_info = self.decompressor.create_infodict(
            source=self.settings["source_path"],
            destination=self.settings["chroot_path"],
            arch=self.settings["compressor_arch"],
            other_options=self.settings["compressor_options"],
        )

        display_msg = (
            'Starting %(mode)s from %(source)s\nto '
            '%(destination)s (this may take some time) ..')

        error_msg = "'%(mode)s' extraction of %(source)s to %(destination)s failed."

        if "seedcache" in self.settings["options"]:
            if os.path.isdir(unpack_info["source"]):
                # SEEDCACHE Is a directory, use rsync
                unpack_info['mode'] = "rsync"
            else:
                # SEEDCACHE is a not a directory, try untar'ing
                log.notice(
                    'Referenced SEEDCACHE does not appear to be a directory, trying to untar...')
                unpack_info['source'] = file_check(unpack_info['source'])
        else:
            # No SEEDCACHE, use tar
            unpack_info['source'] = file_check(unpack_info['source'])
        # end of unpack_info settings

        # set defaults,
        # only change them if the resume point is proven to be good
        _unpack = True
        invalid_chroot = True
        # Begin autoresume validation
        if "autoresume" in self.settings["options"]:
            # check chroot
            if os.path.isdir(self.settings["chroot_path"]):
                if self.resume.is_enabled("unpack"):
                    # Autoresume is valid in the chroot
                    _unpack = False
                    invalid_chroot = False
                    log.notice('Resume: "chroot" is valid...')
                else:
                    # self.resume.is_disabled("unpack")
                    # Autoresume is invalid in the chroot
                    log.notice(
                        'Resume: "seed source" unpack resume point is disabled')

            # check seed source
            if os.path.isfile(self.settings["source_path"]) and not invalid_chroot:
                if self.settings["source_path_hash"].replace("\n", " ") == clst_unpack_hash:
                    # Seed tarball has not changed, chroot is valid
                    _unpack = False
                    invalid_chroot = False
                    log.notice('Resume: "seed source" hash matches chroot...')
                else:
                    # self.settings["source_path_hash"] != clst_unpack_hash
                    # Seed tarball has changed, so invalidate the chroot
                    _unpack = True
                    invalid_chroot = True
                    log.notice(
                        'Resume: "seed source" has changed, hashes do not match, invalidating resume...')
                    log.notice('        source_path......: %s',
                               self.settings["source_path"])
                    log.notice('        new source hash..: %s',
                               self.settings["source_path_hash"].replace("\n", " "))
                    log.notice('        recorded hash....: %s',
                               clst_unpack_hash)
                    unpack_info['source'] = file_check(unpack_info['source'])

        else:
            # No autoresume, check SEEDCACHE
            if "seedcache" in self.settings["options"]:
                # if the seedcache is a dir, rsync will clean up the chroot
                if os.path.isdir(self.settings["source_path"]):
                    pass
            elif os.path.isdir(self.settings["source_path"]):
                    # We should never reach this, so something is very wrong
                raise CatalystError(
                    "source path is a dir but seedcache is not enabled: %s"
                    % self.settings["source_path"])

        if _unpack:
            self.mount_safety_check()

            if invalid_chroot:
                if "autoresume" in self.settings["options"]:
                    log.notice(
                        'Resume: Target chroot is invalid, cleaning up...')

                self.clear_autoresume()
                self.clear_chroot()

            ensure_dirs(self.settings["chroot_path"])

            ensure_dirs(self.settings["chroot_path"] + "/tmp", mode=1777)

            if "pkgcache" in self.settings["options"]:
                ensure_dirs(self.settings["pkgcache_path"], mode=0o755)

            if "kerncache" in self.settings["options"]:
                ensure_dirs(self.settings["kerncache_path"], mode=0o755)

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
            log.notice(
                'Resume: Valid resume point detected, skipping seed unpack operation...')

    def config_profile_link(self):
        log.info('Configuring profile link...')
        make_profile = Path(self.settings['chroot_path'] + self.settings['port_conf'],
                            'make.profile')
        make_profile.unlink()
        make_profile.symlink_to(Path('../..' + self.settings['repo_basedir'],
                                     self.settings['repo_name'],
                                     'profiles',
                                     self.settings['target_profile']),
                                target_is_directory=True)

    def setup_confdir(self):
        if "autoresume" in self.settings["options"] \
                and self.resume.is_enabled("setup_confdir"):
            log.notice(
                'Resume point detected, skipping setup_confdir operation...')
            return

        if "portage_confdir" in self.settings:
            log.info('Configuring %s...', self.settings['port_conf'])
            dest = normpath(
                self.settings['chroot_path'] + '/' + self.settings['port_conf'])
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
                    ensure_dirs(
                        self.settings['chroot_path'] + self.settings['local_overlay'])
                    cmd("cp -a " + x + "/* " + self.settings["chroot_path"] +
                        self.settings["local_overlay"],
                        env=self.env)

    def root_overlay(self):
        """ Copy over the root_overlay """
        if self.settings["spec_prefix"] + "/root_overlay" in self.settings:
            for x in self.settings[self.settings["spec_prefix"] +
                                   "/root_overlay"]:
                if os.path.exists(x):
                    log.info('Copying root_overlay: %s', x)
                    cmd(['rsync', '-a', x + '/', self.settings['destpath']],
                        env=self.env)

    def bind(self):
        for x in [x for x in self.mount if self.mount[x]['enable']]:
            if str(self.mount[x]['source']) == 'config':
                raise CatalystError(f'"{x}" bind mount source is not configured')
            if str(self.mount[x]['target']) == 'config':
                raise CatalystError(f'"{x}" bind mount target is not configured')

            source = str(self.mount[x]['source'])
            target = self.settings['chroot_path'] + str(self.mount[x]['target'])
            fstype = ''
            options = ''

            log.debug('bind %s: "%s" -> "%s"', x, source, target)

            if source == 'maybe_tmpfs':
                if 'var_tmpfs_portage' not in self.settings:
                    continue

                fstype = 'tmpfs'
                options = f"size={self.settings['var_tmpfs_portage']}G"
            elif source == 'tmpfs':
                fstype = 'tmpfs'
            elif source == 'shm':
                fstype = 'tmpfs'
                options = 'noexec,nosuid,nodev'
            else:
                source_path = Path(self.mount[x]['source'])
                if source_path.suffix == '.sqfs':
                    fstype = 'squashfs'
                    options = 'ro,loop'
                else:
                    options = 'bind'

                    # We may need to create the source of the bind mount. E.g., in the
                    # case of an empty package cache we must create the directory that
                    # the binary packages will be stored into.
                    source_path.mkdir(mode=0o755, exist_ok=True)

            Path(target).mkdir(mode=0o755, parents=True, exist_ok=True)

            try:
                cxt = libmount.Context(source=source, target=target,
                                       fstype=fstype, options=options)
                cxt.mount()
            except OSError as e:
                self.unbind()
                raise CatalystError(f"Couldn't mount: {source}, {e.strerror}")

    def unbind(self):
        chroot_path = self.settings["chroot_path"]
        umount_failed = False

        # Unmount in reverse order
        for target in [Path(chroot_path + self.mount[x]['target'])
                       for x in reversed(self.mount)
                       if self.mount[x]['enable']]:
            if not target.exists():
                log.debug('%s does not exist. Skipping', target)
                continue

            if not ismount(target):
                log.debug('%s is not a mount point. Skipping', target)
                continue

            try:
                cxt = libmount.Context(target=str(target))
                cxt.umount()
            except OSError:
                log.warning('First attempt to unmount failed: %s', target)
                log.warning('Killing any pids still running in the chroot')

                self.kill_chroot_pids()

                try:
                    cxt.umount()
                except OSError as e:
                    umount_failed = True
                    log.warning("Couldn't umount: %s, %s", target,
                                e.strerror)

        if umount_failed:
            # if any bind mounts really failed, then we need to raise
            # this to potentially prevent an upcoming bash stage cleanup script
            # from wiping our bind mounts.
            raise CatalystError(
                "Couldn't umount one or more bind-mounts; aborting for safety.")

    def chroot_setup(self):
        self.makeconf = read_makeconf(normpath(self.settings["chroot_path"] +
                                               self.settings["make_conf"]))
        self.override_cbuild()
        self.override_chost()
        self.override_cflags()
        self.override_cxxflags()
        self.override_fcflags()
        self.override_fflags()
        self.override_ldflags()
        self.override_asflags()
        self.override_common_flags()
        if "autoresume" in self.settings["options"] \
                and self.resume.is_enabled("chroot_setup"):
            log.notice(
                'Resume point detected, skipping chroot_setup operation...')
            return

        log.notice('Setting up chroot...')

        shutil.copy('/etc/resolv.conf',
                    self.settings['chroot_path'] + '/etc/')

        # Copy over the binary interpreter (qemu), if applicable; note that it's given
        # as full path and goes to the same place in the chroot
        if "interpreter" in self.settings:
            if not os.path.exists(self.settings["interpreter"]):
                raise CatalystError(
                    "Can't find interpreter " +
                    self.settings["interpreter"],
                    print_traceback=True)

            log.notice('Copying binary interpreter %s into chroot',
                       self.settings['interpreter'])

            if os.path.exists(self.settings['chroot_path'] + '/' + self.settings['interpreter']):
                os.rename(
                    self.settings['chroot_path'] +
                    '/' + self.settings['interpreter'],
                    self.settings['chroot_path'] + '/' + self.settings['interpreter'] + '.catalyst')

            shutil.copy(self.settings['interpreter'],
                        self.settings['chroot_path'] + '/' + self.settings['interpreter'])

        # Copy over the envscript, if applicable
        if "envscript" in self.settings:
            if not os.path.exists(self.settings["envscript"]):
                raise CatalystError(
                    "Can't find envscript " + self.settings["envscript"],
                    print_traceback=True)

            log.warning(
                'env variables in catalystrc may cause catastrophic failure.\n'
                'If your build fails look here first as the possible problem.')

            shutil.copy(self.settings['envscript'],
                        self.settings['chroot_path'] + '/tmp/envscript')

        # Copy over /etc/hosts from the host in case there are any
        # specialties in there
        hosts_file = self.settings['chroot_path'] + '/etc/hosts'
        if os.path.exists(hosts_file):
            os.rename(hosts_file, hosts_file + '.catalyst')
            shutil.copy('/etc/hosts', hosts_file)
        # write out the make.conf
        try:
            self.write_make_conf(setup=True)
        except OSError as e:
            raise CatalystError('Could not write %s: %s' % (
                normpath(self.settings["chroot_path"] +
                         self.settings["make_conf"]), e))
        self.resume.enable("chroot_setup")

    def write_make_conf(self, setup=True):
        # Modify and write out make.conf (for the chroot)
        makepath = normpath(self.settings["chroot_path"] +
                            self.settings["make_conf"])
        with open(makepath, "w") as myf:
            log.notice("Writing the stage make.conf to: %s" % makepath)
            myf.write("# These settings were set by the catalyst build script "
                      "that automatically\n# built this stage.\n")
            myf.write("# Please consult "
                      "/usr/share/portage/config/make.conf.example "
                      "for a more\n# detailed example.\n")

            for flags in ["COMMON_FLAGS", "CFLAGS", "CXXFLAGS", "FCFLAGS", "FFLAGS",
                          "LDFLAGS", "ASFLAGS"]:
                if flags in ["LDFLAGS", "ASFLAGS"]:
                    if not flags in self.settings:
                        continue
                    myf.write("# %s is unsupported.  USE AT YOUR OWN RISK!\n"
                              % flags)
                if flags not in self.settings or (flags != "COMMON_FLAGS" and
                                                  self.settings[flags] == self.settings["COMMON_FLAGS"]):
                    myf.write('%s="${COMMON_FLAGS}"\n' % flags)
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
                myf.write('CBUILD="' + self.settings["CBUILD"] + '"\n')

            if "CHOST" in self.settings:
                myf.write("# WARNING: Changing your CHOST is not something "
                          "that should be done lightly.\n# Please consult "
                          "https://wiki.gentoo.org/wiki/Changing_the_CHOST_variable "
                          "before changing.\n")
                myf.write('CHOST="' + self.settings["CHOST"] + '"\n')

            # Figure out what our USE vars are for building
            myusevars = []
            if "bindist" in self.settings["options"]:
                myf.write(
                    "\n# NOTE: This stage was built with the bindist Use flag enabled\n")
            if setup or "sticky-config" in self.settings["options"]:
                myusevars.extend(self.settings["catalyst_use"])
                log.notice("STICKY-CONFIG is enabled")
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

            myuseexpandvars = {}
            if "HOSTUSEEXPAND" in self.settings:
                for hostuseexpand in self.settings["HOSTUSEEXPAND"]:
                    myuseexpandvars.update(
                        {hostuseexpand: self.settings["HOSTUSEEXPAND"][hostuseexpand]})

            if myuseexpandvars:
                for hostuseexpand in myuseexpandvars:
                    myf.write(hostuseexpand + '="' +
                              ' '.join(myuseexpandvars[hostuseexpand]) + '"\n')

            # Write non-default PORTDIR/DISTDIR/PKGDIR settings to make.conf
            if (self.settings['repo_basedir'], self.settings['repo_name']) != \
               (confdefaults['repo_basedir'], confdefaults['repo_name']):
                myf.write('PORTDIR="%s/%s"\n' % (self.settings['repo_basedir'],
                                                 self.settings['repo_name']))

            for x in ['target_distdir', 'target_pkgdir']:
                if self.settings[x] != confdefaults[x]:
                    varname = x.split('_')[1].upper()
                    myf.write(f'{varname}="{self.settings[x]}"\n')

            if setup:
                # Setup the portage overlay
                if "portage_overlay" in self.settings:
                    myf.write('PORTDIR_OVERLAY="%s"\n' %
                              self.settings["local_overlay"])

            # Set default locale for system responses. #478382
            myf.write(
                '\n'
                '# This sets the language of build output to English.\n'
                '# Please keep this setting intact when reporting bugs.\n'
                'LC_MESSAGES=C\n')

    def fsscript(self):
        if "autoresume" in self.settings["options"] \
                and self.resume.is_enabled("fsscript"):
            log.notice('Resume point detected, skipping fsscript operation...')
            return

        if "fsscript" in self.settings:
            if os.path.exists(self.settings["controller_file"]):
                cmd([self.settings['controller_file'], 'fsscript'],
                    env=self.env)
                self.resume.enable("fsscript")

    def rcupdate(self):
        if "autoresume" in self.settings["options"] \
                and self.resume.is_enabled("rcupdate"):
            log.notice('Resume point detected, skipping rcupdate operation...')
            return

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
                clear_path(normpath(self.settings["destpath"] + x))

        # Put /etc/hosts back into place
        hosts_file = self.settings['chroot_path'] + '/etc/hosts'
        if os.path.exists(hosts_file + '.catalyst'):
            os.rename(hosts_file + '.catalyst', hosts_file)

        # optionally clean up binary interpreter
        if "interpreter" in self.settings:
            if os.path.exists(self.settings['chroot_path'] + '/' + self.settings['interpreter'] + '.catalyst'):
                os.rename(
                    self.settings['chroot_path'] + '/' +
                    self.settings['interpreter'] + '.catalyst',
                    self.settings['chroot_path'] + '/' + self.settings['interpreter'])
            else:
                os.remove(
                    self.settings['chroot_path'] + '/' + self.settings['interpreter'])

        # optionally clean up portage configs
        if ("portage_prefix" in self.settings and
                "sticky-config" not in self.settings["options"]):
            log.debug("clean(), portage_preix = %s, no sticky-config",
                      self.settings["portage_prefix"])
            for _dir in "package.accept_keywords", "package.keywords", "package.mask", "package.unmask", "package.use", "package.env", "env":
                target = pjoin(self.settings["destpath"],
                               "etc/portage/%s" % _dir,
                               self.settings["portage_prefix"])
                log.notice("Clearing portage_prefix target: %s", target)
                clear_path(target)

        # Remove hacks that should *never* go into stages
        target = pjoin(self.settings["destpath"], "etc/portage/patches")
        if os.path.exists(target):
            log.warning("You've been hacking. Clearing target patches: %s", target)
            clear_path(target)

        # Remove our overlay
        overlay = normpath(
            self.settings["chroot_path"] + self.settings["local_overlay"])
        if os.path.exists(overlay):
            clear_path(overlay)

        if "sticky-config" not in self.settings["options"]:
            # re-write the make.conf to be sure it is clean
            self.write_make_conf(setup=False)

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
            return

        if self.settings["spec_prefix"] + "/empty" in self.settings:
            if isinstance(
                    self.settings[self.settings['spec_prefix'] + '/empty'],
                    str):
                self.settings[self.settings["spec_prefix"] + "/empty"] = \
                    self.settings[self.settings["spec_prefix"] +
                                  "/empty"].split()
            for x in self.settings[self.settings["spec_prefix"] + "/empty"]:
                myemp = self.settings["destpath"] + x
                if not os.path.isdir(myemp) or os.path.islink(myemp):
                    log.warning('not a directory or does not exist, '
                                'skipping "empty" operation: %s', x)
                    continue
                log.info('Emptying directory %s', x)
                clear_dir(myemp)
        self.resume.enable("empty")

    def remove(self):
        if "autoresume" in self.settings["options"] \
                and self.resume.is_enabled("remove"):
            log.notice('Resume point detected, skipping remove operation...')
            return

        if self.settings["spec_prefix"] + "/rm" in self.settings:
            for x in self.settings[self.settings["spec_prefix"] + "/rm"]:
                # We're going to shell out for all these cleaning
                # operations, so we get easy glob handling.
                log.notice('%s: removing %s', self.settings["spec_prefix"], x)
                clear_path(self.settings["destpath"] + x)
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
            return

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
            return

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
            log.warning("Couldn't create stage tarball: %s",
                        target_filename)

    def run_local(self):
        if "autoresume" in self.settings["options"] \
                and self.resume.is_enabled("run_local"):
            log.notice('Resume point detected, skipping run_local operation...')
            return

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
        log.debug('setup_environment(); settings = %r', self.settings)
        for x in list(self.settings):
            log.debug('setup_environment(); processing: %s', x)
            if x == "options":
                for opt in self.settings[x]:
                    self.env['clst_' + opt.upper()] = "true"
                continue

            varname = 'clst_' + sanitize_name(x)

            if isinstance(self.settings[x], str):
                # Prefix to prevent namespace clashes
                if "path" in x:
                    self.env[varname] = self.settings[x].rstrip("/")
                else:
                    self.env[varname] = self.settings[x]
            elif isinstance(self.settings[x], list):
                self.env[varname] = ' '.join(self.settings[x])
            elif isinstance(self.settings[x], bool):
                if self.settings[x]:
                    self.env[varname] = "true"
            elif isinstance(self.settings[x], (int, float)):
                self.env[varname] = str(self.settings[x])
            elif isinstance(self.settings[x], dict):
                if x in ['compress_definitions', 'decompress_definitions']:
                    continue
                log.warning("Not making envar for '%s', is a dict", x)

        makeopts = []
        for flag, setting in {'j': 'jobs', 'l': 'load-average'}.items():
            if setting in self.settings:
                makeopts.append(f'-{flag}{self.settings[setting]}')
        self.env['MAKEOPTS'] = ' '.join(makeopts)

        log.debug('setup_environment(); env = %r', self.env)

    def run_sequence(self, sequence):
        for func in sequence:
            log.notice('--- Running action sequence: %s', func)
            sys.stdout.flush()
            try:
                getattr(self, func)()
            except LockInUse:
                log.error('Unable to aquire the lock...')
                return False
            except Exception:
                log.error('Exception running action sequence %s',
                          func, exc_info=True)
                return False

        return True

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
            return True

        if "purgeonly" in self.settings["options"]:
            log.info('StageBase: run() purgeonly')
            self.purge()

        if "purge" in self.settings["options"]:
            log.info('StageBase: run() purge')
            self.purge()

        if not self.run_sequence(self.prepare_sequence):
            return False

        with namespace(mount=True):
            if not self.run_sequence(self.build_sequence):
                return False

        if not self.run_sequence(self.finish_sequence):
            return False

        return True

    def unmerge(self):
        if "autoresume" in self.settings["options"] \
                and self.resume.is_enabled("unmerge"):
            log.notice('Resume point detected, skipping unmerge operation...')
            return

        if self.settings["spec_prefix"] + "/unmerge" in self.settings:
            if isinstance(self.settings[self.settings['spec_prefix'] + '/unmerge'], str):
                self.settings[self.settings["spec_prefix"] + "/unmerge"] = \
                    [self.settings[self.settings["spec_prefix"] + "/unmerge"]]

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
            log.notice(
                'Resume point detected, skipping target_setup operation...')
            return

        log.notice('Setting up filesystems per filesystem type')
        cmd([self.settings['controller_file'], 'target_image_setup',
             self.settings['target_path']], env=self.env)
        self.resume.enable("target_setup")

    def setup_overlay(self):
        if "autoresume" in self.settings["options"] \
                and self.resume.is_enabled("setup_overlay"):
            log.notice(
                'Resume point detected, skipping setup_overlay operation...')
            return

        if self.settings["spec_prefix"] + "/overlay" in self.settings:
            for x in self.settings[self.settings["spec_prefix"] + "/overlay"]:
                if os.path.exists(x):
                    cmd(['rsync', '-a', x + '/', self.settings['target_path']],
                        env=self.env)
            self.resume.enable("setup_overlay")

    def create_iso(self):
        if "autoresume" in self.settings["options"] \
                and self.resume.is_enabled("create_iso"):
            log.notice(
                'Resume point detected, skipping create_iso operation...')
            return

        # Create the ISO
        if "iso" in self.settings:
            cmd([self.settings['controller_file'], 'iso', self.settings['iso']],
                env=self.env)
            self.gen_contents_file(self.settings["iso"])
            self.gen_digest_file(self.settings["iso"])
            self.resume.enable("create_iso")
        else:
            log.warning('livecd/iso was not defined.  '
                        'An ISO Image will not be created.')

    def build_packages(self):
        build_packages_resume = pjoin(self.settings["autoresume_path"],
                                      "build_packages")
        if "autoresume" in self.settings["options"] \
                and self.resume.is_enabled("build_packages"):
            log.notice(
                'Resume point detected, skipping build_packages operation...')
            return

        if self.settings["spec_prefix"] + "/packages" in self.settings:
            target_pkgs = self.settings["spec_prefix"] + '/packages'
            if "autoresume" in self.settings["options"] \
                    and self.resume.is_enabled("build_packages"):
                log.notice('Resume point detected, skipping build_packages '
                           'operation...')
            else:
                command = [self.settings['controller_file'],
                           'build_packages']
                if isinstance(self.settings[target_pkgs], str):
                    command.append(self.settings[target_pkgs])
                else:
                    command.extend(self.settings[target_pkgs])
                try:
                    cmd(command, env=self.env)
                    fileutils.touch(build_packages_resume)
                    self.resume.enable("build_packages")
                except CatalystError:
                    self.unbind()
                    raise CatalystError(
                        self.settings["spec_prefix"] +
                        "build aborting due to error.")

    def build_kernel(self):
        '''Build all configured kernels'''
        if "autoresume" in self.settings["options"] \
                and self.resume.is_enabled("build_kernel"):
            log.notice(
                'Resume point detected, skipping build_kernel operation...')
            return

        if "boot/kernel" in self.settings:
            try:
                mynames = self.settings["boot/kernel"]
                if isinstance(mynames, str):
                    mynames = [mynames]
                # Execute the script that sets up the kernel build environment
                cmd([self.settings['controller_file'], 'pre-kmerge'], env=self.env)
                for kname in [sanitize_name(name) for name in mynames]:
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
                and self.resume.is_enabled("build_kernel_" + kname):
            log.notice('Resume point detected, skipping build_kernel '
                       'for %s operation...', kname)
            return
        self._copy_kernel_config(kname=kname)

        # If we need to pass special options to the bootloader
        # for this kernel put them into the environment
        key = 'boot/kernel/' + kname + '/kernelopts'
        if key in self.settings:
            myopts = self.settings[key]

            if not isinstance(myopts, str):
                myopts = ' '.join(myopts)
            self.env[kname + "_kernelopts"] = myopts

        key = 'boot/kernel/' + kname + '/extraversion'
        self.settings.setdefault(key, '')
        self.env["clst_kextraversion"] = self.settings[key]

        self._copy_initramfs_overlay(kname=kname)

        # Execute the script that builds the kernel
        cmd([self.settings['controller_file'], 'kernel', kname],
            env=self.env)

        if "boot/kernel/" + kname + "/initramfs_overlay" in self.settings:
            log.notice('Cleaning up temporary overlay dir')
            clear_dir(self.settings['chroot_path'] + '/tmp/initramfs_overlay/')

        self.resume.is_enabled("build_kernel_" + kname)

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
                log.notice('Copying initramfs_overlay dir %s',
                           self.settings[key])

                ensure_dirs(
                    self.settings['chroot_path'] +
                    '/tmp/initramfs_overlay/' + self.settings[key])

                cmd('cp -R ' + self.settings[key] + '/* ' +
                    self.settings['chroot_path'] +
                    '/tmp/initramfs_overlay/' + self.settings[key], env=self.env)

    def bootloader(self):
        if "autoresume" in self.settings["options"] \
                and self.resume.is_enabled("bootloader"):
            log.notice(
                'Resume point detected, skipping bootloader operation...')
            return

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
            log.notice(
                'Resume point detected, skipping build_packages operation...')
            return

        try:
            cmd([self.settings['controller_file'], 'livecd-update'],
                env=self.env)
            self.resume.enable("livecd_update")

        except CatalystError:
            self.unbind()
            raise CatalystError(
                "build aborting due to livecd_update error.")

    @staticmethod
    def _debug_pause_():
        input("press any key to continue: ")
