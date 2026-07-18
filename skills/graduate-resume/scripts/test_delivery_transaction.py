from __future__ import annotations

import hashlib
import errno
import inspect
import os
import re
import signal
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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


THEMES = ("保守稳妥", "现代简洁", "个性设计")
OWNER_PREFIX = "张三简历-"


def triple(stem: str, marker: str) -> dict[str, bytes]:
    return {
        f"{stem}.md": f"# {marker}\n".encode(),
        f"{stem}.typ": f"// {marker}\n".encode(),
        f"{stem}.pdf": b"%PDF-1.7\n" + marker.encode() + b"\n%%EOF\n",
    }


def snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            digest = f"symlink:{os.readlink(path)}"
        elif path.is_file():
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
        elif path.is_dir():
            digest = "directory"
        else:
            digest = "special"
        result[relative] = digest
    return result


def exact_snapshot(root: Path) -> dict[str, tuple[str, int, int, int, bytes | str | None]]:
    result: dict[str, tuple[str, int, int, int, bytes | str | None]] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        metadata = path.lstat()
        if path.is_symlink():
            kind = "symlink"
            payload: bytes | str | None = os.readlink(path)
        elif path.is_file():
            kind = "file"
            payload = path.read_bytes()
        elif path.is_dir():
            kind = "directory"
            payload = None
        else:
            kind = "special"
            payload = None
        result[relative] = (
            kind,
            metadata.st_ino,
            metadata.st_mtime_ns,
            metadata.st_mode,
            payload,
        )
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
            "王小明简历-acme-industrial-controls-engineer-现代简洁",
            "王小明简历-通用-保守稳妥",
        )
        spec = DeliverySpec(Path("delivery"), stems, THEMES, "authority", "王小明简历-")
        self.assertEqual(spec.safe_stems, stems)
        with self.assertRaisesRegex(DeliveryError, "registered theme"):
            DeliverySpec(Path("delivery"), ("王小明简历-acme-现代简洁-个性设计",), THEMES, "patch", "王小明简历-")
        with self.assertRaisesRegex(DeliveryError, "duplicate"):
            DeliverySpec(Path("delivery"), (stems[0], stems[0]), THEMES, "patch", "王小明简历-")
        for owner_prefix in ("", "Ｗang简历-", "李四简历-"):
            with self.subTest(owner_prefix=owner_prefix), self.assertRaises(DeliveryError):
                DeliverySpec(Path("delivery"), (stems[1],), THEMES, "patch", owner_prefix)


class DiscoveryFailClosedTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "delivery"
        self.stem = "张三简历-通用-保守稳妥"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def spec(self) -> DeliverySpec:
        return DeliverySpec(self.root, (self.stem,), THEMES, "patch", OWNER_PREFIX)

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

    def test_sources_and_assets_are_unknown_without_mutating_existing_state(self) -> None:
        cases = (
            "empty-directory",
            "nonempty-directory",
            "regular-file",
            "symlink",
        )
        for support_name in ("sources", "assets"):
            for case in cases:
                with self.subTest(support_name=support_name, case=case):
                    self.temporary.cleanup()
                    self.temporary = tempfile.TemporaryDirectory()
                    self.root = Path(self.temporary.name) / "delivery"
                    self.write_current()
                    history_stem = "张三简历-旧公司-旧岗位-现代简洁"
                    archived = self.root / "history" / "001" / history_stem
                    archived.mkdir(parents=True)
                    for name, payload in triple(history_stem, "archived").items():
                        (archived / name).write_bytes(payload)
                    polluted = self.root / support_name
                    if case == "empty-directory":
                        polluted.mkdir()
                    elif case == "nonempty-directory":
                        polluted.mkdir()
                        (polluted / "private.txt").write_text("private", encoding="utf-8")
                    elif case == "regular-file":
                        polluted.write_text("private", encoding="utf-8")
                    else:
                        polluted.symlink_to("outside")

                    before = exact_snapshot(self.root)
                    with self.assertRaisesRegex(
                        DeliveryError,
                        rf"unknown delivery-root entry: {support_name}",
                    ):
                        DeliverySession(self.spec()).__enter__()
                    self.assertEqual(exact_snapshot(self.root), before)

    def test_history_uses_owner_bound_grammar_and_exact_triples_not_current_membership(self) -> None:
        cases = (
            ("other-owner", "李四简历-通用-保守稳妥"),
            ("unregistered-theme", "张三简历-通用-未登记"),
            ("malformed-structure", "张三简历-单段-保守稳妥"),
            ("unknown", "张三简历-旧公司-旧岗位-现代简洁"),
            ("partial", "张三简历-旧公司-旧岗位-现代简洁"),
            ("symlink", "张三简历-旧公司-旧岗位-现代简洁"),
            ("directory", "张三简历-旧公司-旧岗位-现代简洁"),
            ("fifo", "张三简历-旧公司-旧岗位-现代简洁"),
        )
        for case, historical_stem in cases:
            with self.subTest(case=case):
                self.temporary.cleanup()
                self.temporary = tempfile.TemporaryDirectory()
                self.root = Path(self.temporary.name) / "delivery"
                self.write_current()
                archived = self.root / "history" / "001" / historical_stem
                archived.mkdir(parents=True)
                for name, payload in triple(historical_stem, "old").items():
                    (archived / name).write_bytes(payload)
                if case == "unknown":
                    (archived / "extra.txt").write_text("unknown", encoding="utf-8")
                elif case == "partial":
                    (archived / f"{historical_stem}.pdf").unlink()
                elif case in {"symlink", "directory", "fifo"}:
                    path = archived / f"{historical_stem}.pdf"
                    path.unlink()
                    if case == "symlink":
                        path.symlink_to("outside")
                    elif case == "directory":
                        path.mkdir()
                    else:
                        os.mkfifo(path)
                self.assert_open_fails_unchanged()

        source = inspect.getsource(DeliverySession._inspect_history)
        self.assertIn("self.spec.owner_prefix", source)
        self.assertNotIn("stem in self.spec.safe_stems", source)


