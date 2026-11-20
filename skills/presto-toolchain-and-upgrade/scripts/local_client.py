#!/usr/bin/env python3
"""Same-host Unix-socket client; no SSH, remote controller or credentials."""
import json
import socket

def request_service(path, operation, timeout=1800):
    if operation not in {'sync', 'status'}:
        raise ValueError('Local service accepts sync/status only')
    with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as connection:
        connection.settimeout(timeout)
        connection.connect(path)
        connection.sendall(json.dumps({'operation': operation}).encode() + b'\n')
        with connection.makefile('rb') as stream:
            raw = stream.readline(16 * 1024 * 1024 + 1)
        if not raw.endswith(b'\n') or len(raw) > 16 * 1024 * 1024:
            raise ValueError('Missing or oversized local service result')
        result = json.loads(raw)
        if not isinstance(result, dict) or 'status' not in result:
            raise ValueError('Invalid local service result')
        return result
