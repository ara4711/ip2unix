import subprocess
import sys

from helper import IP2UNIX

# The synthesised IPv4 peer address encodes the peer's PID (peer-cred lookup).
TESTPROG = r'''
import os
import socket
import struct

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('1.2.3.4', 5))
server.listen(1)

childpid = os.fork()
if childpid == 0:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(('1.2.3.4', 5))
        sock.recv(1)
    raise SystemExit

with server.accept()[0] as conn:
    peer_ip = conn.getpeername()[0]
    conn.sendall(b'x')

peer_pid = struct.unpack('>I', socket.inet_aton(peer_ip))[0]
assert peer_pid == childpid, '%d != %d' % (peer_pid, childpid)
os.waitpid(childpid, 0)
'''


def test_peer_address_encodes_pid(tmpdir):
    sockfile = str(tmpdir.join('foo.sock'))
    cmd = [IP2UNIX, '-r', 'path=' + sockfile, sys.executable, '-c', TESTPROG]
    assert subprocess.run(cmd).returncode == 0
