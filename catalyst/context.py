
import contextlib
import os

from snakeoil.process.namespaces import setns, simple_unshare

@contextlib.contextmanager
def namespace(mount=False, uts=False, ipc=False, net=False, pid=False,
              user=False, hostname=None):
    namespaces = {
        (mount, "mnt"):  None,
        (uts,   "uts"):  None,
        (ipc,   "ipc"):  None,
        (net,   "net"):  None,
        (pid,   "pid"):  None,
        (user,  "user"): None,
    }

    dirs = {
        "root": None,
        "cwd":  None,
    }

    # Save fds of current namespaces
    for ns in [ns for ns in namespaces if ns[0]]:
        fp = open(f"/proc/self/ns/{ns[1]}")
        namespaces[ns] = fp

    # Save fds of current directories
    if mount:
        for d in dirs:
            dirs[d] = os.open(f"/proc/self/{d}", os.O_RDONLY)

    simple_unshare(mount=mount, uts=uts, ipc=ipc, net=net, pid=pid, user=user,
                   hostname=hostname)
    try:
        yield
    finally:
        for ns in [ns for ns in namespaces if ns[0]]:
            fp = namespaces[ns]
            setns(fp.fileno(), 0)
            fp.close()

        if mount:
            # Restore original root and cwd. Since we cannot directly chroot to
            # a fd, first change the current directory to the fd of the
            # original root, then chroot to "."

            os.fchdir(dirs["root"])
            os.chroot(".")
            os.fchdir(dirs["cwd"])

            for fd in dirs.values():
                os.close(fd)
