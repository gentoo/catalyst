# Copyright 1999-2004 Gentoo Foundation
# Distributed under the terms of the GNU General Public License v2
# $Header: /var/cvsroot/gentoo/src/catalyst/modules/embedded_target.py,v 1.8 2005/01/13 00:04:49 zhen Exp $

"""
This class works like a 'stage3'.  A stage2 tarball is unpacked, but instead
of building a stage3, it emerges a 'system' into another directory
inside the 'stage2' system.  This way we do not have to emerge gcc/portage
into the staged system.

It sounds real complicated but basically it runs
ROOT=/tmp/submerge emerge --blahblah foo bar
"""

import os,string,imp,types,shutil
from catalyst_support import *
from generic_stage_target import *
from stat import *

class embedded_target(generic_stage_target):

    def __init__(self,spec,addlargs):
        self.required_values=[]
        self.valid_values=[]
        self.valid_values.extend(["embedded/empty","embedded/rm","embedded/unmerge","embedded/fs-prepare","embedded/fs-finish","embedded/mergeroot","embedded/packages","embedded/use","embedded/fs-type","boot/kernel"])

        if addlargs.has_key("embedded/fs-type"):
            self.valid_values.append("embedded/fs-ops")

        # this kernel code is also from livecd stage2

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

        generic_stage_target.__init__(self,spec,addlargs)
	self.settings["image_path"]=self.settings["storedir"]+"/builds/"+self.settings["target_subpath"]+"/image"	
               
    # taken from livecd-stage3 code
    def unmerge(self):
	    print "Unmerging packages"
            if self.settings.has_key("embedded/unmerge"):
		    if type(self.settings["embedded/unmerge"])==types.StringType:
			    self.settings["embedded/unmerge"]=[self.settings["embedded/unmerge"]]
		    myunmerge=self.settings["embedded/unmerge"][:]
                    
                    for x in range(0,len(myunmerge)):
                        myunmerge[x]="'"+myunmerge[x]+"'"
	     		myunmerge=string.join(myunmerge)
                    # before cleaning unmerge stuff
		    cmd("/bin/bash "+self.settings["sharedir"]+"/targets/"+self.settings["target"]+"/unmerge.sh "+myunmerge,"unmerge script failed.")
                        
    def clean(self):
	    if self.settings.has_key("embedded/rm"):
		    if type(self.settings["embedded/rm"])==types.StringType:
			    self.settings["embedded/rm"]=[self.settings["embedded/rm"]]
			    print "Removing directories from image"
		    for x in self.settings["embedded/rm"]:
			    print "Removing "+x
			    os.system("rm -rf "+self.settings["chroot_path"]+"/tmp/mergeroot"+x)

    def build_fs(self):
        try:
            if self.settings.has_key("embedded/fs-type"):
                cmd("/bin/bash "+self.settings["sharedir"]+"/targets/embedded/embedded.sh package","filesystem packaging failed")
        except CatalystError:
                self.unbind()
                raise CatalystError, "embedded filesystem creation aborting due to error."

    # this code is mostly duplication from the livecd stage2 module
    def pre_build_fs(self):
    	try:
		if self.settings.has_key("embedded/fs-prepare"):
			cmd("/bin/bash "+self.settings["embedded/fs-prepare"], "pre filesystem packaging cause an error in execution")
	except CatalystError:
		self.unbind()
		raise CatalystError, "embedded pre filesystem creation script aborting due to error"

    def post_build_fs(self):
    	try:
		if self.settings.has_key("embedded/fs-finish"):
			cmd("/bin/bash "+self.settings["embedded/fs-finish"], "pre filesystem packaging cause an error in execution")
	except CatalystError:
		self.unbind()
		raise CatalystError, "embedded post filesystem creation script aborting due to error"

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
			
            if self.settings.has_key("boot/kernel/"+kname+"/extraversion"):
                            args.append(self.settings["boot/kernel/"+kname+"/extraversion"])
            else:
                args.append("NULL_VALUE")
	    if self.settings.has_key("boot/kernel/"+kname+"/gk_action"):
	    		args.append(self.settings["boot/kernel/"+kname+"/gk_action"])
			
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
                        myf.write("export clst_embedded_gk_kernargs=\""+myex+"\"\n")
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
            cmd("/bin/bash "+self.settings["sharedir"]+"/targets/embedded/embedded.sh kernel "+list_bashify(args),
                "Runscript kernel build failed")

    def run_local(self):
	    mypackages=list_bashify(self.settings["embedded/packages"])
	    print "Merging embedded image"
	    try:
		    cmd("/bin/bash "+self.settings["sharedir"]+"/targets/embedded/embedded.sh run")
	    except CatalystError:
		    self.unbind()
		    raise CatalystError, "Embedded build aborted due to error."

            if self.settings.has_key("boot/kernel"):
	     	self.build_kernel()

	    self.unmerge()
	    self.clean()

	    self.pre_build_fs()
            self.build_fs()
	    self.post_build_fs()

    def set_action_sequence(self):
	self.settings["action_sequence"]=["dir_setup","unpack_and_bind","chroot_setup",\
					"setup_environment","run_local","unbind","capture"]
	
    def set_use(self):
        self.settings["use"]=self.settings["embedded/use"]
    def set_stage_path(self):
        self.settings["stage_path"]=self.settings["chroot_path"]+"/tmp/mergeroot"
	print "embedded stage path is "+self.settings["stage_path"]
def register(foo):
        foo.update({"embedded":embedded_target})
        return foo
