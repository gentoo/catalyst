
import sys,string,os,types,re,signal,traceback,time
from catalyst.output import warn
import catalyst.util
#import md5,sha

selinux_capable = False
#userpriv_capable = (os.getuid() == 0)
#fakeroot_capable = False
BASH_BINARY             = "/bin/bash"

try:
        import resource
        max_fd_limit=resource.getrlimit(RLIMIT_NOFILE)
except SystemExit, e:
        raise
except:
        # hokay, no resource module.
        max_fd_limit=256

# pids this process knows of.
spawned_pids = []

try:
        import urllib
except SystemExit, e:
        raise

def cleanup(pids,block_exceptions=True):
        """function to go through and reap the list of pids passed to it"""
        global spawned_pids
        if type(pids) == int:
                pids = [pids]
        for x in pids:
                try:
                        os.kill(x,signal.SIGTERM)
                        if os.waitpid(x,os.WNOHANG)[1] == 0:
                                # feisty bugger, still alive.
                                os.kill(x,signal.SIGKILL)
                                os.waitpid(x,0)

                except OSError, oe:
                        if block_exceptions:
                                pass
                        if oe.errno not in (10,3):
                                raise oe
                except SystemExit:
                        raise
                except Exception:
                        if block_exceptions:
                                pass
                try:                    spawned_pids.remove(x)
                except IndexError:      pass



# a function to turn a string of non-printable characters into a string of
# hex characters
def hexify(str):
	hexStr = string.hexdigits
	r = ''
	for ch in str:
		i = ord(ch)
		r = r + hexStr[(i >> 4) & 0xF] + hexStr[i & 0xF]
	return r
# hexify()

def generate_contents(file,contents_function="auto",verbose=False):
	try:
		_ = contents_function
		if _ == 'auto' and file.endswith('.iso'):
			_ = 'isoinfo-l'
		if (_ in ['tar-tv','auto']):
			if file.endswith('.tgz') or file.endswith('.tar.gz'):
				_ = 'tar-tvz'
			elif file.endswith('.tbz2') or file.endswith('.tar.bz2'):
				_ = 'tar-tvj'
			elif file.endswith('.tar'):
				_ = 'tar-tv'

		if _ == 'auto':
			warn('File %r has unknown type for automatic detection.' % (file, ))
			return None
		else:
			contents_function = _
			_ = contents_map[contents_function]
			return _[0](file,_[1],verbose)
	except:
		raise CatalystError,\
			"Error generating contents, is appropriate utility (%s) installed on your system?" \
			% (contents_function, )

def calc_contents(file,cmd,verbose):
	args={ 'file': file }
	cmd=cmd % dict(args)
	a=os.popen(cmd)
	mylines=a.readlines()
	a.close()
	result="".join(mylines)
	if verbose:
		print result
	return result

# This has map must be defined after the function calc_content
# It is possible to call different functions from this but they must be defined
# before hash_map
# Key,function,cmd
contents_map={
	# 'find' is disabled because it requires the source path, which is not
	# always available
	#"find"		:[calc_contents,"find %(path)s"],
	"tar-tv":[calc_contents,"tar tvf %(file)s"],
	"tar-tvz":[calc_contents,"tar tvzf %(file)s"],
	"tar-tvj":[calc_contents,"tar tvjf %(file)s"],
	"isoinfo-l":[calc_contents,"isoinfo -l -i %(file)s"],
	# isoinfo-f should be a last resort only
	"isoinfo-f":[calc_contents,"isoinfo -f -i %(file)s"],
}

def generate_hash(file,hash_function="crc32",verbose=False):
	try:
		return hash_map[hash_function][0](file,hash_map[hash_function][1],hash_map[hash_function][2],\
			hash_map[hash_function][3],verbose)
	except:
		raise CatalystError,"Error generating hash, is appropriate utility installed on your system?"

def calc_hash(file,cmd,cmd_args,id_string="MD5",verbose=False):
	a=os.popen(cmd+" "+cmd_args+" "+file)
	mylines=a.readlines()
	a.close()
	mylines=mylines[0].split()
	result=mylines[0]
	if verbose:
		print id_string+" (%s) = %s" % (file, result)
	return result

def calc_hash2(file,cmd,cmd_args,id_string="MD5",verbose=False):
	a=os.popen(cmd+" "+cmd_args+" "+file)
	header=a.readline()
	mylines=a.readline().split()
	hash=mylines[0]
	short_file=os.path.split(mylines[1])[1]
	a.close()
	result=header+hash+"  "+short_file+"\n"
	if verbose:
		print header+" (%s) = %s" % (short_file, result)
	return result

