#!/usr/bin/env python3
"""Check or install whole canonical skill folders into an explicit DSH skill root.

Requires Python 3 + PyYAML. Defaults to read-only planning. Does not configure DSH.
Replacement is per skill, not an all-skills atomic transaction.
"""
import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path

import yaml

NAME = re.compile(r'^[a-z0-9]+(?:-[a-z0-9]+)*$')
ROOT = Path(__file__).resolve().parent.parent / 'skills'


def real_path(path):
    """Reject existing symlink/special/non-directory ancestors without following them."""
    for part in [*reversed(path.parents), path]:
        try:
            mode = part.lstat().st_mode
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
            raise ValueError(f'Not a real directory: {part}')


def manifest(root):
    real_path(root)
    result = {}
    for path in sorted(root.rglob('*')):
        mode = path.lstat().st_mode
        rel = path.relative_to(root).as_posix()
        if stat.S_ISDIR(mode):
            result[rel + '/'] = 'directory'
        elif stat.S_ISREG(mode):
            result[rel] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            raise ValueError(f'Symlink or special file refused: {path}')
    return result


def metadata(folder):
    text = (folder / 'SKILL.md').read_text(encoding='utf-8')
    pieces = text.split('---', 2)
    if not text.startswith('---\n') or len(pieces) != 3:
        raise ValueError(f'Missing YAML frontmatter: {folder}')
    data = yaml.safe_load(pieces[1])
    if not isinstance(data, dict) or data.get('name') != folder.name or not NAME.fullmatch(folder.name):
        raise ValueError(f'Invalid or mismatched skill name: {folder}')
    if not isinstance(data.get('description'), str) or not data['description'].strip():
        raise ValueError(f'Missing description: {folder}')
    for key in ['modelInvocable', 'disableModelInvocation', 'userInvocable']:
        if key in data:
            raise ValueError(f'DSH rejects legacy invocation key {key}: {folder}')
    for key in ['disable-model-invocation', 'user-invocable']:
        if key in data and not (isinstance(data[key], bool) or str(data[key]).lower() in
                                ['true', 'false', 'yes', 'no', 'on', 'off', '1', '0']):
            raise ValueError(f'Invalid DSH invocation flag {key}: {folder}')
    return data


def install_one(source, target, expected, replace):
    # Recheck just before mutation; existing target content is never merged.
    real_path(target.parent)
    if manifest(source) != expected:
        raise ValueError(f'Source changed during installation: {source}')
    if target.exists() or target.is_symlink():
        current = manifest(target)
        if current == expected:
            return {'skill': source.name, 'action': 'unchanged'}
        if not replace:
            raise ValueError(f'Target differs; use --replace to retain backup and replace: {target}')
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix='.presto-install-', dir=target.parent))
    backup = None
    published = False
    try:
        candidate = stage / source.name
        shutil.copytree(source, candidate)
        if manifest(candidate) != expected:
            raise ValueError(f'Copy verification failed: {source.name}')
        if target.exists():
            # Backup lives outside a valid skill bundle and is never auto-deleted.
            backups = target.parent / '.presto-backups'
            real_path(backups)
            backups.mkdir(exist_ok=True)
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
            backup = backups / f'{source.name}-{stamp}-{uuid.uuid4().hex[:8]}'
            os.replace(target, backup)
        os.replace(candidate, target)
        published = True
        if manifest(target) != expected:
            raise ValueError(f'Installed verification failed: {target}')
        return {'skill': source.name, 'action': 'installed',
                'backup': str(backup) if backup else None, 'entries': len(expected)}
    except BaseException:
        if published:
            # Keep the failed candidate inside our own staging tree until cleanup.
            os.replace(target, stage / 'failed')
        if backup is not None and backup.exists():
            os.replace(backup, target)
        raise
    finally:
        shutil.rmtree(stage)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--skill', action='append', help='Repeat to select exact skill names')
    group.add_argument('--all', action='store_true')
    parser.add_argument('--dest', type=Path, required=True, help='Absolute DSH skill root')
    parser.add_argument('--install', action='store_true', help='Apply checked copies; otherwise read-only')
    parser.add_argument('--replace', action='store_true', help='Back up differing targets before replacement')
    args = parser.parse_args()
    if not args.dest.is_absolute() or '..' in args.dest.parts:
        parser.error('--dest must be absolute without parent traversal')
    try:
        real_path(args.dest)
        names = sorted(p.name for p in ROOT.iterdir() if p.is_dir() and (p / 'SKILL.md').is_file()) if args.all else sorted(set(args.skill))
        plan = []
        for name in names:
            if not NAME.fullmatch(name):
                raise ValueError(f'Invalid skill name: {name}')
            source, target = ROOT / name, args.dest / name
            if target.resolve() == source.resolve() or ROOT.resolve() in target.resolve().parents:
                raise ValueError('Destination cannot be the canonical source tree')
            expected = manifest(source)
            metadata(source)
            current = manifest(target) if target.exists() or target.is_symlink() else None
            action = 'unchanged' if current == expected else 'replace' if current is not None else 'install'
            if action == 'replace' and not args.replace:
                raise ValueError(f'Target differs; use --replace for backup-first replacement: {target}')
            plan.append((source, target, expected, action))
        results = []
        for source, target, expected, action in plan:
            results.append(install_one(source, target, expected, args.replace) if args.install else
                           {'skill': source.name, 'action': action, 'entries': len(expected)})
        print(json.dumps({'mode': 'install' if args.install else 'check', 'destination': str(args.dest),
                          'results': results, 'runtime_discovery_verified': False}, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, yaml.YAMLError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
