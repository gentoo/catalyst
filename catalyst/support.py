
import glob
import sys
import os
import shutil
import time
from pathlib import Path
from subprocess import Popen, PIPE

import libmount

from portage.repository.config import RepoConfig
from tempfile import TemporaryDirectory

from snakeoil.bash import read_bash_dict

from catalyst import log
from catalyst.context import namespace

BASH_BINARY = "/bin/bash"


class CatalystError(Exception):
    def __init__(self, message, print_traceback=False):
        if message:
            log.error('CatalystError: %s', message, exc_info=print_traceback)

def command(name):
    c = shutil.which(name)
    if not c:
        raise CatalystError(f'"{name}" not found or is not executable')
    return c

def cmd(mycmd, env=None, debug=False, fail_func=None):
    """Run the external |mycmd|.

    If |mycmd| is a string, then it's assumed to be a bash snippet and will
    be run through bash.  Otherwise, it's a standalone command line and will
    be run directly.
    """
    log.debug('cmd: %r', mycmd)
    sys.stdout.flush()

    if env is None:
        env = {}
    if 'BASH_ENV' not in env:
        env = env.copy()
        env['BASH_ENV'] = '/etc/spork/is/not/valid/profile.env'

    args = []
    if isinstance(mycmd, str):
        args.append(BASH_BINARY)
        if debug:
            args.append('-x')
        args.extend(['-c', mycmd])
    else:
        args.extend(mycmd)

    log.debug('args: %r', args)
    proc = Popen(args, env=env)
    ret = proc.wait()
    if ret:
        if fail_func:
            log.error('cmd(%r) exited %s; running fail_func().', args, ret)
            fail_func()
        raise CatalystError('cmd(%r) exited %s' % (args, ret),
                            print_traceback=False)

def sed(my_re, my_in):
    """Apply the regular expression |my_re| on the string |my_in| using sed.
    """
    log.debug('sed: regex: %r', my_re)
    log.debug('sed: input: %r', my_in)
    sys.stdout.flush()

    p = Popen(["sed", "-E", "-e", my_re.encode('utf-8')], stdin=PIPE, stdout=PIPE, stderr=PIPE)
    (my_out_b, my_err_b) = p.communicate(my_in.encode('utf-8'))

    if my_err_b:
        my_err=my_err_b.decode('utf-8');
        raise CatalystError('sed error output %s' % (my_err), print_traceback=False)

    my_out=my_out_b.decode('utf-8');
    log.debug('sed: out  : %r', my_out)
    sys.stdout.flush()

    return my_out

def file_check(filepath, extensions=None):
    '''Check for the files existence and that only one exists
    if others are found with various extensions
    '''
    if os.path.isfile(filepath):
        return filepath
    # it didn't exist
    # so check if there are files of that name with an extension
    files = glob.glob("%s.*" % filepath)
    # remove any false positive files
    files = [x for x in files if
             not x.endswith(".CONTENTS") and
             not x.endswith(".CONTENTS.gz") and
             not x.endswith(".DIGESTS") and
             not x.endswith(".sha256")]
    if len(files) == 1:
        return files[0]
    if len(files) > 1:
        msg = "Ambiguous Filename: %s\nPlease specify the correct extension as well" % filepath
        raise CatalystError(msg, print_traceback=False)
    target_file = None
    for ext in extensions:
        target = filepath + "." + ext
        if target in files:
            target_file = target
            break
    if target_file:
        return target_file
    raise CatalystError("File Not Found: %s" % filepath)


