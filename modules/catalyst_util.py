#!/usr/bin/python
# Copyright 2003 Gentoo Technologies, Inc.; http://www.gentoo.org
# Released under the GNU General Public License version 2

#TODO: add snapshotting of portage trees, which will not be handled by spec files.
#Then, add spec file support and env var export support, then mount/umount support...
#then we should be getting close to completion and usability.

import sys,os,string,stat

subarches=["amd64", "hppa", "hppa1.1", "hppa2.0", "x86", "i386", "i486", "i586", "i686",
"athlon", "athlon-xp", "athlon-mp", "pentium-mmx", "pentium3", "pentium4", "ppc", "g3",
"g4", "sparc", "sparc64", "mips", "alpha", "ev4", "ev5", "ev56", "pca56", "ev6", "ev67" ]

#this target stuff is not completed, but I've added it as a general template.
"""
setting name			default/example			defined how?
=====================================================================================================================

globals:

storedir*			/var/tmp/catalyst			default (where to store all the stuff, ie snapshots, etc.)
sharedir*			/usr/share/catalyst			default (where the dir that holds targets is)

global external paths:

distdir				/usr/portage/distfiles			default (/usr/portage/distfiles)
portdir*			/usr/portage				default (not set inside chroot)

locals from spec:

version_stamp			20031016					user (from spec)
target				stage3						user (from spec)
subarch				pentium4					user (from spec)
rel_type			default						user (from spec) (was BUILDTYPE)
rel_version			1.4						user (from spec) (was MAINVERSION)
snapshot			20031016					user (from spec)
source				default-x86-1.4/stage2-pentium4-20031016	user (from spec)


target_subpath			default-x86-1.4/stage3-pentium4-20031016
				rel_type+"-"+mainarch+"-"+rel_version+"/"+target+"-"+subarch+"-"+version_stamp

snapshot_path			/var/tmp/catalyst/snapshots/portage-20031016.tar.bz2	
				storedir+"/snapshots/portage"+snapshot+".tar.bz2"

target_path			/var/tmp/catalyst/builds/default-x86-1.4/stage3-pentium4-20031016.tar.bz2
				storedir+"/builds/"+target_subpath+".tar.bz2"

source_path			/var/tmp/catalyst/builds/default-x86-1.4/stage2-pentium4-20031016.tar.bz2
				storedir+"/builds/"+source+".tar.bz2"

chroot_path			/var/tmp/catalyst/tmp/default-x86-1.4/stage3-pentium4-20031016
				storedir+"/tmp/"+target_subpath


locals, auto-generated:

pkgdir										default (package cache dir)
mainarch			x86						auto
catdirname			default-x86-1.4/stage3-pentium4-20031016	auto
cflags				-O2						auto
cxxflags			-O2						auto
hostuse				mmx sse						auto
chost				i686-pc-linux-gnu				auto
makeopts			-j2						auto (but overridable from catalyst.conf)
chroot				chroot						auto (linux32 chroot or chroot)



Config file sources:
	1. defaults can come from /etc/catalyst.conf (since it's run as root, might as well put it in /etc
		(these defaults can be things like pkgdir, distdir, but not rel_version or rel_type
		which we specifically want in the spec file so that we have a complete description there.)
		This file can also tell catalyst whether to use ccache or not.
	2. spec file
		spec can override any of the "auto" variables. we need to remember cxxflags too.
"""
class generic_target:
	def __init__(self,myset):
		self.settings=myset
		self.envmap={"CFLAGS":"cflags" }
	def path(self):
		#temp file paths: 
		#/var/tmp/catalyst/default-x86-1.4/stage1-pentium4-20030911/work
		#/var/tmp/catalyst/default-x86-1.4/stage1-pentium4-20030911/packages (if there is a package cache)
		
		#final paths:
		#snapshots/portage-20030911.tar.bz2
		#builds/default-x86-1.4/stage1-pentium4-20030911.tar.bz2
		#builds/default-x86-1.4/stage2-pentium4-20030911.tar.bz2
		#builds/default-x86-1.4/stage3-pentium4-20030911.tar.bz2
		#builds/default-x86-1.4/grp-pentium4-20030911/cd1/packages/All
		#builds/default-x86-1.4/grp-pentium4-20030911/cd2/packages/All
		#builds/default-x86-1.4/livecd-20030911.tar.bz2
		#builds/buildtype-mainarch-mainversion/buildtype-subarch-version_stamp
		#now where to put the work files.
		return "stages/stage1-"+self.settings["subarch"]+"-"+self.settings["buildno"]+".tar.bz2"
	def read_spec_file(self,myfile):
		#settings from this file:
		#pkgdir, distdir, subarch, mainversion, version_stamp, snapshot, source tarball
		#default default  user     user         user           user      user
		#read in a spec file, grab settings we need.
		pass
	def execute_script(self,myscript,myargs):
		#export env vars here
		return os.system(myscript+" "+string.join(myargs," "))
		pass
	def export_variables(self):
		#export environment variables
		#export:
		# CFLAGS, HOSTUSE, CHOST, MAINARCH, MAINVERSION, BUILDTYPE, MAKEOPTS, BASEDIR, CHROOTDIR, FEATURES
		# auto    auto     auto   auto      spec         spec auto default  auto       default	
		pass
	def build(self):
		#do the actual stage1 building
		return execute_script("targets/stage1/build.sh")
	def unpack(self):
		#unpack stages
		pass
	def mount_all(self):
		#mount mount points; let's handle this from python
		pass
	def umount_all(self):
		#umount mount points; let's handle this from python
		pass
	def mount_safety_check(self,mypath):
		#check and verify that none of our paths in mypath are mounted. We don't want to clean up with things still
		#mounted, and this allows us to check. returns 1 on ok, 0 on "something is still mounted" case.
		paths=["usr/portage/packages","/usr/portage/distfiles", "/var/tmp/distfiles", "/proc", "/root/.ccache", "/dev"]
		if not os.path.exists(mypath):
			return 1 
		mypstat=os.stat(mypath)[ST_DEV]
		for x in paths:
			if not os.path.exists(x):
				continue
			teststat=os.stat(x)[ST_DEV]
			if teststat!=mypstat:
				#something is still mounted
				return 0
		return 1
	def prep(self):
		#prepare stage for packing up
		pass
	def clean(self):
		#clean up temporary build directory
		pass
	def pack(self):
		#tar up anything like a stage and put in right place
		pass
	def run(self):
		self.mount_safety_check()
		self.unpack()
		self.setup()
		self.mount_all()
		retval=self.build() #check for failure
		self.umount_all()
		self.mount_safety_check()
		self.prep()
		self.pack()
		self.clean()

