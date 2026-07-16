#!/usr/bin/env python3
"""Render canonical school-pptx Markdown and publish a safe dual artifact pair."""

from __future__ import annotations

import argparse
import copy
import fcntl
import inspect
import os
import re
import secrets
import signal
import stat
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, BinaryIO, Callable

from markdown_contract import ManifestError, load_manifest, parse_document, print_diagnostic
from pptx_emit import PptxEmitError, emit_deck, validate_staged_package
from pptx_paginate import build_deck_plan


MAX_PUBLIC_DIAGNOSTICS = 200
MAX_STEM_LENGTH = 128
TEMP_NAMES = {
    "markdown": tuple(f".school-pptx-render-md.tmp-{index}" for index in range(100)),
    "pptx": tuple(f".school-pptx-render-pptx.tmp-{index}" for index in range(100)),
}
RENDER_PRE_VALIDATE_HOOK: Callable[[Path], None] | None = None
RENDER_PRE_SAVE_HOOK: Callable[[Any, BinaryIO], None] | None = None
RENDER_PRE_PUBLISH_HOOK: Callable[[Path], None] | None = None
RENDER_BETWEEN_REPLACE_HOOK: Callable[[Path], None] | None = None
RENDER_POST_PARSE_HOOK: Callable[[Path], None] | None = None

SUPPORT_DIRECTORIES = ("sources", "assets", "history", ".work")
FAULT_NAMES = (
    "after_candidate_validation",
    "after_history_reservation",
    "after_archive_snapshot",
    "after_publish_file_1",
    "after_publish_middle_file",
    "before_post_publish_verify",
    "before_work_cleanup",
)
FAULT_ENV = "PRESTO_CLEAN_DELIVERY_FAULT"
ASSET_REFERENCE = re.compile(r"!?\[[^\]]*\]\((?:<)?(assets/[^\s)>]+)(?:>)?(?:\s+[^)]*)?\)")


