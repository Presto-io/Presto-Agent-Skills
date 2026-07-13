#!/usr/bin/env python3
"""Render canonical school-pptx Markdown and publish a safe dual artifact pair."""

from __future__ import annotations

import argparse
import copy
import inspect
import os
import stat
import sys
from pathlib import Path
from typing import Any, Callable

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
RENDER_PRE_PUBLISH_HOOK: Callable[[Path], None] | None = None
RENDER_BETWEEN_REPLACE_HOOK: Callable[[Path], None] | None = None


class RenderError(RuntimeError):
    """Bounded public render failure."""

    def __init__(self, code: str, message: str, fix: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.fix = fix


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
        self.temporary: dict[str, tuple[str, tuple[int, int]]] = {}
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
                file_descriptor = os.open(
                    name,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                    0o600,
                    dir_fd=self.root_fd,
                )
                created = os.fstat(file_descriptor)
                self.temporary[kind] = (name, (created.st_dev, created.st_ino))
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
        finally:
            os.close(file_descriptor)

    def reserve_pptx(self) -> Path:
        file_descriptor, name = self._create_temporary("pptx")
        os.close(file_descriptor)
        return self.output_root / name

    def assert_temporary(self, kind: str) -> None:
        assert self.root_fd is not None
        name, identity = self.temporary[kind]
        try:
            result = os.stat(name, dir_fd=self.root_fd, follow_symlinks=False)
        except OSError as exc:
            raise RenderError("OUTPUT_TEMP_CHANGED", "命令自有临时文件在渲染期间被替换。", "检查输出目录安全后重试。") from exc
        if not stat.S_ISREG(result.st_mode) or (result.st_dev, result.st_ino) != identity:
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
        del self.temporary["markdown"]
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
        del self.temporary["pptx"]
        os.fsync(self.root_fd)
        return self.output_root / self.final_names["markdown"], self.output_root / self.final_names["pptx"]

    def close(self) -> None:
        if self.root_fd is not None:
            for name, identity in tuple(self.temporary.values()):
                try:
                    result = os.stat(name, dir_fd=self.root_fd, follow_symlinks=False)
                    if stat.S_ISREG(result.st_mode) and (result.st_dev, result.st_ino) == identity:
                        os.unlink(name, dir_fd=self.root_fd)
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
        parser_errors = [parser_diagnostic(item) for item in document.get("errors", ())]
        plan_errors = [item for item in plan.diagnostics if item.severity == "error"]
        warnings = list(document.get("warnings", ())) + [item for item in plan.diagnostics if item.severity == "warning"]
        template_path = Path(args.skill_dir) / "templates" / "standard-school.pptx"
        with SecureRenderDestination(output_root, stem, input_path) as destination:
            destination.stage_markdown(raw_markdown)
            staged_pptx = destination.reserve_pptx()
            emit_deck(plan, manifest, template_path, staged_pptx, media_root=input_path.parent)
            destination.assert_temporary("pptx")
            if RENDER_PRE_VALIDATE_HOOK is not None:
                try:
                    RENDER_PRE_VALIDATE_HOOK(staged_pptx)
                except Exception as exc:
                    raise RenderError("PPTX_STAGED_INTERRUPTED", "staged PPTX 校验前故障注入已中止渲染。", "排除 staged 故障后重试。") from exc
            validate_staged_package(staged_pptx, expected_slides=len(plan.slides))
            destination.assert_temporary("pptx")
            markdown_output, pptx_output = destination.publish()
        affected = affected_slides(document, parser_errors, plan_errors)
        if parser_errors or plan_errors:
            print("渲染完成但输入存在异常")
            print("本次渲染不成功，命令退出码非零。")
            print(f"输入 Markdown：{input_path}")
            print(f"主题：{document.get('metadata', {}).get('theme') or manifest.get('theme_id') or '-'}")
            print(f"错误：{len(parser_errors) + len(plan_errors)}；警告：{len(warnings)}")
            print(f"受影响逻辑页：{'、'.join(affected)}")
            for item in parser_errors[:MAX_PUBLIC_DIAGNOSTICS]:
                print_diagnostic(item)
            for item in plan_errors[: max(0, MAX_PUBLIC_DIAGNOSTICS - len(parser_errors))]:
                print(f"{input_path}:{item.source_line}:1 [{item.code}] {item.message}")
                print(f"  slide: {','.join(map(str, item.logical_indices)) or 'unknown'}")
                print("  layout: unknown")
                print(f"  fix: {item.fix}")
            print(f"Markdown：{markdown_output}")
            print(f"异常 PPTX：{pptx_output}")
            print("请修正 Markdown 后重新渲染覆盖，或在自动工作流结束后手工修改可编辑 PPTX。")
            return 1
        print("渲染成功")
        print(f"输入 Markdown：{input_path}")
        print(f"主题：{document.get('metadata', {}).get('theme') or manifest.get('theme_id') or '-'}")
        print(f"逻辑页：{len(document.get('logical_slides', ()))}；物理页：{len(plan.slides)}")
        print(f"分页摘要：{len(plan.logical_to_physical)} 个逻辑映射；transition mode：none")
        print(f"Markdown：{markdown_output}")
        print(f"PPTX：{pptx_output}")
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