class stage2(generic_target):
	#subclass of generic_target
	def path(self):
		return "stages/stage2-"+self.settings["subarch"]+"-"+self.settings["buildno"]+".tar.bz2"

class stage3(generic_target):
	def path(self):
		return "stages/stage3-"+self.settings["subarch"]+"-"+self.settings["buildno"]+".tar.bz2"

class grp(generic_target):
	def path(self):
		return "stages/stage3-"+self.settings["subarch"]+"-"+self.settings["buildno"]+".tar.bz2"

class livecd(generic_target):
	def path(self):
		return "stages/stage3-"+self.settings["subarch"]+"-"+self.settings["buildno"]+".tar.bz2"

def verify_os(myset):
	if sys.platform=="linux2":
		myset["os_userland"]="GNU"
	else:
		raise OSError, "Platform "+sys.platform+" not recognized."

def job_defaults(mainarch):
	return "to be completed"

def verify_subarch(myset,subarch):
	global subarches
	if subarch not in subarches:
		raise ValueError, "Sub-architecture "+mysubarch+" not recognized."
	myset["subarch"]=subarch

	if subarch == "athlon-mp":
		subarch="athlon-xp"

	results=None

	if subarch == "ia64":
		results=["ia64","-O2","ia64-unknown-linux-gnu",[]]
	elif subarch == "amd64":
		results=["amd64","-O2 -fPIC","x86_64-pc-linux-gnu",[]]
	elif subarch in ["hppa","hppa1.1","hppa2.0"]:
		results=["hppa","-O2","hppa-unknown-linux-gnu",[]]
		if subarch == "hppa2.0":
			results[1] += " -march=2.0"
		else:
			results[1] += " -march=1.1"
	elif subarch in ["x86","i386","i486","i586","i686","athlon","athlon-xp","athlon-mp","pentium-mmx","pentium3","pentium4"]:
		#With recent gcc compilers (gcc-3.1+,) gcc produces generally slower code with -O3 as compared to -O2
		#So we are tweaking things here. 
		uf=[]
		if subarch == "x86":
			cf="-O2 -mcpu=i686 -fomit-frame-pointer"
		elif subarch == "athlon-xp":
			#we've intentionally lowered optimizations here to address compile bugs. It is very likely safe to
			#go up to -O3 without any additional -f goodies (like unroll-loops and prefetch-loop-arrays) tacked
			#on. Note that we don't add any extra -f goodies if we are athlon* below.
			cf="-O2 -march=athlon-xp -fomit-frame-pointer"
		else:
			cf="-O2 -march="+subarch+" -fomit-frame-pointer"
		if subarch[0:6] == "athlon":
			uf.append("3dnow")
		if subarch in [ "athlon","athlon-xp","athlon-mp","pentium-mmx","pentium3","pentium4" ]:
			uf.append("mmx")
		if subarch in [ "pentium3", "pentium4" ]:
			uf.append("sse")
		if subarch in ["pentium3", "pentium4", "athlon", "athlon-xp", "athlon-mp", "i686"]:
			cf += " -finline-functions -finline-limit=800"
		if subarch in ["i386","i486","i586"]:
			results=["x86",cf,subarch+"-pc-linux-gnu",[]]
		elif subarch == "x86":
			results=["x86",cf,"i486-pc-linux-gnu",[]]
		elif subarch == "pentium-mmx":
			results=["x86",cf,"i586-pc-linux-gnu",uf]
		else:
			results=["x86",cf,"i686-pc-linux-gnu",uf]
		
	elif subarch in ["ppc","g3","g4"]:
		if subarch == "ppc":
			results=["ppc","-O2 -fsigned-char",[]]
		elif subarch == "g3":
			results=["ppc","-O2 -mcpu=750 -mpowerpc-gfxopt -fsigned-char"]
		elif subarch == "g4":
			results=["ppc","-O2 -mcpu=7400 -maltivec -mabi=altivec -mpowerpc-gfxopt -fsigned-char"]
		results.extend(["powerpc-unknown-linux-gnu",[]])
	elif subarch in ["sparc","sparc64"]:
		if subarch == "sparc":
			results=["sparc","-O2"]
		else:
			results=["sparc64","-O3 -mcpu=ultrasparc -mtune=ultrasparc"]
		results.extend(["sparc-unknown-linux-gnu",[]])
	elif subarch == "mips":
		results=["mips","-O2","mips-unknown-linux-gnu",[]]
	elif subarch in ["alpha","ev4","ev5","ev56","pca56","ev6","ev67"]:
		if subarch == "alpha":
			results=["alpha","-O3 -mcpu=ev5","alpha-unknown-linux-gnu",[]]
		else:
			results=["alpha","-O3 -mcpu="+subarch,"alpha"+subarch+"-linux-gnu",[]]
	if results==None:
		raise ValueError, "Invalid subarch value passed to compile_defaults (you should not see this)"
	#the main architecture we're building for: (string)
	myset["mainarch"]=results[0]
	#the CFLAGS we should use on this specific architecture (ie pentium4): (string)
	myset["cflags"]=results[1]
	#the CHOST setting (ie i686-pc-linux-gnu): (string)
	myset["chost"]=results[2]
	#any USE variables that should be enabled on this platform (mmx, sse, 3dnow) (list)
	myset["hostuse"]=results[3]
	
