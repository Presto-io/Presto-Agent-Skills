"""Candidate-first three-theme Markdown/Typst/PDF render matrix."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable, Mapping

from graduate_resume_cli import CliError
from graduate_resume_final_markdown import emit_final_markdown, load_final_resume
from graduate_resume_layout import (
    PhotoAsset, THEME_SPECS, build_frozen_resume_plan, resolve_theme,
    selected_fact_view, validate_font_manifest,
)
from graduate_resume_targeting import VersionProjection
from graduate_resume_typst import emit_typst, normalize_photo_bytes

RENDER_INPUT_INVALID = "RENDER_INPUT_INVALID"
RENDER_STEM_COLLISION = "RENDER_STEM_COLLISION"
RENDER_MATRIX_FAILED = "RENDER_MATRIX_FAILED"
THEME_KEYS = ("conservative", "modern", "expressive")
_SAFE_RE = re.compile(r"[^\w\u3400-\u9fff-]+", re.UNICODE)


@dataclass(frozen=True, slots=True)
class RenderItem:
    version_id: str
    theme_key: str
    theme_label: str
    stem: str


@dataclass(frozen=True, slots=True)
class RenderMatrix:
    items: tuple[RenderItem, ...]
    candidate_root: Path | None = None
    publishable: bool = False

    @property
    def managed_files(self) -> tuple[str, ...]:
        return tuple(f"{item.stem}{suffix}" for item in self.items for suffix in (".md", ".typ", ".pdf"))


def safe_component(value: str, *, max_length: int = 48) -> str:
    if not isinstance(value, str):
        raise CliError(RENDER_INPUT_INVALID, "文件名组件无效。")
    normalized = unicodedata.normalize("NFKC", value)
    normalized = "".join("-" if char.isspace() or char in "/\\:|" else char for char in normalized if unicodedata.category(char) != "Cc")
    normalized = _SAFE_RE.sub("-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-_.")
    if not normalized:
        raise CliError(RENDER_INPUT_INVALID, "文件名组件规范化后为空。")
    if len(normalized) > max_length:
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:10]
        normalized = normalized[: max_length - 11].rstrip("-_.") + "-" + digest
    return normalized


def build_stem(candidate_name: str, theme_key: str, *, company: str | None = None, role: str | None = None) -> str:
    if theme_key not in THEME_SPECS:
        raise CliError(RENDER_INPUT_INVALID, "登记主题无效。")
    name = safe_component(candidate_name)
    theme = safe_component(THEME_SPECS[theme_key].label)
    if company is None and role is None:
        return f"{name}简历-通用-{theme}"
    if not company or not role:
        raise CliError(RENDER_INPUT_INVALID, "定向文件名必须同时包含单位和岗位。")
    return f"{name}简历-{safe_component(company)}-{safe_component(role)}-{theme}"


def _projection_items(value: VersionProjection | Iterable[VersionProjection]) -> tuple[VersionProjection, ...]:
    if isinstance(value, VersionProjection):
        return (value,)
    items = tuple(value)
    if not items or any(not isinstance(item, VersionProjection) for item in items):
        raise CliError(RENDER_INPUT_INVALID, "版本投影集合无效。")
    return items


def build_render_matrix(
    candidate_name: str, projections: VersionProjection | Iterable[VersionProjection],
    *, targets: Mapping[str, Mapping[str, Any]] | None = None,
) -> RenderMatrix:
    items: list[RenderItem] = []
    for projection in _projection_items(projections):
        target = None if projection.target_id is None else (targets or {}).get(projection.target_id)
        if projection.target_id is not None and target is None:
            raise CliError(RENDER_INPUT_INVALID, "定向矩阵缺少单位和岗位显示信息。")
        for theme_key in THEME_KEYS:
            stem = build_stem(
                candidate_name, theme_key,
                company=None if target is None else str(target.get("company") or ""),
                role=None if target is None else str(target.get("role") or ""),
            )
            items.append(RenderItem(projection.version_id, theme_key, THEME_SPECS[theme_key].label, stem))
    stems = [item.stem for item in items]
    if len(stems) != len(set(stems)):
        raise CliError(RENDER_STEM_COLLISION, "规范化文件名发生碰撞。")
    return RenderMatrix(tuple(items))


def _compile_typst(typst_path: Path, pdf_path: Path, fonts_root: Path) -> None:
    completed = subprocess.run(
        ["typst", "compile", "--font-path", str(fonts_root), "--ignore-system-fonts", "--creation-timestamp", "0", str(typst_path), str(pdf_path)],
        cwd=typst_path.parent, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    if completed.returncode or not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise CliError(RENDER_MATRIX_FAILED, "Typst/PDF 候选编译失败。")


def render_candidate_matrix(
    candidate_root: Path | str, facts: Mapping[str, Any], projection: VersionProjection, *,
    canonical_hash: str, target: Mapping[str, Any] | None = None,
    photo_bytes: bytes | None = None, font_manifest_hash: str | None = None,
    fail_theme: str | None = None,
) -> RenderMatrix:
    root = Path(candidate_root)
    if root.exists() and any(root.iterdir()):
        raise CliError(RENDER_INPUT_INVALID, "候选目录必须为空或不存在。")
    candidate = facts.get("candidate")
    if not isinstance(candidate, Mapping) or not isinstance(candidate.get("name"), str):
        raise CliError(RENDER_INPUT_INVALID, "候选人姓名缺失。")
    targets = None if target is None else {str(target.get("id")): target}
    matrix = build_render_matrix(candidate["name"], projection, targets=targets)
    skill_root = Path(__file__).resolve().parent.parent
    fonts_root = skill_root / "fonts"
    font_hash = font_manifest_hash or validate_font_manifest(fonts_root)
    view = selected_fact_view(facts, projection.selected_fact_ids)
    photo_mode = "photo" if photo_bytes is not None else "no-photo"
    normalized_photo = None if photo_bytes is None else normalize_photo_bytes(photo_bytes)
    photo = None if normalized_photo is None else PhotoAsset("embedded-normalized.png")
    root.parent.mkdir(parents=True, exist_ok=True)
    evidence_root = root.parent / ".render-evidence"
    evidence_root.mkdir(exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="matrix-", dir=root.parent))
    try:
        evidence = {"projection": projection.to_projection(), "themes": []}
        for item in matrix.items:
            if fail_theme == item.theme_key:
                raise CliError(RENDER_MATRIX_FAILED, "注入的主题渲染失败。")
            plan = build_frozen_resume_plan(view, resolve_theme(item.theme_key), photo_mode, photo, font_hash, projection.requested_pages)
            md_path = stage / f"{item.stem}.md"
            md_path.write_bytes(emit_final_markdown(
                facts, projection, canonical_hash=canonical_hash, theme_key=item.theme_key,
                theme_label=item.theme_label, page_count=plan.page_count, photo_mode=photo_mode, target=target,
            ))
            final = load_final_resume(md_path)
            if normalized_photo is not None:
                final = dataclasses.replace(final, normalized_photo_png=normalized_photo)
            reparsed_plan = build_frozen_resume_plan(final.fact_view(), resolve_theme(item.theme_key), photo_mode, photo, font_hash, projection.requested_pages)
            if reparsed_plan.page_count != final.page_count:
                raise CliError(RENDER_MATRIX_FAILED, "最终 Markdown 重读后的布局漂移。")
            typ_path = stage / f"{item.stem}.typ"
            typ_path.write_text(emit_typst(reparsed_plan, final), encoding="utf-8")
            pdf_path = stage / f"{item.stem}.pdf"
            _compile_typst(typ_path, pdf_path, fonts_root)
            evidence["themes"].append({"theme": item.theme_key, "page_count": plan.page_count, "comparison_pages": plan.recommendation.comparison_pages})
        actual = {path.name for path in stage.iterdir() if path.is_file()}
        if actual != set(matrix.managed_files) or any((stage / name).stat().st_size == 0 for name in actual):
            raise CliError(RENDER_MATRIX_FAILED, "候选三件套集合不完整。")
        root.mkdir(exist_ok=True)
        for name in matrix.managed_files:
            os.replace(stage / name, root / name)
        (evidence_root / f"{projection.version_id}.json").write_text(
            json.dumps(evidence, ensure_ascii=False, sort_keys=True, separators=(",", ":")), encoding="utf-8"
        )
        return RenderMatrix(matrix.items, root, True)
    except Exception:
        if root.exists():
            for path in root.iterdir():
                if path.is_file() and path.name in matrix.managed_files:
                    path.unlink()
        raise
    finally:
        shutil.rmtree(stage, ignore_errors=True)


__all__ = [
    "RenderItem", "RenderMatrix", "build_render_matrix", "build_stem",
    "render_candidate_matrix", "safe_component",
]
