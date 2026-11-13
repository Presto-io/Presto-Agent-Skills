"""Isolated installer tests; no user DSH configuration or skill roots are touched."""
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('dsh_install', ROOT / 'scripts/install-dsh-skills.py')
installer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(installer)


class InstallTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / 'source' / 'sample-skill'
        (self.source / 'references').mkdir(parents=True)
        (self.source / 'SKILL.md').write_text('---\nname: sample-skill\ndescription: test\n---\n# Test\n')
        (self.source / 'references/rule.md').write_text('support')
        self.dest = self.root / 'dest'
        self.dest.mkdir()
        self.target = self.dest / self.source.name
        self.expected = installer.manifest(self.source)

    def test_complete_copy_and_exact_noop(self):
        installer.metadata(self.source)
        installer.install_one(self.source, self.target, self.expected, False)
        self.assertEqual(installer.manifest(self.target), self.expected)
        before = (self.target / 'SKILL.md').stat().st_mtime_ns
        result = installer.install_one(self.source, self.target, self.expected, False)
        self.assertEqual(result['action'], 'unchanged')
        self.assertEqual((self.target / 'SKILL.md').stat().st_mtime_ns, before)
        self.assertFalse((self.dest / '.presto-backups').exists())

    def test_changed_refused_then_backup_preserved(self):
        installer.install_one(self.source, self.target, self.expected, False)
        (self.target / 'references/rule.md').write_text('old local edit')
        old = installer.manifest(self.target)
        with self.assertRaises(ValueError):
            installer.install_one(self.source, self.target, self.expected, False)
        self.assertEqual(installer.manifest(self.target), old)
        result = installer.install_one(self.source, self.target, self.expected, True)
        self.assertEqual(installer.manifest(Path(result['backup'])), old)
        self.assertEqual(installer.manifest(self.target), self.expected)

    def test_failure_after_backup_restores_original(self):
        installer.install_one(self.source, self.target, self.expected, False)
        (self.target / 'references/rule.md').write_text('old local edit')
        old = installer.manifest(self.target)
        replace = installer.os.replace
        def fail_candidate(source, target):
            if Path(source).parent.name.startswith('.presto-install-') and Path(source).name == 'sample-skill':
                raise OSError('injected publish failure')
            return replace(source, target)
        with patch.object(installer.os, 'replace', fail_candidate):
            with self.assertRaises(OSError):
                installer.install_one(self.source, self.target, self.expected, True)
        self.assertEqual(installer.manifest(self.target), old)
        self.assertFalse(list(self.dest.glob('.presto-install-*')))

    def test_symlink_and_source_drift_refused(self):
        self.target.symlink_to(self.source, target_is_directory=True)
        with self.assertRaises(ValueError):
            installer.install_one(self.source, self.target, self.expected, True)
        self.target.unlink()
        (self.source / 'references/rule.md').write_text('changed')
        with self.assertRaises(ValueError):
            installer.install_one(self.source, self.target, self.expected, False)
        self.assertFalse(self.target.exists())

    def test_invalid_invocation_refused(self):
        (self.source / 'SKILL.md').write_text('---\nname: sample-skill\ndescription: test\nuserInvocable: true\n---\n')
        with self.assertRaises(ValueError):
            installer.metadata(self.source)


if __name__ == '__main__':
    unittest.main()
