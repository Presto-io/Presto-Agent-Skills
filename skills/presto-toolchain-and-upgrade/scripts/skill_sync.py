#!/usr/bin/env python3
"""Git-backed skill fleet synchronizer. Python 3.9+, Git; private JSON configuration."""
import argparse
import base64
import contextlib
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import time
import uuid

RETIRED = {'school-presentation', 'resume-generation', 'jiaoan-jihua', 'jiaoan-shicao'}
PRIVATE = {'uws-workspace'}
IGNORE = {'__pycache__', '.DS_Store'}
FORBIDDEN = {'.git', '.secrets', '.env', '.work', '.venv', 'venv', 'history', 'backups', 'sources', 'source', 'output', 'delivery', 'node_modules'}
NAME = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')

class Blocked(Exception):
    pass

def digest(data):
    return hashlib.sha256(data).hexdigest()

def dump(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        with temp.open('x', encoding='utf-8') as f:
            json.dump(value, f, ensure_ascii=False, sort_keys=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temp, path)
    finally:
        temp.unlink(missing_ok=True)

def load(path, default=None):
    return json.loads(Path(path).read_text()) if Path(path).exists() else default

def file_path(root, relative):
    p = PurePosixPath(relative)
    if not relative or p.is_absolute() or '..' in p.parts or '\\' in relative or str(p) != relative:
        raise Blocked('Invalid relative path')
    target = Path(root).joinpath(*p.parts)
    for ancestor in [target, *target.parents]:
        if ancestor.is_symlink():
            raise Blocked('Symlink path refused: ' + relative)
    return target

def snapshot(root, blobs=None):
    root = Path(root)
    if root.is_symlink():
        raise Blocked('Skill symlink refused: ' + str(root))
    if not root.exists():
        return None
    if not root.is_dir():
        raise Blocked('Skill is not a directory: ' + str(root))
    result = {}
    for p in sorted(root.rglob('*')):
        rel = p.relative_to(root).as_posix()
        if any(part in IGNORE for part in p.relative_to(root).parts) or p.suffix == '.pyc':
            continue
        if p.is_symlink() or not (p.is_file() or p.is_dir()):
            raise Blocked('Special file refused: ' + str(p))
        if p.is_file():
            data = p.read_bytes()
            if len(data) > 64 * 1024 * 1024:
                raise Blocked('File exceeds 64 MiB: ' + str(p))
            sha = digest(data)
            result[rel] = {'sha': sha, 'mode': 0o755 if p.stat().st_mode & 0o111 else 0o644}
            if blobs is not None:
                blobs.setdefault(sha, data)
    return result

def put_tree(root, tree, blobs):
    root = Path(root)
    root.mkdir(parents=True, exist_ok=True)
    for rel, item in tree.items():
        p = file_path(root, rel)
        p.parent.mkdir(parents=True, exist_ok=True)
        data = blobs[item['sha']]
        if digest(data) != item['sha']:
            raise Blocked('Blob checksum mismatch')
        p.write_bytes(data)

        if item['mode'] not in {0o644, 0o755}:
            raise Blocked('Invalid file mode')
        p.chmod(item['mode'])

@contextlib.contextmanager
def lock(state):
    state.mkdir(parents=True, exist_ok=True)
    p = state / 'sync.lock'
    f = p.open('a+b')
    try:
        if os.name == 'nt':
            import msvcrt
            if p.stat().st_size == 0:
                f.write(b'0'); f.flush()
            f.seek(0)
            msvcrt.locking(f.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        f.close()
        raise Blocked('Another sync is running; do not remove its lock')
    try:
        yield
    finally:
        f.close()

def state_dir(config):
    return Path(config['state_dir']).expanduser().resolve()

def roots(config):
    result = []
    seen = set()
    for r in config['roots']:
        p = Path(r['path']).expanduser().resolve()
        if p in seen:
            continue
        seen.add(p)
        result.append(dict(r, path=str(p)))
    state = state_dir(config)
    for r in result:
        p = Path(r['path'])
        if p == state or p in state.parents or state in p.parents:
            raise Blocked('State/backups must be outside skill roots')
    return result

def endpoint_export(config, request):
    known = set(request.get('known', []))
    names = request['names']
    if any(not NAME.fullmatch(n) or n in PRIVATE | RETIRED | set(config.get('private_skills', [])) for n in names):
        raise Blocked('Private, archived or invalid skill requested')
    blobs = {}
    copies = []
    for r in roots(config):
        for name in names:
            target = Path(r['path']) / name
            if target.is_symlink() and any(target.resolve() == Path(other['path']) / name for other in roots(config)):
                continue
            tree = snapshot(target, blobs)
            if tree is not None or r.get('install_missing', False):
                copies.append({'root': r['path'], 'name': name, 'tree': tree})
    return {'copies': copies, 'blobs': {sha: base64.b64encode(data).decode('ascii') for sha, data in blobs.items() if sha not in known}}

def endpoint_apply(config, request):
    state = state_dir(config)
    with lock(state):
        for pending in (state / 'backups').glob('*/journal.json'):
            if load(pending).get('status') == 'prepared':
                raise Blocked('Interrupted installation; inspect journal before retry: ' + str(pending))
        approved = {r['path'] for r in roots(config)}
        blobs = decode_blobs(request['blobs'])
        actions = request['actions']
        targets = set()
        before = {}
        for a in actions:
            if a['root'] not in approved or not NAME.fullmatch(a['name']) or a['name'] in PRIVATE | set(config.get('private_skills', [])) or (a['name'] in RETIRED and a['tree'] is not None):
                raise Blocked('Unregistered target')
            target = Path(a['root']) / a['name']
            if target in targets:
                raise Blocked('Duplicate target')
            targets.add(target)
            current = snapshot(target)
            if current != a['expected']:
                raise Blocked('Changed since collection: ' + str(target))
            before[str(target)] = current
            if a['tree'] is None and a['name'] not in RETIRED:
                raise Blocked('Whole-skill deletion requires retirement policy')
        run = state / 'backups' / uuid.uuid4().hex
        run.mkdir(parents=True)
        journal = []
        dump(run / 'journal.json', {'status': 'prepared', 'before': before})
        try:
            for i, a in enumerate(actions):
                target = Path(a['root']) / a['name']
                if a['expected'] == a['tree']:
                    continue
                target.parent.mkdir(parents=True, exist_ok=True)
                if target.parent.stat().st_dev != run.stat().st_dev:
                    raise Blocked('Configure state_dir on the installation filesystem')
                stage = run / ('candidate-' + str(i))
                if a['tree'] is not None:
                    put_tree(stage, a['tree'], blobs)
                    if snapshot(stage) != a['tree']:
                        raise Blocked('Candidate verification failed')
                # Recheck immediately before the rename, after staging.
                if snapshot(target) != a['expected']:
                    raise Blocked('Concurrent edit: ' + str(target))
                backup = run / ('previous-' + str(i))
                entry = {'target': str(target), 'backup': str(backup), 'moved': False, 'published': False}
                journal.append(entry)
                dump(run / 'journal.json', {'status': 'prepared', 'entries': journal, 'before': before})
                if target.exists():
                    os.replace(target, backup)
                    entry['moved'] = True
                if a['tree'] is not None:
                    os.replace(stage, target)
                    entry['published'] = True
                dump(run / 'journal.json', {'status': 'prepared', 'entries': journal, 'before': before})
                if snapshot(target) != a['tree']:
                    raise Blocked('Installed checksum mismatch')
            dump(run / 'journal.json', {'status': 'committed', 'before': before})
        except BaseException:
            for entry in reversed(journal):
                target, backup = Path(entry['target']), Path(entry['backup'])
                if entry['published'] and target.exists():
                    shutil.rmtree(target)
                if entry['moved'] and backup.exists():
                    os.replace(backup, target)
            dump(run / 'journal.json', {'status': 'rolled_back', 'before': before})
            raise
        for a in actions:
            if a['name'] == 'presto-toolchain-and-upgrade':
                # Also refresh on no-op retries after an earlier refresh failure.
                available = dict(blobs)
                snapshot(Path(a['root']) / a['name'], available)
                refresh_engine(config, a['tree'], available)
                break
        return {'status': 'applied', 'copies': len(actions), 'backup': str(run)}

def refresh_engine(config, tree, blobs):
    destination = config.get('engine_path')
    if not destination or not tree:
        return
    item = tree.get('scripts/skill_sync.py')
    if not item:
        raise Blocked('Updated sync skill is missing its engine')
    data = blobs[item['sha']]
    compile(data, '<sync-engine>', 'exec')
    target = Path(destination).expanduser()
    temp = target.with_name(target.name + '.' + uuid.uuid4().hex + '.tmp')
    try:
        temp.write_bytes(data); temp.chmod(0o644)
        os.replace(temp, target)
    finally:
        temp.unlink(missing_ok=True)

def decode_blobs(values):
    result = {}
    for sha, encoded in values.items():
        data = base64.b64decode(encoded, validate=True)
        if digest(data) != sha:
            raise Blocked('Transport checksum mismatch')
        result[sha] = data
    return result

def run_command(argv, cwd=None, data=None, timeout=180):
    env = dict(os.environ, GIT_TERMINAL_PROMPT='0', GCM_INTERACTIVE='never')
    r = subprocess.run(argv, cwd=cwd, env=env, input=data, capture_output=True, timeout=timeout)
    if r.returncode:
        # Diagnostics remain local; do not echo arbitrary tool output or credentials.
        raise Blocked('Command failed (exit %s): %s' % (r.returncode, Path(argv[0]).name))
    return r.stdout

def git(repo, *args):
    return run_command(['git', '-c', 'core.hooksPath=/dev/null' if os.name != 'nt' else 'core.hooksPath=NUL', '-C', str(repo), *args])

def merge_value(base, local, remote):
    if local == base or local == remote:
        return remote
    if remote == base:
        return local
    raise Blocked('Concurrent property change')

def merge_file(base, local, remote, blobs, directory):
    try:
        return merge_value(base, local, remote)
    except Blocked:
        pass
    if base is None or local is None or remote is None:
        raise Blocked('Add/add or delete/modify conflict')
    mode = merge_value(base['mode'], local['mode'], remote['mode'])
    try:
        sha = merge_value(base['sha'], local['sha'], remote['sha'])
        return {'sha': sha, 'mode': mode}
    except Blocked:
        pass
    values = [blobs[x['sha']] for x in [local, base, remote]]
    try:
        for data in values:
            if b'\x00' in data:
                raise UnicodeError()
            data.decode('utf-8')
    except UnicodeError:
        raise Blocked('Binary conflict')
    paths = []
    for i, data in enumerate(values):
        p = directory / str(i); p.write_bytes(data); paths.append(str(p))
    r = subprocess.run(['git', 'merge-file', '-p', *paths], capture_output=True)
    if r.returncode:
        raise Blocked('Overlapping text changes')
    sha = digest(r.stdout); blobs[sha] = r.stdout
    return {'sha': sha, 'mode': mode}

def validate_skill(name, tree, blobs):
    if 'SKILL.md' not in tree:
        raise Blocked(name + ': missing SKILL.md')
    text = blobs[tree['SKILL.md']['sha']].decode('utf-8')
    header = text.split('---', 2)
    if len(header) != 3 or header[0].strip() or not re.search(r'^name:\s*[\"\']?' + re.escape(name) + r'[\"\']?\s*$', header[1], re.M):
        raise Blocked(name + ': invalid skill frontmatter')
    for rel, item in tree.items():
        file_path(Path('/validation'), rel)
        if any(part in FORBIDDEN or part.startswith('.env') for part in PurePosixPath(rel).parts):
            raise Blocked(name + '/' + rel + ': runtime/private path is not publishable')
        data = blobs[item['sha']]
        if re.search(rb'-----BEGIN (?:OPENSSH |RSA |EC |DSA )?PRIVATE KEY-----|gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,}', data):
            raise Blocked(name + '/' + rel + ': credential-like content')

def contact(endpoint, operation, request):
    if 'config' in endpoint:
        config = load(endpoint['config'])
        return endpoint_export(config, request) if operation == 'export' else endpoint_apply(config, request)
    raw = run_command(endpoint['command'] + [operation], data=json.dumps(request).encode(), timeout=endpoint.get('timeout', 300))
    try:
        result = json.loads(raw)
    except (ValueError, UnicodeError):
        raise Blocked(endpoint['id'] + ': invalid or truncated response')
    if result.get('status') == 'blocked':
        raise Blocked(endpoint['id'] + ': ' + result.get('reason', 'endpoint blocked'))
    return result

def fleet(config):
    state = state_dir(config)
    with lock(state):
        ledger = load(state / 'baseline.json', {'copies': {}})
        cache = state / 'repository'
        marker = state / 'owned-cache.json'
        if not cache.exists():
            run_command(['git', 'clone', '--no-checkout', config['repository'], str(cache)])
            dump(marker, {'path': str(cache.resolve()), 'repository': config['repository']})
        if load(marker) != {'path': str(cache.resolve()), 'repository': config['repository']}:
            raise Blocked('Cache is not registered as exclusively owned')
        if git(cache, 'remote', 'get-url', 'origin').decode().strip() != config['repository']:
            raise Blocked('Repository URL changed')
        branch = config.get('branch', 'main')
        if branch != 'main':
            raise Blocked('Only the configured production main branch is accepted')
        run = state / 'runs' / uuid.uuid4().hex
        run.mkdir(parents=True)
        blob_dir = state / 'blobs'; blob_dir.mkdir(exist_ok=True)
        blobs = {p.name: p.read_bytes() for p in blob_dir.iterdir() if p.is_file()}
        if any(digest(data) != sha for sha, data in blobs.items()):
            raise Blocked('Stored blob checksum mismatch')
        resolutions = load(Path(config['resolution_file']).expanduser(), {}) if config.get('resolution_file') else {}
        endpoints = config['endpoints']
        if len({e['id'] for e in endpoints}) != len(endpoints):
            raise Blocked('Duplicate endpoint id')
        collected = None
        for attempt in range(3):
            git(cache, 'fetch', 'origin', branch)
            head = git(cache, 'rev-parse', 'FETCH_HEAD').decode().strip()
            git(cache, 'checkout', '--detach', '--force', head)
            git(cache, 'clean', '-fd', '--', 'skills')
            # This is an exclusively owned checkout, never the user's divergent worktree.
            canonical = {}
            excluded = PRIVATE | RETIRED | set(config.get('private_skills', []))
            for p in sorted((cache / 'skills').iterdir()):
                if p.is_dir() and (p / 'SKILL.md').is_file() and p.name not in excluded:
                    canonical[p.name] = snapshot(p, blobs)
            if collected is None:
                collected = []
                for endpoint in endpoints:
                    packet = contact(endpoint, 'export', {'names': sorted(canonical), 'known': sorted(blobs)})
                    blobs.update(decode_blobs(packet['blobs']))
                    for copy in packet['copies']:
                        copy['endpoint'] = endpoint['id']
                        if copy['name'] not in canonical:
                            raise Blocked('Unexpected skill in endpoint response')
                        collected.append(copy)
                dump(run / 'collected.json', collected)
            desired = {n: dict(t) for n, t in canonical.items()}
            conflicts = []
            for copy in collected:
                key = json.dumps([copy['endpoint'], copy['root'], copy['name']])
                current = copy['tree']
                base = ledger['copies'].get(key)
                if base is None:
                    if current is None or current == canonical[copy['name']]:
                        continue
                    conflicts.append(dict(copy, reason='No trusted baseline; inspect/adopt this installation first'))
                    continue
                if current is None:
                    conflicts.append(dict(copy, reason='Previously installed skill is missing; do not infer global deletion'))
                    continue
                target = desired[copy['name']]
                for rel in sorted(set(base) | set(current) | set(target)):
                    try:
                        item = merge_file(base.get(rel), current.get(rel), target.get(rel), blobs, run)
                        if item is None:
                            target.pop(rel, None)
                        else:
                            target[rel] = item
                    except Blocked as error:
                        conflict = {'endpoint': copy['endpoint'], 'root': copy['root'], 'name': copy['name'], 'file': rel, 'reason': str(error), 'base': base.get(rel), 'local': current.get(rel), 'github': target.get(rel)}
                        fingerprint = digest(json.dumps(conflict, sort_keys=True).encode())
                        conflict['id'] = fingerprint
                        choice = resolutions.get(fingerprint)
                        if choice:
                            if 'take' in choice and choice['take'] in {'base', 'local', 'github'}:
                                item = conflict[choice['take']]
                            elif 'path' in choice:
                                data = Path(choice['path']).expanduser().read_bytes()
                                sha = digest(data); blobs[sha] = data
                                item = {'sha': sha, 'mode': choice.get('mode', 0o644)}
                            else:
                                raise Blocked('Invalid conflict resolution: ' + fingerprint)
                            if item is None:
                                target.pop(rel, None)
                            else:
                                target[rel] = item
                        else:
                            folder = run / 'conflict-files' / fingerprint
                            folder.mkdir(parents=True)
                            for label in ['base', 'local', 'github']:
                                if conflict[label] is not None:
                                    (folder / label).write_bytes(blobs[conflict[label]['sha']])
                            conflict['versions'] = str(folder)
                            conflicts.append(conflict)
            if conflicts:
                for sha, data in blobs.items():
                    if not (blob_dir / sha).exists():
                        (blob_dir / sha).write_bytes(data)
                dump(run / 'conflicts.json', conflicts)
                dump(state / 'last-result.json', {'status': 'conflict', 'report': str(run / 'conflicts.json')})
                raise Blocked('Conflicts need review: ' + str(run / 'conflicts.json'))
            changed = [n for n in desired if desired[n] != canonical[n]]
            for name in changed:
                validate_skill(name, desired[name], blobs)
                shutil.rmtree(cache / 'skills' / name)
                put_tree(cache / 'skills' / name, desired[name], blobs)
            for validator in config.get('validators', []):
                if set(validator['skills']) & set(changed):
                    run_command(validator['command'], cwd=cache)
            if changed:
                git(cache, 'add', '--', *['skills/' + n for n in changed])
                git(cache, '-c', 'user.name=' + config.get('author_name', 'Skill Sync'), '-c', 'user.email=' + config.get('author_email', 'skill-sync@users.noreply.github.com'), 'commit', '-m', 'sync: ' + ', '.join(changed))
                try:
                    git(cache, 'push', 'origin', 'HEAD:refs/heads/' + branch)
                except Blocked:
                    if attempt == 2:
                        raise
                    collected = None
                    continue
            published = git(cache, 'rev-parse', 'HEAD').decode().strip()
            break
        for sha, data in blobs.items():
            if not (blob_dir / sha).exists():
                (blob_dir / sha).write_bytes(data)
        pending = []
        applied = []
        for endpoint in endpoints:
            copies = [c for c in collected if c['endpoint'] == endpoint['id']]
            actions = [{'root': c['root'], 'name': c['name'], 'expected': c['tree'], 'tree': desired[c['name']]} for c in copies]
            needed = {v['sha'] for a in actions if a['tree'] != a['expected'] for v in a['tree'].values()}
            try:
                receipt = contact(endpoint, 'apply', {'actions': actions, 'blobs': {s: base64.b64encode(blobs[s]).decode() for s in needed}, 'commit': published})
                if receipt.get('status') != 'applied':
                    raise Blocked('Endpoint did not confirm application')
                for c in copies:
                    key = json.dumps([endpoint['id'], c['root'], c['name']])
                    ledger['copies'][key] = desired[c['name']]
                ledger['commit'] = published
                dump(state / 'baseline.json', ledger)
                applied.append(endpoint['id'])
            except (Blocked, OSError, subprocess.SubprocessError) as error:
                pending.append({'endpoint': endpoint['id'], 'reason': str(error)})
        if not pending:
            refresh_engine(config, desired.get('presto-toolchain-and-upgrade'), blobs)
        result = {'status': 'complete' if not pending else 'partial', 'commit': published, 'changed_skills': changed, 'applied': applied, 'pending': pending}
        dump(state / 'last-result.json', result)
        dump(run / 'result.json', result)
        return result

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--config', required=True)
    p.add_argument('command', choices=['sync', 'export', 'apply', 'status'])
    a = p.parse_args(); config = load(Path(a.config).expanduser())
    if a.command in {'export', 'apply'}:
        req = json.load(sys.stdin)
        result = endpoint_export(config, req) if a.command == 'export' else endpoint_apply(config, req)
    elif 'controller' in config:
        raw = run_command(config['controller'] + [a.command], timeout=config.get('timeout', 1800))
        result = json.loads(raw)
    elif a.command == 'status':
        result = load(state_dir(config) / 'last-result.json', {'status': 'not_initialized'})
    else:
        result = fleet(config)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result.get('status') not in {'conflict', 'partial', 'blocked'} else 2

if __name__ == '__main__':
    try:
        sys.exit(main())
    except (Blocked, OSError, ValueError, KeyError, subprocess.SubprocessError) as error:
        print(json.dumps({'status': 'blocked', 'reason': str(error)}, ensure_ascii=False))
        sys.exit(2)
