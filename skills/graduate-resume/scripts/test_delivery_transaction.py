from __future__ import annotations

import hashlib
import os
import signal
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from graduate_resume_delivery import (
    BundleDelta,
    FAULT_ENV,
    FAULT_NAMES,
    DeliveryError,
    DeliverySession,
    DeliverySpec,
    classify_bundle_delta,
)


THEMES = ("conservative", "modern", "expressive")


def triple(stem: str, marker: str) -> dict[str, bytes]:
    return {
        f"{stem}.md": f"# {marker}\n".encode(),
        f"{stem}.typ": f"// {marker}\n".encode(),
        f"{stem}.pdf": b"%PDF-1.7\n" + marker.encode() + b"\n%%EOF\n",
    }


def snapshot(root: Path) -> dict[str, tuple[str, int, int]]:
    result: dict[str, tuple[str, int, int]] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        metadata = path.lstat()
        if path.is_symlink():
            digest = f"symlink:{os.readlink(path)}"
        elif path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        elif path.is_dir():
            digest = "directory"
        else:
            digest = "special"
        result[relative] = (digest, metadata.st_ino, metadata.st_mtime_ns)
    return result


class BundleDeltaTests(unittest.TestCase):
    def test_classifies_complete_triples_at_stem_granularity(self) -> None:
        unchanged = "resume-generic-conservative"
        updated = "resume-generic-modern"
        removed = "resume-old-expressive"
        added = "resume-new-expressive"
        current = {
            unchanged: triple(unchanged, "same"),
            updated: triple(updated, "old"),
            removed: triple(removed, "old"),
        }
        candidate = {
            unchanged: triple(unchanged, "same"),
            updated: triple(updated, "old"),
            added: triple(added, "new"),
        }
        candidate[updated][f"{updated}.pdf"] = b"%PDF-1.7\nchanged\n%%EOF\n"

        delta = classify_bundle_delta(candidate, current, mode="authority")

        self.assertEqual(delta.unchanged, (unchanged,))
        self.assertEqual(delta.updated, (updated,))
        self.assertEqual(delta.added, (added,))
        self.assertEqual(delta.removed, (removed,))
        self.assertTrue(delta.approval_digest)

    def test_patch_rejects_removed_and_incomplete_triples(self) -> None:
        first = "resume-generic-conservative"
        second = "resume-generic-modern"
        current = {first: triple(first, "one"), second: triple(second, "two")}
        with self.assertRaisesRegex(DeliveryError, "patch"):
            classify_bundle_delta({first: triple(first, "new")}, current, mode="patch")

        partial = triple(first, "one")
        partial.pop(f"{first}.pdf")
        with self.assertRaisesRegex(DeliveryError, "complete triple"):
            classify_bundle_delta({first: partial}, {}, mode="patch")

    def test_spec_consumes_explicit_stems_without_splitting_identity(self) -> None:
        stems = (
            "王小明-acme-industrial-controls-engineer-modern",
            "王小明-generic-conservative",
        )
        spec = DeliverySpec(Path("delivery"), stems, THEMES, "authority")
        self.assertEqual(spec.safe_stems, stems)
        with self.assertRaisesRegex(DeliveryError, "registered theme"):
            DeliverySpec(Path("delivery"), ("王小明-acme-modern-expressive",), THEMES, "patch")
        with self.assertRaisesRegex(DeliveryError, "duplicate"):
            DeliverySpec(Path("delivery"), (stems[0], stems[0]), THEMES, "patch")


class DiscoveryFailClosedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "delivery"
        self.stem = "resume-generic-conservative"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def spec(self) -> DeliverySpec:
        return DeliverySpec(self.root, (self.stem,), THEMES, "patch")

    def write_current(self) -> None:
        self.root.mkdir(parents=True, exist_ok=True)
        for name, payload in triple(self.stem, "old").items():
            (self.root / name).write_bytes(payload)

    def assert_open_fails_unchanged(self) -> None:
        before = snapshot(self.root)
        with self.assertRaises(DeliveryError):
            DeliverySession(self.spec()).__enter__()
        self.assertEqual(snapshot(self.root), before)

    def test_unknown_partial_symlink_directory_fifo_and_stale_work_fail(self) -> None:
        cases = ("unknown", "partial", "symlink", "directory", "fifo", "stale-work")
        for case in cases:
            with self.subTest(case=case):
                self.temporary.cleanup()
                self.temporary = tempfile.TemporaryDirectory()
                self.root = Path(self.temporary.name) / "delivery"
                self.write_current()
                if case == "unknown":
                    (self.root / "notes.txt").write_text("private", encoding="utf-8")
                elif case == "partial":
                    (self.root / f"{self.stem}.pdf").unlink()
                elif case == "symlink":
                    path = self.root / f"{self.stem}.pdf"
                    path.unlink()
                    path.symlink_to("outside")
                elif case == "directory":
                    path = self.root / f"{self.stem}.pdf"
                    path.unlink()
                    path.mkdir()
                elif case == "fifo":
                    path = self.root / f"{self.stem}.pdf"
                    path.unlink()
                    os.mkfifo(path)
                else:
                    stale = self.root / ".work" / "stale-run"
                    stale.mkdir(parents=True)
                    (stale / "evidence.json").write_text("{}", encoding="utf-8")
                self.assert_open_fails_unchanged()

    def test_support_directory_symlink_fails(self) -> None:
        self.write_current()
        (self.root / "history").symlink_to("outside")
        self.assert_open_fails_unchanged()


class PublicationTransactionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "delivery"
        self.stems = (
            "resume-generic-conservative",
            "resume-generic-modern",
            "resume-generic-expressive",
        )

    def tearDown(self) -> None:
        os.environ.pop(FAULT_ENV, None)
        self.temporary.cleanup()

    def spec(self, mode: str = "authority") -> DeliverySpec:
        return DeliverySpec(self.root, self.stems, THEMES, mode)

    @staticmethod
    def stage(session: DeliverySession, stems: tuple[str, ...], marker: str) -> None:
        for stem in stems:
            for name, payload in triple(stem, marker).items():
                session.candidate_path(name).write_bytes(payload)

    def publish_authority(self, stems: tuple[str, ...], marker: str) -> str:
        with DeliverySession(self.spec()) as session:
            self.stage(session, stems, marker)
            delta = session.preflight()
            return session.publish(approval_digest=delta.approval_digest)

    def test_identical_does_not_create_history_or_touch_inode_mtime(self) -> None:
        self.assertEqual(self.publish_authority(self.stems, "v1"), "first")
        before = {
            name: (path.stat().st_ino, path.stat().st_mtime_ns, path.read_bytes())
            for stem in self.stems
            for name in triple(stem, "v1")
            if (path := self.root / name)
        }

        self.assertEqual(self.publish_authority(self.stems, "v1"), "identical")

        self.assertFalse((self.root / "history").exists())
        for name, expected in before.items():
            path = self.root / name
            self.assertEqual((path.stat().st_ino, path.stat().st_mtime_ns, path.read_bytes()), expected)

    def test_updated_and_removed_archive_only_old_complete_triples(self) -> None:
        self.assertEqual(self.publish_authority(self.stems, "v1"), "first")
        unchanged, updated, removed = self.stems
        old = {
            stem: {name: (self.root / name).read_bytes() for name in triple(stem, "v1")}
            for stem in self.stems
        }
        before_unchanged = {
            name: ((self.root / name).stat().st_ino, (self.root / name).stat().st_mtime_ns)
            for name in triple(unchanged, "v1")
        }
        with DeliverySession(self.spec()) as session:
            self.stage(session, (unchanged,), "v1")
            self.stage(session, (updated,), "v2")
            delta = session.preflight()
            self.assertEqual(delta.updated, (updated,))
            self.assertEqual(delta.removed, (removed,))
            self.assertEqual(session.publish(approval_digest=delta.approval_digest), "changed")

        sequence = self.root / "history" / "001"
        self.assertEqual({path.name for path in sequence.iterdir()}, {updated, removed})
        for stem in (updated, removed):
            archived = sequence / stem
            self.assertEqual({path.name for path in archived.iterdir()}, set(triple(stem, "v1")))
            self.assertEqual({name: (archived / name).read_bytes() for name in old[stem]}, old[stem])
        self.assertFalse((sequence / unchanged).exists())
        self.assertFalse(any((self.root / name).exists() for name in triple(removed, "v1")))
        for name, expected in before_unchanged.items():
            path = self.root / name
            self.assertEqual((path.stat().st_ino, path.stat().st_mtime_ns), expected)

    def test_authority_requires_unchanged_approval_and_patch_preserves_other_stems(self) -> None:
        self.assertEqual(self.publish_authority(self.stems, "v1"), "first")
        with DeliverySession(self.spec()) as session:
            self.stage(session, self.stems[:2], "v2")
            delta = session.preflight()
            with self.assertRaisesRegex(DeliveryError, "approval"):
                session.publish()
            with self.assertRaisesRegex(DeliveryError, "approval"):
                session.publish(approval_digest="0" * 64)

        untouched = self.stems[1:]
        before = {name: (self.root / name).read_bytes() for stem in untouched for name in triple(stem, "v1")}
        with DeliverySession(self.spec("patch")) as session:
            self.stage(session, (self.stems[0],), "patch")
            delta = session.preflight()
            self.assertFalse(delta.removed)
            self.assertEqual(session.publish(), "changed")
        for name, payload in before.items():
            self.assertEqual((self.root / name).read_bytes(), payload)

    def test_candidate_validation_failure_never_changes_current_or_history(self) -> None:
        self.assertEqual(self.publish_authority(self.stems, "v1"), "first")
        before = snapshot(self.root)
        with DeliverySession(self.spec()) as session:
            self.stage(session, self.stems, "v2")
            session.candidate_path(f"{self.stems[0]}.pdf").write_bytes(b"")
            with self.assertRaises(DeliveryError):
                session.preflight()
        self.assertEqual(snapshot(self.root), before)

    def test_every_fault_and_handled_signal_restore_entire_current_set(self) -> None:
        self.assertEqual(self.publish_authority(self.stems, "v1"), "first")
        baseline = snapshot(self.root)
        for fault in FAULT_NAMES:
            with self.subTest(fault=fault):
                os.environ[FAULT_ENV] = fault
                with self.assertRaises(DeliveryError):
                    self.publish_authority(self.stems[:2], f"failed-{fault}")
                os.environ.pop(FAULT_ENV, None)
                self.assertEqual(snapshot(self.root), baseline)

        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signum=signum):
                with DeliverySession(self.spec()) as session:
                    self.stage(session, self.stems[:2], f"signal-{signum}")
                    delta = session.preflight()
                    original_fault = session._fault

                    def interrupt(name: str) -> None:
                        if name == "after_publish_file_1":
                            os.kill(os.getpid(), signum)
                        original_fault(name)

                    session._fault = interrupt
                    with self.assertRaises(DeliveryError):
                        session.publish(approval_digest=delta.approval_digest)
                self.assertEqual(snapshot(self.root), baseline)


if __name__ == "__main__":
    unittest.main()