# This has map must be defined after the function calc_hash
# It is possible to call different functions from this but they must be defined
# before hash_map
# Key,function,cmd,cmd_args,Print string
hash_map={
	 "adler32":[calc_hash2,"shash","-a ADLER32","ADLER32"],\
	 "crc32":[calc_hash2,"shash","-a CRC32","CRC32"],\
	 "crc32b":[calc_hash2,"shash","-a CRC32B","CRC32B"],\
	 "gost":[calc_hash2,"shash","-a GOST","GOST"],\
	 "haval128":[calc_hash2,"shash","-a HAVAL128","HAVAL128"],\
	 "haval160":[calc_hash2,"shash","-a HAVAL160","HAVAL160"],\
	 "haval192":[calc_hash2,"shash","-a HAVAL192","HAVAL192"],\
	 "haval224":[calc_hash2,"shash","-a HAVAL224","HAVAL224"],\
	 "haval256":[calc_hash2,"shash","-a HAVAL256","HAVAL256"],\
	 "md2":[calc_hash2,"shash","-a MD2","MD2"],\
	 "md4":[calc_hash2,"shash","-a MD4","MD4"],\
	 "md5":[calc_hash2,"shash","-a MD5","MD5"],\
	 "ripemd128":[calc_hash2,"shash","-a RIPEMD128","RIPEMD128"],\
	 "ripemd160":[calc_hash2,"shash","-a RIPEMD160","RIPEMD160"],\
	 "ripemd256":[calc_hash2,"shash","-a RIPEMD256","RIPEMD256"],\
	 "ripemd320":[calc_hash2,"shash","-a RIPEMD320","RIPEMD320"],\
	 "sha1":[calc_hash2,"shash","-a SHA1","SHA1"],\
	 "sha224":[calc_hash2,"shash","-a SHA224","SHA224"],\
	 "sha256":[calc_hash2,"shash","-a SHA256","SHA256"],\
	 "sha384":[calc_hash2,"shash","-a SHA384","SHA384"],\
	 "sha512":[calc_hash2,"shash","-a SHA512","SHA512"],\
	 "snefru128":[calc_hash2,"shash","-a SNEFRU128","SNEFRU128"],\
	 "snefru256":[calc_hash2,"shash","-a SNEFRU256","SNEFRU256"],\
	 "tiger":[calc_hash2,"shash","-a TIGER","TIGER"],\
	 "tiger128":[calc_hash2,"shash","-a TIGER128","TIGER128"],\
	 "tiger160":[calc_hash2,"shash","-a TIGER160","TIGER160"],\
	 "whirlpool":[calc_hash2,"shash","-a WHIRLPOOL","WHIRLPOOL"],\
	 }

required_config_file_values=["storedir","sharedir","distdir","portdir"]
valid_config_file_values=required_config_file_values[:]
valid_config_file_values.append("PKGCACHE")
valid_config_file_values.append("KERNCACHE")
valid_config_file_values.append("CCACHE")
valid_config_file_values.append("DISTCC")
valid_config_file_values.append("ICECREAM")
valid_config_file_values.append("ENVSCRIPT")
valid_config_file_values.append("AUTORESUME")
valid_config_file_values.append("FETCH")
valid_config_file_values.append("CLEAR_AUTORESUME")
valid_config_file_values.append("options")
valid_config_file_values.append("DEBUG")
valid_config_file_values.append("VERBOSE")
valid_config_file_values.append("PURGE")
valid_config_file_values.append("PURGEONLY")
valid_config_file_values.append("SNAPCACHE")
valid_config_file_values.append("snapshot_cache")
valid_config_file_values.append("hash_function")
valid_config_file_values.append("digests")
valid_config_file_values.append("contents")
valid_config_file_values.append("SEEDCACHE")

verbosity=1

class CatalystError(Exception):
	def __init__(self, message):
		if message:
			(type,value)=sys.exc_info()[:2]
			if value!=None:
				print
				print traceback.print_exc(file=sys.stdout)
			print
			print "!!! catalyst: "+message
			print

class LockInUse(Exception):
	def __init__(self, message):
		if message:
			#(type,value)=sys.exc_info()[:2]
			#if value!=None:
			    #print
			    #kprint traceback.print_exc(file=sys.stdout)
			print
			print "!!! catalyst lock file in use: "+message
			print

def spawn_bash(mycommand,env={},debug=False,opt_name=None,**keywords):
	"""spawn mycommand as an arguement to bash"""
	args=[BASH_BINARY]
	if not opt_name:
	    opt_name=mycommand.split()[0]
	if not "BASH_ENV" in env:
	    env["BASH_ENV"] = "/etc/spork/is/not/valid/profile.env"
	if debug:
	    args.append("-x")
	args.append("-c")
	args.append(mycommand)
	return spawn(args,env=env,opt_name=opt_name,**keywords)