def die(msg=None):
	if msg:
		print "catalyst: "+msg
	sys.exit(1)

def warn(msg):
	print "catalyst: "+msg

modes=["snap","enter","umount","livecd","stage"]
modesdesc={ 	"snap":"Create a snapshot of the Portage tree for building",
		"enter":"Enter the specified build chroot (interactive)",
		"umount":"Unmount the specified build chroot mount points",
		"livecd":"Build the specified LiveCD runtime image",
		"stage":"Build the specified stage tarball or package set",
}

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

def usage():
	print "catalyst: Gentoo Linux stage/LiveCD/GRP building tool"
	print
	for x in modes:
		print x+":",modesdesc[x]
	die()

def read_settings(myset,myfn):
	"""Grab local settings from a specified file myfn, dump values we are interested in to settings dictionary myset"""
	if not os.path.exists(myfn):
		raise OSError, "Cannot find settings file "+myfn
	valdict={}
	#this next line might throw an exception; it runs the file myfn as python code
	#and dumps all variable definitions in the valdict dictionary.
	try:
		execfile(myfn,valdict,valdict)
	except:
		raise ValueError, "Error parsing settings file: "+myfn
	#now we look inside the valdict dictionary and grab the settings we're interested
	#in.
	for x in ["buildtype","portdir","distdir","ccache"]:
		if valdict.has_key(x):
			myset[x]=valdict[x]

