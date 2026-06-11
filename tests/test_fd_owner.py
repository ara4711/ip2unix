import subprocess
import sys

from helper import IP2UNIX

# The F_SETOWN fd owner must survive the socket replacement done at bind.
TESTPROG = r'''
import fcntl
import os
import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
fcntl.fcntl(sock.fileno(), fcntl.F_SETOWN, os.getpid())
sock.bind(('1.2.3.4', 5))
owner = fcntl.fcntl(sock.fileno(), fcntl.F_GETOWN)
assert owner == os.getpid(), '%d != %d' % (owner, os.getpid())
'''


def test_fd_owner_survives_bind(tmpdir):
    sockfile = str(tmpdir.join('foo.sock'))
    cmd = [IP2UNIX, '-r', 'path=' + sockfile, sys.executable, '-c', TESTPROG]
    assert subprocess.run(cmd).returncode == 0
