from __future__ import annotations

import hashlib
import os
import signal
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from school_presentation.delivery import (
    FAULT_ENV,
    FAULT_NAMES,
    DeliveryError,
    DeliverySession,
    DeliverySpec,
    validate_html_candidate,
)


def snapshot(root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    if not root.exists() and not root.is_symlink():
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


def html(marker: str) -> bytes:
    return (
        "<!doctype html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">"
        "<style>body{color:#000}</style></head><body>"
        f"<div class=\"app\"><div class=\"page-source\">{marker}</div></div>"
        "<script>const pages=[];</script></body></html>"
    ).encode("utf-8")


class DeliverySessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.root = self.base / "delivery"
        self.input_root = self.base / "input"
        self.input_root.mkdir()
        self.spec = DeliverySpec(self.root, "deck", ())

    def tearDown(self) -> None:
        os.environ.pop(FAULT_ENV, None)
        self.temporary.cleanup()

    def publish(self, marker: str, *, assets: tuple[str, ...] = ()) -> str:
        spec = DeliverySpec(self.root, "deck", assets)
        with DeliverySession(spec) as session:
            session.stage_candidate(
                f"# {marker}\n".encode("utf-8"),
                html(marker),
                asset_root=self.input_root,
            )
            return session.publish(lambda bundle: validate_html_candidate(bundle, 1))

    def test_first_identical_changed_and_gap_history(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        before = {name: (self.root / name).stat() for name in ("deck.md", "deck.html")}
        self.assertEqual(self.publish("v1"), "identical")
        after = {name: (self.root / name).stat() for name in ("deck.md", "deck.html")}
        self.assertFalse((self.root / "history").exists())
        for name in before:
            self.assertEqual(
                (before[name].st_ino, before[name].st_mtime_ns),
                (after[name].st_ino, after[name].st_mtime_ns),
            )

        for sequence in ("001", "003"):
            directory = self.root / "history" / sequence
            directory.mkdir(parents=True)
            (directory / "marker").write_text(sequence, encoding="utf-8")
        previous = {name: (self.root / name).read_bytes() for name in ("deck.md", "deck.html")}
        self.assertEqual(self.publish("v2"), "changed")
        archived = self.root / "history" / "004"
        self.assertEqual({path.name for path in archived.iterdir()}, {"deck.md", "deck.html"})
        self.assertEqual({name: (archived / name).read_bytes() for name in previous}, previous)

    def test_archived_referenced_assets_resolve_and_unreferenced_stays_out(self) -> None:
        assets = self.input_root / "assets"
        assets.mkdir()
        (assets / "diagram.png").write_bytes(b"v1-image")
        (assets / "unused.png").write_bytes(b"unused")
        spec = DeliverySpec(self.root, "deck", ("assets/diagram.png",))
        with DeliverySession(spec) as session:
            session.stage_candidate(
                b"# v1\n\n![diagram](assets/diagram.png)\n",
                html("v1"),
                asset_root=self.input_root,
            )
            self.assertEqual(session.publish(lambda bundle: validate_html_candidate(bundle, 1)), "first")

        (assets / "diagram.png").write_bytes(b"v2-image")
        with DeliverySession(spec) as session:
            session.stage_candidate(
                b"# v2\n\n![diagram](assets/diagram.png)\n",
                html("v2"),
                asset_root=self.input_root,
            )
            self.assertEqual(session.publish(lambda bundle: validate_html_candidate(bundle, 1)), "changed")

        archived = self.root / "history" / "001"
        self.assertEqual((archived / "assets" / "diagram.png").read_bytes(), b"v1-image")
        self.assertFalse((archived / "assets" / "unused.png").exists())
        markdown = (archived / "deck.md").read_text(encoding="utf-8")
        self.assertIn("assets/diagram.png", markdown)
        self.assertTrue((archived / "assets" / "diagram.png").is_file())

    def test_all_faults_and_signals_restore_pair_history_and_sources(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        sources = self.root / "sources"
        sources.mkdir()
        (sources / "notes.txt").write_text("user-owned", encoding="utf-8")
        baseline = snapshot(self.root)
        for fault in FAULT_NAMES:
            with self.subTest(fault=fault):
                os.environ[FAULT_ENV] = fault
                with self.assertRaises(DeliveryError):
                    self.publish(f"failed-{fault}")
                os.environ.pop(FAULT_ENV, None)
                self.assertEqual(snapshot(self.root), baseline)

        for signum in (signal.SIGINT, signal.SIGTERM):
            with self.subTest(signum=signum):
                with DeliverySession(self.spec) as session:
                    session.stage_candidate(b"# signal\n", html("signal"), asset_root=self.input_root)
                    original_fault = session._fault

                    def interrupt(name: str) -> None:
                        if name == "after_publish_file_1":
                            os.kill(os.getpid(), signum)
                        original_fault(name)

                    session._fault = interrupt
                    with self.assertRaises(DeliveryError):
                        session.publish(lambda bundle: validate_html_candidate(bundle, 1))
                self.assertEqual(snapshot(self.root), baseline)

    def test_validation_failures_never_change_current(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        before = snapshot(self.root)
        invalid_candidates = (
            html("oversize") + b"x" * 1024 * 1024,
            html("online").replace(b"</body>", b'<img src="https://example.invalid/x.png"></body>'),
            b"<html><body>missing required DOM</body></html>",
        )
        for candidate in invalid_candidates:
            with self.subTest(candidate=candidate[:32]):
                with DeliverySession(self.spec) as session:
                    session.stage_candidate(b"# invalid\n", candidate, asset_root=self.input_root)
                    with self.assertRaises(DeliveryError):
                        session.publish(lambda bundle: validate_html_candidate(bundle, 0.5))
                self.assertEqual(snapshot(self.root), before)

        missing_spec = DeliverySpec(self.root, "deck", ("assets/missing.png",))
        with self.assertRaises(DeliveryError):
            with DeliverySession(missing_spec) as session:
                session.stage_candidate(
                    b"# missing\n\n![missing](assets/missing.png)\n",
                    html("missing"),
                    asset_root=self.input_root,
                )
        self.assertEqual(snapshot(self.root), before)

    def test_unknown_legacy_manifest_symlink_partial_and_stale_work_fail_closed(self) -> None:
        self.assertEqual(self.publish("v1"), "first")
        cases = (
            ("unknown.txt", lambda path: path.write_text("unknown", encoding="utf-8")),
            ("manifest.json", lambda path: path.write_text("{}", encoding="utf-8")),
            ("media", lambda path: path.mkdir()),
            ("legacy-link", lambda path: path.symlink_to(self.base)),
        )
        for name, create in cases:
            with self.subTest(name=name):
                path = self.root / name
                create(path)
                before = snapshot(self.root)
                with self.assertRaises(DeliveryError):
                    self.publish("v2")
                self.assertEqual(snapshot(self.root), before)
                path.unlink() if path.is_symlink() or path.is_file() else path.rmdir()

        (self.root / "deck.html").unlink()
        partial = snapshot(self.root)
        with self.assertRaises(DeliveryError):
            self.publish("v2")
        self.assertEqual(snapshot(self.root), partial)

        (self.root / "deck.html").write_bytes(html("v1"))
        stale = self.root / ".work" / "unrelated-run"
        stale.mkdir(parents=True)
        (stale / "keep.txt").write_text("keep", encoding="utf-8")
        before = snapshot(self.root)
        with self.assertRaises(DeliveryError):
            self.publish("v2")
        self.assertEqual(snapshot(self.root), before)

    def test_seed_markdown_is_restored_when_first_publication_fails(self) -> None:
        self.root.mkdir()
        seed = self.root / "deck.md"
        seed.write_bytes(b"# reviewed seed\n")
        spec = DeliverySpec(self.root, "deck", (), seed_markdown=seed)
        before = snapshot(self.root)
        os.environ[FAULT_ENV] = "after_publish_file_1"
        with self.assertRaises(DeliveryError):
            with DeliverySession(spec) as session:
                session.stage_candidate(seed.read_bytes(), html("seed"), asset_root=self.root)
                session.publish(lambda bundle: validate_html_candidate(bundle, 1))
        self.assertEqual(snapshot(self.root), before)


if __name__ == "__main__":
    unittest.main()