class RenderError(RuntimeError):
    """Bounded public render failure."""

    def __init__(self, code: str, message: str, fix: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.fix = fix


def managed_asset_references(markdown: bytes) -> tuple[str, ...]:
    """Return the exact confirmed persistent assets referenced by reviewed Markdown."""
    try:
        text = markdown.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise RenderError("INPUT_ENCODING_INVALID", "输入 Markdown 必须是 UTF-8。", "将文件转为 UTF-8 后重试。") from exc
    references: set[str] = set()
    for match in ASSET_REFERENCE.finditer(text):
        relative = match.group(1)
        parts = Path(relative).parts
        if (not parts or parts[0] != "assets" or any(
                not part or part in {".", ".."} or "\x00" in part or "/" in part or "\\" in part
                for part in parts)):
            raise RenderError("ASSET_PATH_INVALID", "Markdown 包含不安全的 assets 相对引用。", "仅使用 assets/ 下的安全相对路径。")
        references.add(Path(*parts).as_posix())
    return tuple(sorted(references))


@dataclass(frozen=True)
class DeliverySpec:
    delivery_root: Path
    stem: str
    managed_assets: tuple[str, ...]

    @property
    def current_names(self) -> tuple[str, ...]:
        return (f"{self.stem}.md", f"{self.stem}.pptx", *self.managed_assets)


class DeliverySession:
    """Whole-bundle history/no-op/rollback transaction for a school-pptx DeliverySpec."""

    def __init__(self, spec: DeliverySpec) -> None:
        self.spec = spec
        self.root = Path(os.path.abspath(spec.delivery_root))
        self.root_fd: int | None = None
        self.root_identity: tuple[int, int] | None = None
        self.work_fd: int | None = None
        self.run_name = f"run-{secrets.token_hex(8)}"
        self.run_root = self.root / ".work" / self.run_name
        self.candidate_root = self.run_root / "candidate"
        self.rollback_root = self.run_root / "rollback"
        self.evidence_root = self.run_root / "evidence"
        self._lock_owned = False
        self._work_created = False
        self._history_sequence: str | None = None
        self._old_bytes: dict[str, bytes] = {}
        self._published: list[str] = []

    def __enter__(self) -> DeliverySession:
        try:
            self.root.mkdir(parents=True, exist_ok=True)
            status = os.stat(self.root, follow_symlinks=False)
            if not stat.S_ISDIR(status.st_mode):
                raise RenderError("OUTPUT_ROOT_INVALID", "--out-dir 必须是真实目录。", "选择非符号链接目录。")
            self.root_fd = os.open(self.root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
            held = os.fstat(self.root_fd)
            self.root_identity = (held.st_dev, held.st_ino)
            self._assert_root_identity()
            self._inspect_root(allow_owned_work=False)
            self._open_work()
            self._create_run_tree()
            return self
        except BaseException:
            self.close()
            raise

    def _assert_root_identity(self) -> None:
        if self.root_fd is None or self.root_identity is None:
            raise RenderError("OUTPUT_ROOT_CHANGED", "交付目录未保持打开。", "重新运行 render。")
        current = os.stat(self.root, follow_symlinks=False)
        held = os.fstat(self.root_fd)
        if (not stat.S_ISDIR(current.st_mode)
                or (current.st_dev, current.st_ino) != self.root_identity
                or (held.st_dev, held.st_ino) != self.root_identity):
            raise RenderError("OUTPUT_ROOT_CHANGED", "交付目录在发布期间被替换。", "恢复安全目录后重试。")

    @staticmethod
    def _entries(path: Path) -> tuple[str, ...]:
        return tuple(sorted(entry.name for entry in os.scandir(path)))

    @staticmethod
    def _require_real_directory(path: Path) -> None:
        status = os.stat(path, follow_symlinks=False)
        if not stat.S_ISDIR(status.st_mode):
            raise RenderError("OUTPUT_COLLISION", f"支持路径必须是真实目录：{path.name}", "移除符号链接或冲突路径。")

    @staticmethod
    def _read_regular(path: Path, *, nonempty: bool = True) -> bytes:
        descriptor = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
        try:
            status = os.fstat(descriptor)
            if not stat.S_ISREG(status.st_mode):
                raise RenderError("OUTPUT_COLLISION", f"受管路径不是普通文件：{path.name}", "移除冲突路径。")
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 1024 * 1024)
                if not chunk:
                    break
                chunks.append(chunk)
            payload = b"".join(chunks)
            if nonempty and not payload:
                raise RenderError("OUTPUT_COLLISION", f"受管文件为空：{path.name}", "恢复完整文件后重试。")
            return payload
        finally:
            os.close(descriptor)

    @staticmethod
    def _write_exclusive(path: Path, payload: bytes) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
        try:
            view = memoryview(payload)
            while view:
                written = os.write(descriptor, view)
                if written <= 0:
                    raise OSError("short write")
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)

    def _current_asset_names(self) -> tuple[str, ...]:
        markdown = self.root / f"{self.spec.stem}.md"
        if not markdown.exists():
            return ()
        return managed_asset_references(self._read_regular(markdown))

    def _inspect_asset_tree(self, expected: tuple[str, ...]) -> None:
        asset_root = self.root / "assets"
        if not asset_root.exists():
            if expected:
                raise RenderError("OUTPUT_PARTIAL", "current 缺少被 Markdown 引用的 assets。", "恢复完整交付后重试。")
            return
        self._require_real_directory(asset_root)
        actual = tuple(sorted(
            path.relative_to(self.root).as_posix()
            for path in asset_root.rglob("*")
            if path.is_file() and not path.is_symlink()
        ))
        for path in asset_root.rglob("*"):
            status = os.stat(path, follow_symlinks=False)
            if not (stat.S_ISDIR(status.st_mode) or stat.S_ISREG(status.st_mode)):
                raise RenderError("OUTPUT_COLLISION", "assets 包含非普通路径。", "先审计并移除冲突路径。")
        if actual != expected:
            raise RenderError("OUTPUT_UNKNOWN", "assets 集合与 current Markdown 引用不一致。", "通过确认式整理处理未引用或缺失资源。")

    def _inspect_history(self) -> None:
        history = self.root / "history"
        if not history.exists():
            return
        self._require_real_directory(history)
        for entry in history.iterdir():
            if not re.fullmatch(r"[0-9]{3,}", entry.name) or entry.is_symlink() or not entry.is_dir():
                raise RenderError("OUTPUT_HISTORY_INVALID", f"history 条目无效：{entry.name}", "先审计 history。")

    def _inspect_root(self, *, allow_owned_work: bool) -> bool:
        assert self.root_fd is not None
        self._assert_root_identity()
        entries = self._entries(self.root)
        pair = (f"{self.spec.stem}.md", f"{self.spec.stem}.pptx")
        allowed = set(pair) | set(SUPPORT_DIRECTORIES)
        unknown = [name for name in entries if name not in allowed]
        if unknown:
            raise RenderError("OUTPUT_UNKNOWN", f"交付根目录包含未知项：{unknown[0]}", "先运行只读审计与确认式整理。")
        present = tuple(name for name in pair if name in entries)
        if present and present != pair:
            raise RenderError("OUTPUT_PARTIAL", "current Markdown/PPTX 不完整。", "恢复完整 pair 后重试。")
        for name in present:
            self._read_regular(self.root / name)
        for name in SUPPORT_DIRECTORIES:
            if name in entries:
                self._require_real_directory(self.root / name)
        assets = self._current_asset_names() if present else ()
        self._inspect_asset_tree(assets)
        if ".work" in entries:
            work_entries = set(self._entries(self.root / ".work"))
            expected = {".lock", self.run_name} if allow_owned_work else set()
            if work_entries != expected:
                raise RenderError("OUTPUT_WORK_STALE", ".work 包含非本次运行内容。", "先审计 stale/concurrent work。")
        self._inspect_history()
        return bool(present)

    def _open_work(self) -> None:
        assert self.root_fd is not None
        try:
            os.mkdir(".work", 0o700, dir_fd=self.root_fd)
            self._work_created = True
        except FileExistsError:
            pass
        self.work_fd = os.open(".work", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=self.root_fd)
        try:
            lock_fd = os.open(".lock", os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600, dir_fd=self.work_fd)
        except FileExistsError as exc:
            raise RenderError("OUTPUT_LOCKED", "另一个 render 正持有交付锁。", "等待该运行结束后重试。") from exc
        os.close(lock_fd)
        self._lock_owned = True

    def _create_run_tree(self) -> None:
        assert self.work_fd is not None
        os.mkdir(self.run_name, 0o700, dir_fd=self.work_fd)
        self.candidate_root.mkdir()
        self.rollback_root.mkdir()
        self.evidence_root.mkdir()

    def stage_assets(self, input_root: Path) -> None:
        for relative in self.spec.managed_assets:
            source = input_root / relative
            payload = self._read_regular(source)
            self._write_exclusive(self.candidate_root / relative, payload)

    def _bundle_bytes(self, root: Path, names: tuple[str, ...]) -> dict[str, bytes]:
        return {name: self._read_regular(root / name) for name in names}

    def _fault(self, name: str) -> None:
        if os.environ.get(FAULT_ENV) == name:
            raise RenderError("OUTPUT_FAULT_INJECTED", f"发布故障注入：{name}", "排除故障后重试。")
        if name in {"after_publish_file_1", "after_publish_middle_file"} and RENDER_BETWEEN_REPLACE_HOOK is not None:
            try:
                RENDER_BETWEEN_REPLACE_HOOK(self.root)
            except Exception as exc:
                raise RenderError("OUTPUT_PAIR_INTERRUPTED", "受管 bundle 发布被中止。", "排除发布故障后重试。") from exc

    def _next_history(self) -> str:
        history = self.root / "history"
        values = [int(entry.name) for entry in history.iterdir()] if history.exists() else []
        return f"{max(values, default=0) + 1:03d}"

    def _remove_empty_asset_dirs(self, root: Path) -> None:
        assets = root / "assets"
        if not assets.exists():
            return
        for path in sorted((item for item in assets.rglob("*") if item.is_dir()), reverse=True):
            try:
                path.rmdir()
            except OSError:
                pass
        try:
            assets.rmdir()
        except OSError:
            pass

    def _remove_names(self, root: Path, names: tuple[str, ...]) -> None:
        for name in sorted(names, key=lambda value: value.count("/"), reverse=True):
            try:
                (root / name).unlink()
            except FileNotFoundError:
                pass
        self._remove_empty_asset_dirs(root)

    def _restore(self, old_names: tuple[str, ...]) -> None:
        all_names = tuple(sorted(set(self._published) | set(old_names)))
        self._remove_names(self.root, all_names)
        for name in old_names:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            os.replace(self.rollback_root / name, target)
        if self._history_sequence is not None:
            history_entry = self.root / "history" / self._history_sequence
            self._remove_names(history_entry, old_names)
            try:
                history_entry.rmdir()
            except FileNotFoundError:
                pass
            try:
                (self.root / "history").rmdir()
            except OSError:
                pass
            self._history_sequence = None
        if self._bundle_bytes(self.root, old_names) != self._old_bytes:
            raise RenderError("OUTPUT_ROLLBACK_FAILED", "旧 bundle 回滚验证失败。", "停止使用目录并人工恢复。")

    def publish(self, expected_slides: int) -> str:
        candidate_names = self.spec.current_names
        candidate = self._bundle_bytes(self.candidate_root, candidate_names)
        validate_staged_package(self.candidate_root / f"{self.spec.stem}.pptx", expected_slides=expected_slides)
        if managed_asset_references(candidate[f"{self.spec.stem}.md"]) != self.spec.managed_assets:
            raise RenderError("ASSET_SET_INVALID", "candidate assets 与 Markdown 引用不一致。", "确认引用资源后重试。")
        self._fault("after_candidate_validation")
        current_exists = self._inspect_root(allow_owned_work=True)
        old_assets = self._current_asset_names() if current_exists else ()
        old_names = (f"{self.spec.stem}.md", f"{self.spec.stem}.pptx", *old_assets) if current_exists else ()
        current = self._bundle_bytes(self.root, old_names)
        if set(old_names) == set(candidate_names) and current == candidate:
            self._fault("before_work_cleanup")
            return "identical"
        self._old_bytes = current
        for name, payload in current.items():
            self._write_exclusive(self.rollback_root / name, payload)
        previous_handlers: dict[int, Any] = {}
        history_entry: Path | None = None

        def interrupt(signum: int, _frame: object) -> None:
            raise RenderError("OUTPUT_INTERRUPTED", f"发布被信号 {signum} 中止。", "重新运行 render。")

        try:
            for signum in (signal.SIGINT, signal.SIGTERM):
                previous_handlers[signum] = signal.signal(signum, interrupt)
            if current:
                (self.root / "history").mkdir(exist_ok=True)
                self._history_sequence = self._next_history()
                history_entry = self.root / "history" / self._history_sequence
                history_entry.mkdir()
                self._fault("after_history_reservation")
                for name, payload in current.items():
                    self._write_exclusive(history_entry / name, payload)
                self._fault("after_archive_snapshot")
            mutation_names = tuple(dict.fromkeys((*candidate_names, *old_names)))
            for index, name in enumerate(mutation_names, start=1):
                target = self.root / name
                if name in candidate:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    os.replace(self.candidate_root / name, target)
                else:
                    target.unlink()
                self._published.append(name)
                if index == 1:
                    self._fault("after_publish_file_1")
                if index == max(1, len(mutation_names) // 2):
                    self._fault("after_publish_middle_file")
            self._remove_empty_asset_dirs(self.root)
            assert self.root_fd is not None
            os.fsync(self.root_fd)
            self._fault("before_post_publish_verify")
            if self._bundle_bytes(self.root, candidate_names) != candidate:
                raise RenderError("OUTPUT_VERIFY_FAILED", "发布后的 exact bundle 验证失败。", "重新运行 render。")
            if history_entry is not None and self._bundle_bytes(history_entry, old_names) != current:
                raise RenderError("OUTPUT_HISTORY_INVALID", "history bundle 验证失败。", "重新运行 render。")
            self._fault("before_work_cleanup")
            return "changed" if current else "first"
        except BaseException:
            self._restore(old_names)
            raise
        finally:
            for signum, handler in previous_handlers.items():
                signal.signal(signum, handler)

    def close(self) -> None:
        for root in (self.candidate_root, self.rollback_root, self.evidence_root):
            try:
                status = os.stat(root, follow_symlinks=False)
            except OSError:
                continue
            if stat.S_ISDIR(status.st_mode):
                files = tuple(
                    path.relative_to(root).as_posix()
                    for path in root.rglob("*")
                    if path.is_file() and not path.is_symlink()
                )
                self._remove_names(root, files)
                try:
                    root.rmdir()
                except OSError:
                    pass
        try:
            self.run_root.rmdir()
        except OSError:
            pass
        if self.work_fd is not None and self._lock_owned:
            try:
                os.unlink(".lock", dir_fd=self.work_fd)
            except OSError:
                pass
            self._lock_owned = False
        if self.work_fd is not None:
            os.close(self.work_fd)
            self.work_fd = None
        if self.root_fd is not None:
            try:
                os.rmdir(".work", dir_fd=self.root_fd)
            except OSError:
                pass
            os.close(self.root_fd)
            self.root_fd = None

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()


def secure_io_capabilities() -> tuple[str, ...]:
    missing: list[str] = []
    for constant in ("O_DIRECTORY", "O_NOFOLLOW"):
        if not hasattr(os, constant):
            missing.append(f"os.{constant}")
    for function in (os.open, os.stat, os.unlink):
        if function not in os.supports_dir_fd:
            missing.append(f"{function.__name__}(dir_fd)")
    parameters = inspect.signature(os.replace).parameters
    for parameter in ("src_dir_fd", "dst_dir_fd"):
        if parameter not in parameters:
            missing.append(f"os.replace({parameter})")
    return tuple(missing)


def validate_stem(stem: str) -> str:
    if (
        not stem
        or stem in {".", ".."}
        or len(stem) > MAX_STEM_LENGTH
        or "\x00" in stem
        or "/" in stem
        or "\\" in stem
        or Path(stem).name != stem
    ):
        raise RenderError(
            "OUTPUT_STEM_INVALID",
            "--stem 必须是非空的单个安全文件名，不得包含路径分隔符、. 或 ..。",
            "改用不含目录部分的简短 stem。",
        )
    return stem


class SecureRenderDestination:
    """Held-descriptor publisher for one renderer-owned Markdown/PPTX pair."""

    def __init__(self, output_root: Path, stem: str, input_path: Path) -> None:
        self.output_root = output_root
        self.stem = validate_stem(stem)
        self.input_path = input_path
        self.root_fd: int | None = None
        self.root_identity: tuple[int, int] | None = None
        self.temporary: dict[str, tuple[str, tuple[int, int], int]] = {}
        self.final_names = {"markdown": f"{self.stem}.md", "pptx": f"{self.stem}.pptx"}

    def __enter__(self) -> SecureRenderDestination:
        missing = secure_io_capabilities()
        if missing:
            raise RenderError(
                "OUTPUT_SECURE_IO_UNAVAILABLE",
                f"当前运行时缺少安全发布能力：{', '.join(missing)}。",
                "改用支持 held directory descriptor、O_NOFOLLOW 与 descriptor-relative replace 的 Python。",
            )
        try:
            self.output_root.mkdir(parents=True, exist_ok=True)
            root_status = os.stat(self.output_root, follow_symlinks=False)
            if not stat.S_ISDIR(root_status.st_mode):
                raise RenderError("OUTPUT_ROOT_INVALID", "--out-dir 必须是普通目录且不能是符号链接。", "选择安全的交付目录。")
            flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
            self.root_fd = os.open(self.output_root, flags)
            opened = os.fstat(self.root_fd)
            self.root_identity = (opened.st_dev, opened.st_ino)
            self.assert_root_identity()
            self._assert_input_distinct()
            self.assert_final_paths()
            return self
        except RenderError:
            self.close()
            raise
        except OSError as exc:
            self.close()
            raise RenderError("OUTPUT_ROOT_INVALID", "--out-dir 无法安全创建或打开。", "检查目录权限和符号链接后重试。") from exc

    def _assert_input_distinct(self) -> None:
        input_resolved = self.input_path.resolve(strict=False)
        for name in self.final_names.values():
            if (self.output_root / name).resolve(strict=False) == input_resolved:
                raise RenderError(
                    "OUTPUT_INPUT_COLLISION",
                    "输入 Markdown 不能与任一公开输出路径相同。",
                    "选择其他 --out-dir 或 --stem，避免原地覆盖输入。",
                )

    def assert_root_identity(self) -> None:
        if self.root_fd is None or self.root_identity is None:
            raise RenderError("OUTPUT_ROOT_CHANGED", "公开输出目录未保持打开状态。", "重新运行 render。")
        try:
            current = os.stat(self.output_root, follow_symlinks=False)
            held = os.fstat(self.root_fd)
        except OSError as exc:
            raise RenderError("OUTPUT_ROOT_CHANGED", "公开输出目录在渲染期间被替换。", "恢复安全目录后重试。") from exc
        identities = (current.st_dev, current.st_ino), (held.st_dev, held.st_ino)
        if not stat.S_ISDIR(current.st_mode) or identities[0] != self.root_identity or identities[1] != self.root_identity:
            raise RenderError("OUTPUT_ROOT_CHANGED", "公开输出目录在渲染期间被替换。", "恢复安全目录后重试。")

    def assert_final_paths(self) -> None:
        assert self.root_fd is not None
        for name in self.final_names.values():
            try:
                result = os.stat(name, dir_fd=self.root_fd, follow_symlinks=False)
            except FileNotFoundError:
                continue
            except OSError as exc:
                raise RenderError("OUTPUT_COLLISION", "无法安全检查公开输出路径。", "移除冲突路径后重试。") from exc
            if not stat.S_ISREG(result.st_mode):
                raise RenderError(
                    "OUTPUT_COLLISION",
                    f"公开输出路径 {name} 必须不存在或为普通文件，不能是目录或符号链接。",
                    "移除冲突路径或选择其他 stem。",
                )

    def _create_temporary(self, kind: str) -> tuple[int, str]:
        assert self.root_fd is not None
        for name in TEMP_NAMES[kind]:
            try:
                access_mode = os.O_RDWR if kind == "pptx" else os.O_WRONLY
                file_descriptor = os.open(
                    name,
                    access_mode | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600,
                    dir_fd=self.root_fd,
                )
                created = os.fstat(file_descriptor)
                if kind == "pptx" and fcntl.fcntl(file_descriptor, fcntl.F_GETFL) & os.O_ACCMODE != os.O_RDWR:
                    os.close(file_descriptor)
                    raise RenderError("OUTPUT_TEMP_FAILED", "PPTX 临时文件不是 read-write descriptor。", "改用兼容运行时后重试。")
                self.temporary[kind] = (name, (created.st_dev, created.st_ino), file_descriptor)
                return file_descriptor, name
            except FileExistsError:
                continue
            except OSError as exc:
                raise RenderError("OUTPUT_TEMP_FAILED", "无法创建命令自有同目录临时文件。", "检查输出目录权限后重试。") from exc
        raise RenderError("OUTPUT_TEMP_FAILED", "命令自有临时文件名已全部被占用。", "清理冲突的 renderer 临时文件后重试。")

    def stage_markdown(self, payload: bytes) -> None:
        file_descriptor, _ = self._create_temporary("markdown")
        try:
            view = memoryview(payload)
            while view:
                written = os.write(file_descriptor, view)
                if written <= 0:
                    raise OSError("short write")
                view = view[written:]
            os.fsync(file_descriptor)
        except OSError as exc:
            raise RenderError("OUTPUT_TEMP_FAILED", "无法完整暂存 Markdown bytes。", "检查可用空间和目录权限后重试。") from exc

    def reserve_pptx(self) -> BinaryIO:
        owner_fd, _ = self._create_temporary("pptx")
        duplicate = os.fdopen(os.dup(owner_fd), "w+b")
        duplicate_status = os.fstat(duplicate.fileno())
        owner_status = os.fstat(owner_fd)
        if ((duplicate_status.st_dev, duplicate_status.st_ino)
                != (owner_status.st_dev, owner_status.st_ino)):
            duplicate.close()
            raise RenderError("OUTPUT_TEMP_FAILED", "PPTX duplicate descriptor 身份不一致。", "改用兼容运行时后重试。")
        return duplicate

    def assert_temporary(self, kind: str) -> None:
        assert self.root_fd is not None
        name, identity, owner_fd = self.temporary[kind]
        try:
            result = os.stat(name, dir_fd=self.root_fd, follow_symlinks=False)
        except OSError as exc:
            raise RenderError("OUTPUT_TEMP_CHANGED", "命令自有临时文件在渲染期间被替换。", "检查输出目录安全后重试。") from exc
        held = os.fstat(owner_fd)
        if ((held.st_dev, held.st_ino) != identity or not stat.S_ISREG(result.st_mode)
                or (result.st_dev, result.st_ino) != identity):
            raise RenderError("OUTPUT_TEMP_CHANGED", "命令自有临时文件在渲染期间被替换。", "检查输出目录安全后重试。")

    def publish(self) -> tuple[Path, Path]:
        assert self.root_fd is not None
        self.assert_root_identity()
        self.assert_final_paths()
        self.assert_temporary("markdown")
        self.assert_temporary("pptx")
        if RENDER_PRE_PUBLISH_HOOK is not None:
            try:
                RENDER_PRE_PUBLISH_HOOK(self.output_root)
            except Exception as exc:
                raise RenderError("OUTPUT_PUBLISH_INTERRUPTED", "PPTX 发布前故障注入已中止提交。", "排除发布故障后重试。") from exc
        self.assert_root_identity()
        self.assert_final_paths()
        markdown_temp = self.temporary["markdown"][0]
        pptx_temp = self.temporary["pptx"][0]
        os.replace(markdown_temp, self.final_names["markdown"], src_dir_fd=self.root_fd, dst_dir_fd=self.root_fd)
        if RENDER_BETWEEN_REPLACE_HOOK is not None:
            try:
                RENDER_BETWEEN_REPLACE_HOOK(self.output_root)
            except Exception as exc:
                raise RenderError(
                    "OUTPUT_PAIR_INTERRUPTED",
                    "Markdown 已替换，但 PPTX-last 提交被中止；旧 PPTX 保持不变。",
                    "重新运行 render 完成 PPTX-last 提交。",
                ) from exc
        self.assert_root_identity()
        self.assert_final_paths()
        self.assert_temporary("pptx")
        os.replace(pptx_temp, self.final_names["pptx"], src_dir_fd=self.root_fd, dst_dir_fd=self.root_fd)
        os.fsync(self.root_fd)
        return self.output_root / self.final_names["markdown"], self.output_root / self.final_names["pptx"]

    def close(self) -> None:
        if self.root_fd is not None:
            for name, identity, owner_fd in tuple(self.temporary.values()):
                try:
                    result = os.stat(name, dir_fd=self.root_fd, follow_symlinks=False)
                    if stat.S_ISREG(result.st_mode) and (result.st_dev, result.st_ino) == identity:
                        os.unlink(name, dir_fd=self.root_fd)
                except OSError:
                    pass
                try:
                    os.close(owner_fd)
                except OSError:
                    pass
            self.temporary.clear()
            try:
                os.close(self.root_fd)
            except OSError:
                pass
            self.root_fd = None

    def __exit__(self, exc_type, exc, traceback) -> None:
        self.close()


def safe_document_for_pagination(document: dict[str, Any], manifest: dict[str, Any]) -> dict[str, Any]:
    """Keep canonical parsed content while replacing only unsafe layout dispatch values."""
    safe = copy.deepcopy(document)
    layouts = manifest.get("layouts", {})
    for slide in safe.get("logical_slides", ()):
        layout = slide.get("layout")
        specification = layouts.get(layout) if isinstance(layout, str) else None
        if not isinstance(specification, dict) or specification.get("markdown_controllable") is False:
            slide["layout"] = "title-content"
    return safe


def parser_diagnostic(item: dict[str, Any]) -> dict[str, Any]:
    result = dict(item)
    result.setdefault("path", "<input>")
    result.setdefault("line", 1)
    result.setdefault("column", 1)
    result.setdefault("code", "RENDER_INPUT_INVALID")
    result.setdefault("message", "输入存在异常。")
    result.setdefault("fix", "修复 Markdown 后重新渲染。")
    return result


def affected_slides(document: dict[str, Any], errors: list[dict[str, Any]], plan_errors: list[Any]) -> list[str]:
    titles: list[str] = []
    logical = document.get("logical_slides", ())
    for item in errors:
        value = item.get("slide")
        if not value or value == "unknown":
            line = int(item.get("line", 1))
            candidates = [slide for slide in logical if int(slide.get("source_line", 1)) <= line]
            if candidates:
                value = candidates[-1].get("title")
        if value and value != "unknown" and value not in titles:
            titles.append(str(value))
    for item in plan_errors:
        for index in item.logical_indices:
            if 0 <= index < len(logical):
                title = str(logical[index].get("title") or f"逻辑页 {index + 1}")
                if title not in titles:
                    titles.append(title)
    return titles or ["unknown"]


def print_unrecoverable(error: RenderError) -> None:
    print("渲染失败")
    print(f"未替换现有 PPTX：[{error.code}] {error.message}")
    print(f"修复：{error.fix}")
    print("请按提示修复后重新运行 render。")


def render_command(args: argparse.Namespace) -> int:
    input_path = Path(args.input)
    output_root = Path(os.path.abspath(args.out_dir))
    stem = args.stem if args.stem is not None else input_path.stem
    try:
        stem = validate_stem(stem)
        try:
            raw_markdown = input_path.read_bytes()
        except OSError as exc:
            raise RenderError("INPUT_UNREADABLE", "输入 Markdown 不存在或不可读取。", "提供可读取的普通 Markdown 文件。") from exc
        manifest = load_manifest(Path(args.skill_dir))
        document = parse_document(input_path, manifest)
        safe_document = safe_document_for_pagination(document, manifest)
        plan = build_deck_plan(safe_document, manifest)
        frozen_projection = plan.to_projection()
        if RENDER_POST_PARSE_HOOK is not None:
            RENDER_POST_PARSE_HOOK(input_path)
        parser_errors = [parser_diagnostic(item) for item in document.get("errors", ())]
        plan_errors = [item for item in plan.diagnostics if item.severity == "error"]
        warnings = list(document.get("warnings", ())) + [item for item in plan.diagnostics if item.severity == "warning"]
        template_path = Path(args.skill_dir) / "templates" / "standard-school.pptx"
        assets = managed_asset_references(raw_markdown)
        spec = DeliverySpec(output_root, stem, assets)
        with DeliverySession(spec) as session:
            with SecureRenderDestination(session.candidate_root, stem, input_path) as destination:
                destination.stage_markdown(raw_markdown)
                with destination.reserve_pptx() as staged_pptx:
                    if RENDER_PRE_SAVE_HOOK is not None:
                        RENDER_PRE_SAVE_HOOK(destination, staged_pptx)
                    emit_evidence = emit_deck(plan, manifest, template_path, staged_pptx, media_root=input_path.parent)
                    if plan.to_projection() != frozen_projection:
                        raise RenderError("PPTX_PLAN_MUTATED", "发射阶段修改了冻结物理计划。", "检查 renderer 实现后重试。")
                    destination.assert_temporary("pptx")
                    if RENDER_PRE_VALIDATE_HOOK is not None:
                        try:
                            RENDER_PRE_VALIDATE_HOOK(staged_pptx)
                        except Exception as exc:
                            raise RenderError("PPTX_STAGED_INTERRUPTED", "staged PPTX 校验前故障注入已中止渲染。", "排除 staged 故障后重试。") from exc
                    validate_staged_package(staged_pptx, expected_slides=len(plan.slides))
                destination.assert_temporary("pptx")
                destination.publish()
            session.stage_assets(input_path.parent)
            runtime_errors = list(emit_evidence.get("runtime_diagnostics", ()))
            affected = affected_slides(document, [*parser_errors, *runtime_errors], plan_errors)
            if parser_errors or plan_errors or runtime_errors:
                print("渲染完成但输入存在异常")
                print("本次渲染不成功，命令退出码非零；best-effort deck 未发布为 current。")
                print(f"输入 Markdown：{input_path}")
                print(f"主题：{document.get('metadata', {}).get('theme') or manifest.get('theme_id') or '-'}")
                print(f"错误：{len(parser_errors) + len(plan_errors) + len(runtime_errors)}；警告：{len(warnings)}")
                print(f"受影响逻辑页：{'、'.join(affected)}")
                for item in parser_errors[:MAX_PUBLIC_DIAGNOSTICS]:
                    print_diagnostic(item)
                for item in plan_errors[: max(0, MAX_PUBLIC_DIAGNOSTICS - len(parser_errors))]:
                    print(f"{input_path}:{item.source_line}:1 [{item.code}] {item.message}")
                    print(f"  slide: {','.join(map(str, item.logical_indices)) or 'unknown'}")
                    print("  layout: unknown")
                    print(f"  fix: {item.fix}")
                remaining = max(0, MAX_PUBLIC_DIAGNOSTICS - len(parser_errors) - len(plan_errors))
                for item in runtime_errors[:remaining]:
                    print(f"{input_path}:{item['source_line']}:1 [{item['code']}] {item['message']}")
                    print(f"  slide: {','.join(map(str, item['logical_indices']))}")
                    print("  layout: unknown")
                    print(f"  fix: {item['fix']}")
                print("异常 Markdown/PPTX 仅作为本次 owned work evidence，收尾时清理。")
                print("请修正 Markdown 后重新渲染；PowerPoint/WPS 视觉验收仍需人工完成。")
                return 1
            publication = session.publish(expected_slides=len(plan.slides))
        markdown_output = output_root / f"{stem}.md"
        pptx_output = output_root / f"{stem}.pptx"
        print("渲染成功")
        print(f"输入 Markdown：{input_path}")
        print(f"主题：{document.get('metadata', {}).get('theme') or manifest.get('theme_id') or '-'}")
        print(f"逻辑页：{len(document.get('logical_slides', ()))}；物理页：{len(plan.slides)}")
        print(f"分页摘要：{len(plan.logical_to_physical)} 个逻辑映射；transition mode：none")
        print(f"Markdown：{markdown_output}")
        print(f"PPTX：{pptx_output}")
        print(f"发布结果：{publication}")
        print("校验结果：PASS")
        return 0
    except ManifestError as exc:
        print_unrecoverable(RenderError(exc.code, str(exc), "修复或恢复 canonical manifest 后重试。"))
        return 1
    except PptxEmitError as exc:
        print_unrecoverable(RenderError(exc.code, exc.message, "检查依赖、受控模板和 staged package 后重试。"))
        return 1
    except RenderError as exc:
        print_unrecoverable(exc)
        return 1
    except (KeyError, TypeError, ValueError, OSError) as exc:
        del exc
        print_unrecoverable(RenderError("PPTX_RENDER_FAILED", "渲染状态机遇到不可恢复的受控错误。", "检查输入、模板和输出目录后重试。"))
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="pptx_render.py", description="school-pptx render command")
    parser.add_argument("skill_dir", nargs="?", default=str(Path(__file__).resolve().parent.parent))
    parser.add_argument("--input", required=True)
    parser.add_argument("--out-dir", required=True)
    parser.add_argument("--stem")
    return parser


def main(argv: list[str] | None = None) -> int:
    return render_command(build_parser().parse_args(argv))


if __name__ == "__main__":
    raise SystemExit(main())
