from __future__ import annotations

import hashlib
import os
import signal
import subprocess
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

        (self.root / "tiaokedan.typ").unlink()
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


class PublicCliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.temp = Path(self.temporary.name)
        self.root = self.temp / "delivery"
        self.input_path = self.temp / "input.md"
        self.script = Path(__file__).resolve().with_name("tiaokedan.sh")
        template = Path(__file__).resolve().parents[1] / "templates" / "tiaokedan.md"
        self.input_path.write_bytes(template.read_bytes())
        self.bin_dir = self.temp / "bin"
        self.bin_dir.mkdir()
        self.typst = self.bin_dir / "typst"
        self.write_typst("success")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def write_typst(self, mode: str) -> None:
        if mode == "success":
            body = '#!/bin/sh\nprintf "%%PDF-1.7\\n" > "$3"\ncat "$2" >> "$3"\nprintf "%%%%EOF\\n" >> "$3"\n'
        elif mode == "invalid":
            body = '#!/bin/sh\nprintf "not-a-pdf\\n" > "$3"\n'
        else:
            body = '#!/bin/sh\nprintf "forced compile failure\\n" >&2\nexit 7\n'
        self.typst.write_text(body, encoding="utf-8")
        self.typst.chmod(0o755)

    def run_cli(self, *, pdf: bool = True, expected: Path | None = None, fault: str | None = None) -> subprocess.CompletedProcess[str]:
        command = [str(self.script), "render", "--input", str(self.input_path), "--typ", str(self.root / "tiaokedan.typ")]
        if pdf:
            command.extend(("--pdf", str(self.root / "tiaokedan.pdf")))
        if expected is not None:
            command.extend(("--expected-typ", str(expected)))
        environment = os.environ.copy()
        environment["PATH"] = f"{self.bin_dir}{os.pathsep}{environment.get('PATH', '')}"
        if fault is not None:
            environment[FAULT_ENV] = fault
        return subprocess.run(command, capture_output=True, text=True, check=False, env=environment)

    def change_input(self, old: str = "2026-06-21", new: str = "2026-06-22") -> None:
        self.input_path.write_text(self.input_path.read_text(encoding="utf-8").replace(old, new), encoding="utf-8")

    def test_real_cli_first_identical_changed_and_fault_matrix(self) -> None:
        first = self.run_cli()
        self.assertEqual(first.returncode, 0, first.stderr)
        before_stats = {name: (self.root / name).stat() for name in ("tiaokedan.md", "tiaokedan.typ", "tiaokedan.pdf")}
        identical = self.run_cli()
        self.assertEqual(identical.returncode, 0, identical.stderr)
        self.assertFalse((self.root / "history").exists())
        for name, metadata in before_stats.items():
            observed = (self.root / name).stat()
            self.assertEqual((metadata.st_ino, metadata.st_mtime_ns), (observed.st_ino, observed.st_mtime_ns))

        self.change_input()
        changed = self.run_cli()
        self.assertEqual(changed.returncode, 0, changed.stderr)
        self.assertEqual({path.name for path in (self.root / "history" / "001").iterdir()}, {"tiaokedan.md", "tiaokedan.typ", "tiaokedan.pdf"})
        baseline = snapshot(self.root)
        self.change_input("2026-06-22", "2026-06-23")
        for fault in FAULT_NAMES:
            with self.subTest(fault=fault):
                result = self.run_cli(fault=fault)
                self.assertNotEqual(result.returncode, 0)
                self.assertLess(len((result.stdout + result.stderr).encode()), 4096)
                self.assertEqual(snapshot(self.root), baseline)

    def test_generation_expected_and_pdf_validation_failures_do_not_mutate(self) -> None:
        self.assertEqual(self.run_cli().returncode, 0)
        baseline = snapshot(self.root)
        self.change_input()

        expected = self.temp / "expected.typ"
        expected.write_text("different\n", encoding="utf-8")
        mismatch = self.run_cli(expected=expected)
        self.assertNotEqual(mismatch.returncode, 0)
        self.assertLess(len((mismatch.stdout + mismatch.stderr).encode()), 4096)
        self.assertEqual(snapshot(self.root), baseline)

        self.write_typst("failure")
        compile_failure = self.run_cli()
        self.assertNotEqual(compile_failure.returncode, 0)
        self.assertEqual(snapshot(self.root), baseline)

        self.write_typst("invalid")
        invalid_pdf = self.run_cli()
        self.assertNotEqual(invalid_pdf.returncode, 0)
        self.assertEqual(snapshot(self.root), baseline)

        self.input_path.write_text(self.input_path.read_text(encoding="utf-8").replace("电气工程系", "{{待补充: 系部}}"), encoding="utf-8")
        unresolved = self.run_cli()
        self.assertNotEqual(unresolved.returncode, 0)
        self.assertEqual(snapshot(self.root), baseline)

    def test_real_cli_history_gap_unknown_symlink_and_path_mismatch(self) -> None:
        self.assertEqual(self.run_cli().returncode, 0)
        history = self.root / "history"
        for sequence in ("001", "003"):
            directory = history / sequence
            directory.mkdir(parents=True)
            for name in ("tiaokedan.md", "tiaokedan.typ", "tiaokedan.pdf"):
                (directory / name).write_bytes(f"historic-{sequence}-{name}".encode())
        self.change_input()
        self.assertEqual(self.run_cli().returncode, 0)
        self.assertTrue((history / "004").is_dir())

        for name, symlink in (("unknown.txt", False), ("bad-link", True)):
            path = self.root / name
            path.symlink_to("outside") if symlink else path.write_text("unknown", encoding="utf-8")
            before = snapshot(self.root)
            result = self.run_cli()
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(snapshot(self.root), before)
            path.unlink()

        mismatch = subprocess.run(
            [str(self.script), "render", "--input", str(self.input_path), "--typ", str(self.root / "tiaokedan.typ"), "--pdf", str(self.temp / "tiaokedan.pdf")],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertNotEqual(mismatch.returncode, 0)


if __name__ == "__main__":
    unittest.main()
