#!/usr/bin/env python3
"""Fixed sync/status gateway for a same-host privileged installer."""
import argparse
import json
import os
from pathlib import Path
import socketserver
import struct
import subprocess
import sys

class Handler(socketserver.StreamRequestHandler):
    def handle(self):
        try:
            self.connection.settimeout(10)
            if hasattr(__import__('socket'), 'SO_PEERCRED'):
                import socket
                _, uid, _ = struct.unpack('3i', self.connection.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, 12))
                if uid not in self.server.allowed_uids:
                    raise ValueError('Caller UID is not permitted')
            raw = self.rfile.readline(257)
            if not raw.endswith(b'\n') or len(raw) > 256:
                raise ValueError('Invalid request size')
            request = json.loads(raw)
            if set(request) != {'operation'} or request['operation'] not in {'sync', 'status'}:
                raise ValueError('Only sync/status are accepted')
            operation = request['operation']
            self.connection.settimeout(1800)
            run = subprocess.run([sys.executable, self.server.engine, '--config', self.server.config, operation], capture_output=True, timeout=1800)
            result = json.loads(run.stdout)
            if not isinstance(result, dict) or 'status' not in result:
                raise ValueError('Invalid installer result')
        except Exception as error:
            result = {'status': 'blocked', 'reason': str(error)}
        self.wfile.write(json.dumps(result).encode() + b'\n')

class Server(socketserver.ThreadingUnixStreamServer):
    daemon_threads = True

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--socket', required=True)
    parser.add_argument('--engine', required=True)
    parser.add_argument('--config', required=True)
    parser.add_argument('--allow-uid', action='append', type=int, required=True)
    parser.add_argument('--socket-gid', type=int)
    args = parser.parse_args()
    path = Path(args.socket)
    # The socket parent is operator-owned, not writable by ordinary agents.
    parent = path.parent.stat()
    if parent.st_uid != os.getuid() or parent.st_mode & 0o022:
        raise ValueError('Socket parent must be owned by service user without group/world write')
    path.unlink(missing_ok=True)
    try:
        with Server(str(path), Handler) as server:
            os.chmod(path, 0o660)
            if args.socket_gid is not None:
                os.chown(path, os.getuid(), args.socket_gid)
            server.engine = str(Path(args.engine).resolve())
            server.config = str(Path(args.config).resolve())
            server.allowed_uids = set(args.allow_uid)
            server.serve_forever()
    finally:
        path.unlink(missing_ok=True)

if __name__ == '__main__':
    main()