#def spawn_get_output(mycommand,spawn_type=spawn,raw_exit_code=False,emulate_gso=True, \
#        collect_fds=[1],fd_pipes=None,**keywords):
def spawn_get_output(mycommand,raw_exit_code=False,emulate_gso=True, \
        collect_fds=[1],fd_pipes=None,**keywords):
        """call spawn, collecting the output to fd's specified in collect_fds list
        emulate_gso is a compatability hack to emulate commands.getstatusoutput's return, minus the
        requirement it always be a bash call (spawn_type controls the actual spawn call), and minus the
        'lets let log only stdin and let stderr slide by'.

        emulate_gso was deprecated from the day it was added, so convert your code over.
        spawn_type is the passed in function to call- typically spawn_bash, spawn, spawn_sandbox, or spawn_fakeroot"""
        global selinux_capable
        pr,pw=os.pipe()

        #if type(spawn_type) not in [types.FunctionType, types.MethodType]:
        #        s="spawn_type must be passed a function, not",type(spawn_type),spawn_type
        #        raise Exception,s

        if fd_pipes==None:
                fd_pipes={}
                fd_pipes[0] = 0

        for x in collect_fds:
                fd_pipes[x] = pw
        keywords["returnpid"]=True

        mypid=spawn_bash(mycommand,fd_pipes=fd_pipes,**keywords)
        os.close(pw)
        if type(mypid) != types.ListType:
                os.close(pr)
                return [mypid, "%s: No such file or directory" % mycommand.split()[0]]

        fd=os.fdopen(pr,"r")
        mydata=fd.readlines()
        fd.close()
        if emulate_gso:
                mydata=string.join(mydata)
                if len(mydata) and mydata[-1] == "\n":
                        mydata=mydata[:-1]
        retval=os.waitpid(mypid[0],0)[1]
        cleanup(mypid)
        if raw_exit_code:
                return [retval,mydata]
        retval=process_exit_code(retval)
        return [retval, mydata]