def global_settings_init(myset):
	#now, we read in global configuration settings from /etc/catalyst.conf
	if os.path.exists("/etc/catalyst.conf"):
		read_settings(myset,"/etc/catalyst.conf")
	#set reasonable defaults if none were provided in /etc/catalyst.conf
	mydefaults={"portdir":"/usr/portage","storedir":"/var/tmp/catalyst","sharedir":"/usr/share/catalyst","distdir":"/usr/share/distfiles"}
	for x in mydefaults.keys():
		if not myset.has_key(x):
			myset[x]=mydefaults[x]
	if not myset.has_key("snapdir"):
		myset["snapdir"]=myset["storedir"]+"/snapshots"
	if not myset.has_key("cat_tmpdir"):
		myset["cat_tmpdir"]=myset["storedir"]+"/tmp"

def init_writable_dirs(myset):
	#create the initial main directories that we need to write to.
	for x in ["storedir","snapdir","cat_tmpdir"]:
		if not os.path.exists(myset[x]):
			os.makedirs(myset[x])

def dump_settings(myset):
	for x in myset.keys():
		print x+":",myset[x]
	print "Done!"

def mainloop():
	global subarches
	#argument processing

	if len(sys.argv)==1 or sys.argv[1] in ["-h","--help"]:
		usage()
	elif os.getuid()!=0:
		#non-root callers can still get -h and --help to work.
		die("This script requires root privileges to operate.")	
	elif sys.argv[1] in modes:
		#set up internal configuration settings dictionary
		#myset=settings()
		myset={}
		verify_os(myset)
		global_settings_init(myset)			
		init_writable_dirs(myset)
		#dump_settings(myset)
		if sys.argv[1]=="snap":
			if len(sys.argv)!=3:
				die("invalid number of arguments for snapshot.")
			do_snapshot(myset["portdir"],myset["cat_tmpdir"],myset["snapdir"],sys.argv[2])
			#do snapshot here
			sys.exit(0)
		sys.exit(0)
	else:
		usage()

if __name__ == "__main__":
	mainloop()



