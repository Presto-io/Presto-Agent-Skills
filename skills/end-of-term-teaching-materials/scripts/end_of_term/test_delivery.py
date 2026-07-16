from __future__ import annotations

import hashlib
import os
import signal
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from end_of_term import _engine
from end_of_term.delivery import (
    CURRENT_NAMES,
    FAULT_ENV,
    FAULT_NAMES,
    DeliveryError,
    DeliverySession,
    DeliverySpec,
)


def snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = f"symlink:{os.readlink(path)}"
        elif path.is_file():
            result[relative] = hashlib.sha256(path.read_bytes()).hexdigest()
        elif path.is_dir():
            result[relative] = "directory"
    return result


class DeliverySessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name) / "delivery"
        self.spec = DeliverySpec(self.root)

    def tearDown(self) -> None:
        os.environ.pop(FAULT_ENV, None)
        os.environ.pop("PRESTO_CLEAN_DELIVERY_SIGNAL_BEFORE_RECORD", None)
        self.temporary.cleanup()

    def candidate(self, marker: str, *, session: DeliverySession) -> None:
        payloads = {
            "end-of-term-full.md": f"# {marker}\n".encode(),
            "end-of-term-package.typ": f"// {marker}\n".encode(),
            "end-of-term-package.pdf": b"%PDF-1.7\n" + marker.encode(),
            "score-list.xlsx": b"PK\x03\x04" + marker.encode(),
        }
        for name in CURRENT_NAMES:
            session.candidate_path(name).write_bytes(payloads[name])

    def publish(self, marker: str) -> str:
        with DeliverySession(self.spec) as session:
            self.candidate(marker, session=session)
            return session.publish()

    def current_bytes(self) -> dict[str, bytes]:
        return {name: (self.root / name).read_bytes() for name in CURRENT_NAMES}

    def test_first_publish_is_exact_and_identical_is_inode_preserving(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        self.assertEqual(set(path.name for path in self.root.iterdir()), set(CURRENT_NAMES))
        before = {name: (self.root / name).stat() for name in CURRENT_NAMES}

        self.assertEqual(self.publish("v1"), "identical")

        after = {name: (self.root / name).stat() for name in CURRENT_NAMES}
        self.assertFalse((self.root / "history").exists())
        self.assertFalse((self.root / ".work").exists())
        for name in CURRENT_NAMES:
            self.assertEqual((before[name].st_ino, before[name].st_mtime_ns),
                             (after[name].st_ino, after[name].st_mtime_ns))

    def test_changed_bundle_uses_max_plus_one_history(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        history = self.root / "history"
        for sequence in ("001", "003"):
            directory = history / sequence
            directory.mkdir(parents=True)
            for name in CURRENT_NAMES:
                (directory / name).write_bytes(f"historic-{sequence}-{name}".encode())
        old = self.current_bytes()

        self.assertEqual(self.publish("v2"), "changed")

        self.assertEqual({path.name for path in history.iterdir()}, {"001", "003", "004"})
        self.assertEqual({name: (history / "004" / name).read_bytes() for name in CURRENT_NAMES}, old)
        self.assertEqual({path.name for path in (history / "004").iterdir()}, set(CURRENT_NAMES))

    def test_every_fault_restores_current_and_existing_history(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        history = self.root / "history" / "003"
        history.mkdir(parents=True)
        for name in CURRENT_NAMES:
            (history / name).write_bytes(f"history-{name}".encode())
        before = snapshot(self.root)

        for fault in FAULT_NAMES:
            with self.subTest(fault=fault):
                os.environ[FAULT_ENV] = fault
                with self.assertRaises(DeliveryError):
                    self.publish(f"failed-{fault}")
                os.environ.pop(FAULT_ENV, None)
                self.assertEqual(snapshot(self.root), before)

    def test_int_and_term_restore_after_first_replacement(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        before = snapshot(self.root)
        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signum=signum):
                with DeliverySession(self.spec) as session:
                    self.candidate(f"signal-{signum}", session=session)
                    original_fault = session._fault

                    def interrupt(name: str) -> None:
                        if name == "after_publish_file_1":
                            os.kill(os.getpid(), signum)
                        original_fault(name)

                    session._fault = interrupt
                    with self.assertRaises(DeliveryError):
                        session.publish()
                self.assertEqual(snapshot(self.root), before)

    def test_first_publish_signal_between_replace_and_record_leaves_no_current(self) -> None:
        for signal_name in ("SIGINT", "SIGTERM"):
            with self.subTest(signal_name=signal_name):
                os.environ["PRESTO_CLEAN_DELIVERY_SIGNAL_BEFORE_RECORD"] = signal_name
                with DeliverySession(self.spec) as session:
                    self.candidate(signal_name, session=session)
                    with self.assertRaises(DeliveryError):
                        session.publish()
                os.environ.pop("PRESTO_CLEAN_DELIVERY_SIGNAL_BEFORE_RECORD", None)
                self.assertFalse(any((self.root / name).exists() for name in CURRENT_NAMES))

    def test_unknown_symlink_partial_and_lock_fail_before_mutation(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        baseline = snapshot(self.root)
        for name, creator in (
            ("unknown.txt", lambda path: path.write_text("unknown", encoding="utf-8")),
            ("legacy", lambda path: path.symlink_to("outside")),
        ):
            with self.subTest(name=name):
                path = self.root / name
                creator(path)
                before = snapshot(self.root)
                with self.assertRaises(DeliveryError):
                    self.publish("v2")
                self.assertEqual(snapshot(self.root), before)
                path.unlink()
                self.assertEqual(snapshot(self.root), baseline)

        (self.root / CURRENT_NAMES[0]).unlink()
        partial = snapshot(self.root)
        with self.assertRaises(DeliveryError):
            self.publish("v2")
        self.assertEqual(snapshot(self.root), partial)

    def test_concurrent_lock_and_stale_work_are_preserved(self) -> None:
        with DeliverySession(self.spec) as first:
            self.candidate("v1", session=first)
            with self.assertRaises(DeliveryError):
                DeliverySession(self.spec).__enter__()
            self.assertEqual(first.publish(), "first")

        stale = self.root / ".work" / "stale-run"
        stale.mkdir(parents=True)
        marker = stale / "evidence.txt"
        marker.write_text("keep", encoding="utf-8")
        before = snapshot(self.root)
        with self.assertRaises(DeliveryError):
            DeliverySession(self.spec).__enter__()
        self.assertEqual(snapshot(self.root), before)


class DeliverIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        temporary_root = Path(self.temporary.name)
        self.out_dir = temporary_root / "delivery"
        self.skill_dir = Path(__file__).resolve().parents[2]
        source = self.skill_dir / "templates" / "end-of-term-full.md"
        self.input_path = temporary_root / "input.md"
        self.input_path.write_bytes(source.read_bytes())

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @staticmethod
    def compile_success(_typst: Path, pdf: Path) -> tuple[str, str]:
        pdf.write_bytes(b"%PDF-1.7\nfixture\n%%EOF\n")
        return "compiled", str(pdf)

    def publish_v1(self) -> None:
        with mock.patch.object(_engine, "compile_pdf", side_effect=self.compile_success):
            result = _engine.deliver(self.input_path, self.out_dir, self.skill_dir)
        self.assertEqual(result["publication"], "first")

    def test_compile_failure_never_mutates_current_or_history(self) -> None:
        self.publish_v1()
        before = snapshot(self.out_dir)
        self.input_path.write_text(self.input_path.read_text(encoding="utf-8").replace(
            "date: 2026-06-05", "date: 2026-06-06"), encoding="utf-8")

        with mock.patch.object(_engine, "compile_pdf", return_value=("failed", "forced failure")):
            with self.assertRaises(_engine.RenderError):
                _engine.deliver(self.input_path, self.out_dir, self.skill_dir)

        self.assertEqual(snapshot(self.out_dir), before)

    def test_malformed_xlsx_is_rejected_before_publish(self) -> None:
        self.publish_v1()
        before = snapshot(self.out_dir)

        def malformed(path: Path, *_args: object, **_kwargs: object) -> None:
            path.write_bytes(b"not-an-xlsx")

        with mock.patch.object(_engine, "compile_pdf", side_effect=self.compile_success), \
                mock.patch.object(_engine, "write_single_sheet_xlsx", side_effect=malformed):
            with self.assertRaises(_engine.RenderError):
                _engine.deliver(self.input_path, self.out_dir, self.skill_dir)

        self.assertEqual(snapshot(self.out_dir), before)

    def test_real_candidate_validators_cover_all_four_formats(self) -> None:
        self.publish_v1()
        _engine.validate_delivery_bundle({name: (self.out_dir / name).read_bytes() for name in CURRENT_NAMES})


if __name__ == "__main__":
    unittest.main()