class PublicationTransactionTests(unittest.TestCase):
    def test_patch_requires_the_reviewed_digest_and_rejects_stale_current(self) -> None:
        patch_spec = self.spec("patch")
        with DeliverySession(patch_spec) as session:
            self.stage(session, (self.stems[0],), "v1")
            delta = session.preflight()
            payload = session.approval_payload(delta, session._candidate, session._current)
            self.assertEqual(session.approval_digest(payload), delta.approval_digest)
            self.assertEqual(payload["mode"], "patch")
            self.assertEqual(payload["canonical_input_hash"], "0" * 64)
            self.assertEqual(
                set(payload["delivery_root"]), {"path", "st_dev", "st_ino"},
            )
            self.assertTrue(payload["candidate"][self.stems[0]][f"{self.stems[0]}.md"])
            with self.assertRaisesRegex(DeliveryError, "approval"):
                session.publish()
            self.assertFalse(tuple(self.root.glob("*.md")))
            self.assertFalse((self.root / "history").exists())
            self.assertEqual(
                session.publish(approval_digest=delta.approval_digest),
                "first",
            )

        with DeliverySession(patch_spec) as session:
            self.stage(session, (self.stems[0],), "v2")
            delta = session.preflight()
            (self.root / f"{self.stems[0]}.md").write_bytes(b"external-change")
            changed = snapshot(self.root)
            with self.assertRaisesRegex(DeliveryError, "approval"):
                session.publish(approval_digest=delta.approval_digest)
            self.assertEqual(snapshot(self.root), changed)

    def test_removed_target_history_reopens_under_reduced_authority_and_then_noops(self) -> None:
        owner_prefix = "张三简历-"
        themes = ("保守稳妥", "现代简洁", "个性设计")
        surviving = (
            "张三简历-通用-保守稳妥",
            "张三简历-通用-现代简洁",
            "张三简历-通用-个性设计",
        )
        removed = "张三简历-某公司-设备工程师-个性设计"
        initial = (*surviving, removed)

        def specification(stems: tuple[str, ...]) -> DeliverySpec:
            return DeliverySpec(
                self.root, stems, themes, "authority", owner_prefix=owner_prefix,
            )

        with DeliverySession(specification(initial)) as session:
            self.stage(session, initial, "v1")
            delta = session.preflight()
            self.assertEqual(session.publish(approval_digest=delta.approval_digest), "first")
        with DeliverySession(specification(initial)) as session:
            self.stage(session, surviving, "v1")
            delta = session.preflight()
            self.assertEqual(delta.removed, (removed,))
            self.assertEqual(session.publish(approval_digest=delta.approval_digest), "changed")

        before = {
            name: (
                (self.root / name).stat().st_ino,
                (self.root / name).stat().st_mtime_ns,
                (self.root / name).read_bytes(),
            )
            for stem in surviving
            for name in triple(stem, "v1")
        }
        history_before = snapshot(self.root / "history")
        with DeliverySession(specification(surviving)) as session:
            self.stage(session, surviving, "v1")
            delta = session.preflight()
            self.assertFalse(delta.changed)
            self.assertEqual(session.publish(approval_digest=delta.approval_digest), "identical")
        self.assertEqual(snapshot(self.root / "history"), history_before)
        self.assertEqual({
            name: (
                (self.root / name).stat().st_ino,
                (self.root / name).stat().st_mtime_ns,
                (self.root / name).read_bytes(),
            )
            for name in before
        }, before)

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "delivery"
        self.stems = (
            "张三简历-通用-保守稳妥",
            "张三简历-通用-现代简洁",
            "张三简历-通用-个性设计",
        )

    def tearDown(self) -> None:
        os.environ.pop(FAULT_ENV, None)
        self.temporary.cleanup()

    def spec(self, mode: str = "authority") -> DeliverySpec:
        return DeliverySpec(self.root, self.stems, THEMES, mode, OWNER_PREFIX)

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
            self.assertEqual(session.publish(approval_digest=delta.approval_digest), "changed")
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

    def test_preflight_snapshot_and_held_root_identity_block_toctou(self) -> None:
        self.assertEqual(self.publish_authority(self.stems, "v1"), "first")
        with DeliverySession(self.spec()) as session:
            self.stage(session, self.stems, "v2")
            delta = session.preflight()
            (self.root / f"{self.stems[0]}.md").write_text("externally changed\n", encoding="utf-8")
            changed = snapshot(self.root)
            with self.assertRaisesRegex(DeliveryError, "approval"):
                session.publish(approval_digest=delta.approval_digest)
            self.assertEqual(snapshot(self.root), changed)

        displaced = self.root.with_name("displaced")
        with DeliverySession(self.spec()) as session:
            self.stage(session, self.stems, "v3")
            self.root.rename(displaced)
            self.root.mkdir()
            replacement = snapshot(self.root)
            with self.assertRaisesRegex(DeliveryError, "root changed"):
                session.preflight()
            self.assertEqual(snapshot(self.root), replacement)

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


class CleanupFailureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "delivery"
        self.stem = "张三简历-通用-保守稳妥"

    def tearDown(self) -> None:
        os.environ.pop(FAULT_ENV, None)
        self.temporary.cleanup()

    def spec(self) -> DeliverySpec:
        return DeliverySpec(self.root, (self.stem,), THEMES, "authority", OWNER_PREFIX)

    def stage(self, session: DeliverySession, marker: str) -> None:
        for name, payload in triple(self.stem, marker).items():
            session.candidate_path(name).write_bytes(payload)

    @staticmethod
    def syscall_failure(
        function: object,
        *,
        expected_name: str | None = None,
        expected_dir_fd: int | None = None,
        expected_descriptor: int | None = None,
    ) -> tuple[object, list[tuple[object, int | None]]]:
        calls: list[tuple[object, int | None]] = []

        def failing(*args: object, **kwargs: object) -> object:
            name = args[0]
            directory_fd = kwargs.get("dir_fd")
            calls.append((name, directory_fd if isinstance(directory_fd, int) else None))
            if expected_descriptor is not None and name == expected_descriptor:
                raise OSError(errno.EIO, "injected cleanup failure")
            if expected_name == name and expected_dir_fd == directory_fd:
                raise OSError(errno.EIO, "injected cleanup failure")
            return function(*args, **kwargs)  # type: ignore[operator]

        return failing, calls

    def prepared_session(self) -> DeliverySession:
        session = DeliverySession(self.spec()).__enter__()
        self.stage(session, "candidate")
        rollback_name = f"{self.stem}.md"
        assert session.rollback_fd is not None
        session._write_bytes(rollback_name, b"rollback", directory_fd=session.rollback_fd)
        session._old_bytes = {rollback_name: b"rollback"}
        return session

    def test_each_cleanup_syscall_failure_is_bounded_and_cleanup_continues(self) -> None:
        cases = (
            ("unlink", "candidate-file", "candidate"),
            ("unlink", "rollback-file", "rollback"),
            ("close", "candidate-fd", "candidate"),
            ("close", "rollback-fd", "rollback"),
            ("close", "evidence-fd", "evidence"),
            ("rmdir", "candidate-dir", "candidate"),
            ("rmdir", "rollback-dir", "rollback"),
            ("rmdir", "evidence-dir", "evidence"),
            ("close", "run-fd", "run"),
            ("rmdir", "run-dir", "run"),
            ("unlink", "lock", ".lock"),
            ("close", "work-fd", ".work"),
            ("rmdir", "work-dir", ".work"),
            ("close", "root-fd", "."),
        )
        for operation, case, owned_name in cases:
            with self.subTest(case=case):
                self.temporary.cleanup()
                self.temporary = tempfile.TemporaryDirectory()
                self.root = Path(self.temporary.name) / "delivery"
                session = self.prepared_session()
                original = getattr(os, operation)
                expected_name: str | None = None
                expected_dir_fd: int | None = None
                expected_descriptor: int | None = None
                if case == "candidate-file":
                    expected_name = f"{self.stem}.md"
                    expected_dir_fd = session.candidate_fd
                elif case == "rollback-file":
                    expected_name = f"{self.stem}.md"
                    expected_dir_fd = session.rollback_fd
                elif case == "candidate-dir":
                    expected_name, expected_dir_fd = "candidate", session.run_fd
                elif case == "rollback-dir":
                    expected_name, expected_dir_fd = "rollback", session.run_fd
                elif case == "evidence-dir":
                    expected_name, expected_dir_fd = "evidence", session.run_fd
                elif case == "run-dir":
                    expected_name, expected_dir_fd = session.run_name, session.work_fd
                elif case == "lock":
                    expected_name, expected_dir_fd = ".lock", session.work_fd
                elif case == "work-dir":
                    expected_name, expected_dir_fd = ".work", session.root_fd
                else:
                    attribute = case.replace("-fd", "_fd")
                    expected_descriptor = getattr(session, attribute)
                failing, calls = self.syscall_failure(
                    original,
                    expected_name=expected_name,
                    expected_dir_fd=expected_dir_fd,
                    expected_descriptor=expected_descriptor,
                )
                with mock.patch.object(os, operation, side_effect=failing):
                    with self.assertRaisesRegex(
                        DeliveryError,
                        rf"cleanup failed: .*{operation} {re.escape(owned_name)}(?:/[^;]+)? errno={errno.EIO}",
                    ):
                        session.close()
                self.assertGreater(len(calls), 1)
                session.close()

    def test_successful_publish_with_cleanup_failure_keeps_current_and_stale_work(self) -> None:
        session = DeliverySession(self.spec()).__enter__()
        self.stage(session, "published")
        delta = session.preflight()
        self.assertEqual(
            session.publish(approval_digest=delta.approval_digest),
            "first",
        )
        original_unlink = os.unlink
        with self.assertRaisesRegex(DeliveryError, r"cleanup failed: .*unlink \.lock errno=5"):
            with mock.patch.object(os, "unlink") as unlink_spy:
                def fail_lock(name: str, *args: object, **kwargs: object) -> None:
                    if name == ".lock":
                        raise OSError(errno.EIO, "injected cleanup failure")
                    original_unlink(name, *args, **kwargs)

                unlink_spy.side_effect = fail_lock
                session.__exit__(None, None, None)
        for name, payload in triple(self.stem, "published").items():
            self.assertEqual((self.root / name).read_bytes(), payload)
        self.assertTrue((self.root / ".work" / ".lock").exists())
        with self.assertRaises(DeliveryError):
            DeliverySession(self.spec()).__enter__()

    def test_publication_and_cleanup_failure_chain_original_after_rollback(self) -> None:
        with DeliverySession(self.spec()) as initial:
            self.stage(initial, "baseline")
            delta = initial.preflight()
            initial.publish(approval_digest=delta.approval_digest)
        baseline = {
            name: (self.root / name).read_bytes()
            for name in triple(self.stem, "baseline")
        }
        session = DeliverySession(self.spec()).__enter__()
        self.stage(session, "replacement")
        delta = session.preflight()
        original_unlink = os.unlink
        os.environ[FAULT_ENV] = "after_publish_file_1"
        with mock.patch.object(os, "unlink") as unlink_spy:
            def fail_lock(name: str, *args: object, **kwargs: object) -> None:
                if name == ".lock":
                    raise OSError(errno.EIO, "injected cleanup failure")
                original_unlink(name, *args, **kwargs)

            unlink_spy.side_effect = fail_lock
            with self.assertRaisesRegex(DeliveryError, r"cleanup failed") as raised:
                try:
                    session.publish(approval_digest=delta.approval_digest)
                except BaseException as original:
                    session.__exit__(type(original), original, original.__traceback__)
        self.assertIsInstance(raised.exception.__cause__, DeliveryError)
        self.assertIn("injected delivery fault", str(raised.exception.__cause__))
        self.assertEqual(
            {name: (self.root / name).read_bytes() for name in baseline},
            baseline,
        )
        self.assertFalse((self.root / "history").exists())

if __name__ == "__main__":
    unittest.main()