# base spawn function
def spawn(mycommand,env={},raw_exit_code=False,opt_name=None,fd_pipes=None,returnpid=False,\
	 uid=None,gid=None,groups=None,umask=None,logfile=None,path_lookup=True,\
	 selinux_context=None, raise_signals=False, func_call=False):
        """base fork/execve function.
	mycommand is the desired command- if you need a command to execute in a bash/sandbox/fakeroot
	environment, use the appropriate spawn call.  This is a straight fork/exec code path.
	Can either have a tuple, or a string passed in.  If uid/gid/groups/umask specified, it changes
	the forked process to said value.  If path_lookup is on, a non-absolute command will be converted
	to an absolute command, otherwise it returns None.

	selinux_context is the desired context, dependant on selinux being available.
	opt_name controls the name the processor goes by.
	fd_pipes controls which file descriptor numbers are left open in the forked process- it's a dict of
	current fd's raw fd #, desired #.

	func_call is a boolean for specifying to execute a python function- use spawn_func instead.
	raise_signals is questionable.  Basically throw an exception if signal'd.  No exception is thrown
	if raw_input is on.

	logfile overloads the specified fd's to write to a tee process which logs to logfile
	returnpid returns the relevant pids (a list, including the logging process if logfile is on).

	non-returnpid calls to spawn will block till the process has exited, returning the exitcode/signal
	raw_exit_code controls whether the actual waitpid result is returned, or intrepretted."""


	myc=''
	if not func_call:
		if type(mycommand)==types.StringType:
			mycommand=mycommand.split()
		myc = mycommand[0]
		if not os.access(myc, os.X_OK):
			if not path_lookup:
				return None
			myc = catalyst.util.find_binary(myc)
			if myc == None:
			    return None
        mypid=[]
	if logfile:
		pr,pw=os.pipe()
		mypid.extend(spawn(('tee','-i','-a',logfile),returnpid=True,fd_pipes={0:pr,1:1,2:2}))
		retval=os.waitpid(mypid[-1],os.WNOHANG)[1]
		if retval != 0:
			# he's dead jim.
			if raw_exit_code:
				return retval
			return process_exit_code(retval)

		if fd_pipes == None:
			fd_pipes={}
			fd_pipes[0] = 0
		fd_pipes[1]=pw
		fd_pipes[2]=pw

	if not opt_name:
		opt_name = mycommand[0]
	myargs=[opt_name]
	myargs.extend(mycommand[1:])
	global spawned_pids
	mypid.append(os.fork())
	if mypid[-1] != 0:
		#log the bugger.
		spawned_pids.extend(mypid)

	if mypid[-1] == 0:
		if func_call:
			spawned_pids = []

		# this may look ugly, but basically it moves file descriptors around to ensure no
		# handles that are needed are accidentally closed during the final dup2 calls.
		trg_fd=[]
		if type(fd_pipes)==types.DictType:
			src_fd=[]
			k=fd_pipes.keys()
			k.sort()

			#build list of which fds will be where, and where they are at currently
			for x in k:
				trg_fd.append(x)
				src_fd.append(fd_pipes[x])

			# run through said list dup'ing descriptors so that they won't be waxed
			# by other dup calls.
			for x in range(0,len(trg_fd)):
				if trg_fd[x] == src_fd[x]:
					continue
				if trg_fd[x] in src_fd[x+1:]:
					new=os.dup2(trg_fd[x],max(src_fd) + 1)
					os.close(trg_fd[x])
					try:
						while True:
							src_fd[s.index(trg_fd[x])]=new
					except SystemExit, e:
						raise
					except:
						pass

			# transfer the fds to their final pre-exec position.
			for x in range(0,len(trg_fd)):
				if trg_fd[x] != src_fd[x]:
					os.dup2(src_fd[x], trg_fd[x])
		else:
			trg_fd=[0,1,2]

		# wax all open descriptors that weren't requested be left open.
		for x in range(0,max_fd_limit):
			if x not in trg_fd:
				try:
					os.close(x)
                                except SystemExit, e:
                                        raise
                                except:
                                        pass

                # note this order must be preserved- can't change gid/groups if you change uid first.
                if selinux_capable and selinux_context:
                        import selinux
                        selinux.setexec(selinux_context)
                if gid:
                        os.setgid(gid)
                if groups:
                        os.setgroups(groups)
                if uid:
                        os.setuid(uid)
                if umask:
                        os.umask(umask)
                else:
                        os.umask(022)

                try:
                        #print "execing", myc, myargs
                        if func_call:
                                # either use a passed in func for interpretting the results, or return if no exception.
                                # note the passed in list, and dict are expanded.
                                if len(mycommand) == 4:
                                        os._exit(mycommand[3](mycommand[0](*mycommand[1],**mycommand[2])))
                                try:
                                        mycommand[0](*mycommand[1],**mycommand[2])
                                except Exception,e:
                                        print "caught exception",e," in forked func",mycommand[0]
                                sys.exit(0)

			#os.execvp(myc,myargs)
                        os.execve(myc,myargs,env)
                except SystemExit, e:
                        raise
                except Exception, e:
                        if not func_call:
                                raise str(e)+":\n   "+myc+" "+string.join(myargs)
                        print "func call failed"

                # If the execve fails, we need to report it, and exit
                # *carefully* --- report error here
                os._exit(1)
                sys.exit(1)
                return # should never get reached

        # if we were logging, kill the pipes.
        if logfile:
                os.close(pr)
                os.close(pw)

        if returnpid:
                return mypid

        # loop through pids (typically one, unless logging), either waiting on their death, or waxing them
        # if the main pid (mycommand) returned badly.
        while len(mypid):
                retval=os.waitpid(mypid[-1],0)[1]
                if retval != 0:
                        cleanup(mypid[0:-1],block_exceptions=False)
                        # at this point we've killed all other kid pids generated via this call.
                        # return now.
                        if raw_exit_code:
                                return retval
                        return process_exit_code(retval,throw_signals=raise_signals)
                else:
                        mypid.pop(-1)
        cleanup(mypid)
        return 0

def cmd(mycmd,myexc="",env={}):
	try:
		sys.stdout.flush()
		retval=spawn_bash(mycmd,env)
		if retval != 0:
			raise CatalystError,myexc
	except:
		raise

def process_exit_code(retval,throw_signals=False):
        """process a waitpid returned exit code, returning exit code if it exit'd, or the
        signal if it died from signalling
        if throw_signals is on, it raises a SystemExit if the process was signaled.
        This is intended for usage with threads, although at the moment you can't signal individual
        threads in python, only the master thread, so it's a questionable option."""
        if (retval & 0xff)==0:
                return retval >> 8 # return exit code
        else:
                if throw_signals:
                        #use systemexit, since portage is stupid about exception catching.
                        raise SystemExit()
                return (retval & 0xff) << 8 # interrupted by signal