def file_locate(settings, filelist, expand=1):
    # if expand=1, non-absolute paths will be accepted and
    # expanded to os.getcwd()+"/"+localpath if file exists
    for myfile in filelist:
        if myfile not in settings:
            # filenames such as cdtar are optional, so we don't assume the variable is defined.
            pass
        else:
            if not settings[myfile]:
                raise CatalystError("File variable \"" + myfile +
                                    "\" has a length of zero (not specified.)", print_traceback=True)
            if settings[myfile][0] == "/":
                if not os.path.exists(settings[myfile]):
                    raise CatalystError("Cannot locate specified " + myfile +
                                        ": " + settings[myfile], print_traceback=False)
            elif expand and os.path.exists(os.getcwd()+"/"+settings[myfile]):
                settings[myfile] = os.getcwd()+"/"+settings[myfile]
            else:
                raise CatalystError("Cannot locate specified " + myfile +
                                    ": "+settings[myfile]+" (2nd try)" +
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
""",
                                    print_traceback=True)


def read_makeconf(mymakeconffile):
    if os.path.exists(mymakeconffile):
        try:
            return read_bash_dict(mymakeconffile, sourcing_command="source")
        except Exception as e:
            raise CatalystError("Could not parse make.conf file " +
                                mymakeconffile, print_traceback=True) from e
    else:
        makeconf = {}
        return makeconf


def get_repo_name_from_dir(repo_path):
    """ Get the name of the repo at the given repo_path.

         References:
         https://wiki.gentoo.org/wiki/Repository_format/profiles/repo_name
         https://wiki.gentoo.org/wiki/Repository_format/metadata/layout.conf#repo-name
    """

    repo_config = RepoConfig(None, {"location": repo_path})

    if repo_config.missing_repo_name:
        raise CatalystError(f"Missing name in repository {repo_path}")

    return repo_config.name


def get_repo_name_from_squash(repo_squash_path):
    """ Get the name of the repo at the given repo_squash_path.
        To obtain the name, the squash file is mounted to a temporary directory.
    """

    repo_name = None

    # Mount squash file to temp directory in separate mount namespace
    with TemporaryDirectory() as temp, namespace(mount=True):
        try:
            source = str(repo_squash_path)
            target = str(temp)
            fstype = 'squashfs'
            options = 'ro,loop'
            cxt = libmount.Context(source=source, target=target,
                                   fstype=fstype, options=options)
            cxt.mount()
            repo_name = get_repo_name_from_dir(target)

        except Exception as e:
            raise CatalystError(f"Couldn't mount: {source}, {e}") from e

    return repo_name


def get_repo_name(repo_path):
    if not Path(repo_path).is_dir():
        return get_repo_name_from_squash(repo_path)

    return get_repo_name_from_dir(repo_path)


def ismount(path):
    """Like os.path.ismount, but also support bind mounts"""
    path = Path(path)
    if path.is_mount():
        return True

    cxt = libmount.Context()
    while (fs := cxt.mtab.next_fs()) is not None:
        if path == Path(fs.target):
            return True

    return False


def addl_arg_parse(myspec, addlargs, requiredspec, validspec):
    "helper function to help targets parse additional arguments"
    messages = []
    for x in addlargs.keys():
        if x not in validspec and x not in requiredspec:
            messages.append("Argument \""+x+"\" not recognized.")
        else:
            myspec[x] = addlargs[x]

    for x in requiredspec:
        if x not in myspec:
            messages.append("Required argument \""+x+"\" not specified.")

    if messages:
        raise CatalystError('\n\tAlso: '.join(messages))


def countdown(secs=5, doing="Starting"):
    # Don't sleep if this is non-interactive
    if not os.isatty(sys.stdin.fileno()) or secs == 0:
        return

    sys.stdout.write(
        ('>>> Waiting %s seconds before starting...\n'
         '>>> (Control-C to abort)...\n'
         '%s in: ') % (secs, doing))
    for sec in reversed(range(1, secs + 1)):
        sys.stdout.write(str(sec) + " ")
        sys.stdout.flush()
        time.sleep(1)
    sys.stdout.write('\n')


def normpath(mypath):
    """Clean up a little more than os.path.normpath

    Namely:
     - Make sure leading // is turned into /.
     - Leave trailing slash intact.
    """
    TrailingSlash = False
    if mypath[-1] == "/":
        TrailingSlash = True
    newpath = os.path.normpath(mypath)
    if len(newpath) > 1:
        if newpath[:2] == "//":
            newpath = newpath[1:]
    if TrailingSlash:
        newpath = newpath+'/'
    return newpath


def sanitize_name(name: str) -> str:
    """
    Normalize name by replacing [.-/] with _, so it may be used as a
    variable name in bash
    """
    table = str.maketrans(".-/", "___")
    return name.translate(table)
