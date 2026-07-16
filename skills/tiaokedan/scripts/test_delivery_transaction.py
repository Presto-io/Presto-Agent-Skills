from __future__ import annotations

import hashlib
import os
import signal
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from delivery_transaction import (
    FAULT_ENV,
    FAULT_NAMES,
    DeliveryError,
    DeliverySession,
    DeliverySpec,
    derive_delivery_spec,
)


def snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = f"symlink:{os.readlink(path)}"
        elif path.is_file():
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif path.is_dir():
            result[relative] = "directory"
    return result


class DeliverySpecTests(unittest.TestCase):
    def test_optional_pdf_changes_exact_set_and_path_mismatch_is_rejected(self) -> None:
        root = Path("build") / "tiaokedan"
        pair = derive_delivery_spec(root / "notice.typ", None)
        triple = derive_delivery_spec(root / "notice.typ", root / "notice.pdf")
        self.assertEqual(pair.current_names, ("notice.md", "notice.typ"))
        self.assertEqual(triple.current_names, ("notice.md", "notice.typ", "notice.pdf"))
        with self.assertRaises(DeliveryError):
            derive_delivery_spec(root / "notice.typ", root / "other.pdf")
        with self.assertRaises(DeliveryError):
            derive_delivery_spec(root / "notice.typ", root.parent / "notice.pdf")
        with self.assertRaises(DeliveryError):
            derive_delivery_spec(root / "../escape.typ", None)


class DeliverySessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "delivery"

    def tearDown(self) -> None:
        os.environ.pop(FAULT_ENV, None)
        self.temporary.cleanup()

    def spec(self, *, pdf: bool = True) -> DeliverySpec:
        return derive_delivery_spec(self.root / "tiaokedan.typ", self.root / "tiaokedan.pdf" if pdf else None)

    @staticmethod
    def candidate(session: DeliverySession, marker: str) -> None:
        for name in session.spec.current_names:
            if name.endswith(".md"):
                payload = f"# {marker}\n".encode()
            elif name.endswith(".typ"):
                payload = f"// {marker}\n".encode()
            else:
                payload = b"%PDF-1.7\n" + marker.encode() + b"\n%%EOF\n"
            session.candidate_path(name).write_bytes(payload)

    def publish(self, marker: str, *, pdf: bool = True) -> str:
        with DeliverySession(self.spec(pdf=pdf)) as session:
            self.candidate(session, marker)
            return session.publish()

    def test_first_identical_and_optional_set_change(self) -> None:
        self.assertEqual(self.publish("v1", pdf=False), "first")
        before = {name: (self.root / name).stat() for name in self.spec(pdf=False).current_names}
        self.assertEqual(self.publish("v1", pdf=False), "identical")
        after = {name: (self.root / name).stat() for name in self.spec(pdf=False).current_names}
        self.assertFalse((self.root / "history").exists())
        for name in before:
            self.assertEqual((before[name].st_ino, before[name].st_mtime_ns), (after[name].st_ino, after[name].st_mtime_ns))

        old = {name: (self.root / name).read_bytes() for name in self.spec(pdf=False).current_names}
        self.assertEqual(self.publish("v1", pdf=True), "changed")
        self.assertEqual({path.name for path in (self.root / "history" / "001").iterdir()}, set(old))
        self.assertEqual({name: (self.root / "history" / "001" / name).read_bytes() for name in old}, old)
        self.assertTrue((self.root / "tiaokedan.pdf").is_file())

    def test_full_set_equality_and_history_gap_guard(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        for sequence in ("001", "003"):
            history = self.root / "history" / sequence
            history.mkdir(parents=True)
            for name in self.spec().current_names:
                (history / name).write_bytes(f"historic-{sequence}-{name}".encode())
        old = {name: (self.root / name).read_bytes() for name in self.spec().current_names}

        with DeliverySession(self.spec()) as session:
            self.candidate(session, "v1")
            session.candidate_path("tiaokedan.pdf").write_bytes(b"%PDF-1.7\nchanged-only-pdf\n")
            self.assertEqual(session.publish(), "changed")

        self.assertEqual({path.name for path in (self.root / "history").iterdir()}, {"001", "003", "004"})
        self.assertEqual({name: (self.root / "history" / "004" / name).read_bytes() for name in old}, old)

    def test_every_fault_restores_current_history_and_sources(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        sources = self.root / "sources"
        sources.mkdir()
        (sources / "facts.txt").write_text("keep", encoding="utf-8")
        history = self.root / "history" / "003"
        history.mkdir(parents=True)
        for name in self.spec().current_names:
            (history / name).write_bytes(f"history-{name}".encode())
        before = snapshot(self.root)

        for fault in FAULT_NAMES:
            with self.subTest(fault=fault):
                os.environ[FAULT_ENV] = fault
                with self.assertRaises(DeliveryError):
                    self.publish(f"failed-{fault}")
                os.environ.pop(FAULT_ENV, None)
                self.assertEqual(snapshot(self.root), before)

    def test_int_and_term_restore_after_first_replace(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        before = snapshot(self.root)
        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signum=signum):
                with DeliverySession(self.spec()) as session:
                    self.candidate(session, f"signal-{signum}")
                    original_fault = session._fault

                    def interrupt(name: str) -> None:
                        if name == "after_publish_file_1":
                            os.kill(os.getpid(), signum)
                        original_fault(name)

                    session._fault = interrupt
                    with self.assertRaises(DeliveryError):
                        session.publish()
                self.assertEqual(snapshot(self.root), before)

    def test_unknown_legacy_symlink_partial_lock_and_stale_work_fail_closed(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        baseline = snapshot(self.root)
        for name, kind in (("unknown.txt", "file"), (".tiaokedan", "directory"), ("media", "directory"), ("bad", "symlink")):
            with self.subTest(name=name):
                path = self.root / name
                if kind == "file":
                    path.write_text("unknown", encoding="utf-8")
                elif kind == "directory":
                    path.mkdir()
                else:
                    path.symlink_to("outside")
                before = snapshot(self.root)
                with self.assertRaises(DeliveryError):
                    self.publish("v2")
                self.assertEqual(snapshot(self.root), before)
                path.unlink() if path.is_symlink() or path.is_file() else path.rmdir()
                self.assertEqual(snapshot(self.root), baseline)

        (self.root / "tiaokedan.pdf").unlink()
        partial = snapshot(self.root)
        with self.assertRaises(DeliveryError):
            self.publish("v2")
        self.assertEqual(snapshot(self.root), partial)

    def test_lock_conflict_and_unrelated_stale_work_are_preserved(self) -> None:
        with DeliverySession(self.spec()) as first:
            self.candidate(first, "v1")
            with self.assertRaises(DeliveryError):
                DeliverySession(self.spec()).__enter__()
            self.assertEqual(first.publish(), "first")

        stale = self.root / ".work" / "stale-run"
        stale.mkdir(parents=True)
        (stale / "evidence.txt").write_text("keep", encoding="utf-8")
        before = snapshot(self.root)
        with self.assertRaises(DeliveryError):
            DeliverySession(self.spec()).__enter__()
        self.assertEqual(snapshot(self.root), before)


if __name__ == "__main__":
    unittest.main()