def file_locate(settings,filelist,expand=1):
	#if expand=1, non-absolute paths will be accepted and
	# expanded to os.getcwd()+"/"+localpath if file exists
	for myfile in filelist:
		if not myfile in settings:
			#filenames such as cdtar are optional, so we don't assume the variable is defined.
			pass
		else:
		    if len(settings[myfile])==0:
			    raise CatalystError, "File variable \""+myfile+"\" has a length of zero (not specified.)"
		    if settings[myfile][0]=="/":
			    if not os.path.exists(settings[myfile]):
				    raise CatalystError, "Cannot locate specified "+myfile+": "+settings[myfile]
		    elif expand and os.path.exists(os.getcwd()+"/"+settings[myfile]):
			    settings[myfile]=os.getcwd()+"/"+settings[myfile]
		    else:
			    raise CatalystError, "Cannot locate specified "+myfile+": "+settings[myfile]+" (2nd try)"
"""
Spec file format:

The spec file format is a very simple and easy-to-use format for storing data. Here's an example
file:

item1: value1
item2: foo bar oni
item3:
	meep
	bark
	gleep moop

This file would be interpreted as defining three items: item1, item2 and item3. item1 would contain
the string value "value1". Item2 would contain an ordered list [ "foo", "bar", "oni" ]. item3
would contain an ordered list as well: [ "meep", "bark", "gleep", "moop" ]. It's important to note
that the order of multiple-value items is preserved, but the order that the items themselves are
defined are not preserved. In other words, "foo", "bar", "oni" ordering is preserved but "item1"
"item2" "item3" ordering is not, as the item strings are stored in a dictionary (hash).
"""

def parse_makeconf(mylines):
	mymakeconf={}
	pos=0
	pat=re.compile("([0-9a-zA-Z_]*)=(.*)")
	while pos<len(mylines):
		if len(mylines[pos])<=1:
			#skip blanks
			pos += 1
			continue
		if mylines[pos][0] in ["#"," ","\t"]:
			#skip indented lines, comments
			pos += 1
			continue
		else:
			myline=mylines[pos]
			mobj=pat.match(myline)
			pos += 1
			if mobj.group(2):
			    clean_string = re.sub(r"\"",r"",mobj.group(2))
			    mymakeconf[mobj.group(1)]=clean_string
	return mymakeconf

def read_makeconf(mymakeconffile):
	if os.path.exists(mymakeconffile):
		try:
			try:
				import snakeoil.fileutils
				return snakeoil.fileutils.read_bash_dict(mymakeconffile, sourcing_command="source")
			except ImportError:
				try:
					import portage_util
					return portage_util.getconfig(mymakeconffile, tolerant=1, allow_sourcing=True)
				except ImportError:
					myf=open(mymakeconffile,"r")
					mylines=myf.readlines()
					myf.close()
					return parse_makeconf(mylines)
		except:
			raise CatalystError, "Could not parse make.conf file "+mymakeconffile
	else:
		makeconf={}
		return makeconf

def pathcompare(path1,path2):
	# Change double slashes to slash
	path1 = re.sub(r"//",r"/",path1)
	path2 = re.sub(r"//",r"/",path2)
	# Removing ending slash
	path1 = re.sub("/$","",path1)
	path2 = re.sub("/$","",path2)

	if path1 == path2:
		return 1
	return 0

def ismount(path):
	"enhanced to handle bind mounts"
	if os.path.ismount(path):
		return 1
	a=os.popen("mount")
	mylines=a.readlines()
	a.close()
	for line in mylines:
		mysplit=line.split()
		if pathcompare(path,mysplit[2]):
			return 1
	return 0

def addl_arg_parse(myspec,addlargs,requiredspec,validspec):
	"helper function to help targets parse additional arguments"
	global valid_config_file_values

	for x in addlargs.keys():
		if x not in validspec and x not in valid_config_file_values and x not in requiredspec:
			raise CatalystError, "Argument \""+x+"\" not recognized."
		else:
			myspec[x]=addlargs[x]

	for x in requiredspec:
		if not x in myspec:
			raise CatalystError, "Required argument \""+x+"\" not specified."

def touch(myfile):
	try:
		myf=open(myfile,"w")
		myf.close()
	except IOError:
		raise CatalystError, "Could not touch "+myfile+"."

def countdown(secs=5, doing="Starting"):
        if secs:
		print ">>> Waiting",secs,"seconds before starting..."
		print ">>> (Control-C to abort)...\n"+doing+" in: ",
		ticks=range(secs)
		ticks.reverse()
		for sec in ticks:
			sys.stdout.write(str(sec+1)+" ")
			sys.stdout.flush()
			time.sleep(1)
		print

