
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

    # Save fds of current namespaces
    for ns in [ns for ns in namespaces if ns[0]]:
        fp = open(f"/proc/self/ns/{ns[1]}")
        namespaces[ns] = fp

    simple_unshare(mount=mount, uts=uts, ipc=ipc, net=net, pid=pid, user=user,
                   hostname=hostname)
    try:
        yield
    finally:
        for ns in [ns for ns in namespaces if ns[0]]:
            fp = namespaces[ns]
            setns(fp.fileno(), 0)
            fp.close()
