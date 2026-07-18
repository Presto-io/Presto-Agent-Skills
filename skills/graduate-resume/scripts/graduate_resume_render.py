"""Candidate-first three-theme Markdown/Typst/PDF render matrix."""

from __future__ import annotations

import dataclasses
import hashlib
import json
import os
import re
import shutil
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
from graduate_resume_typst_runtime import TypstExecutable

RENDER_INPUT_INVALID = "RENDER_INPUT_INVALID"
RENDER_STEM_COLLISION = "RENDER_STEM_COLLISION"
RENDER_MATRIX_FAILED = "RENDER_MATRIX_FAILED"
THEME_KEYS = ("conservative", "modern", "expressive")
_SAFE_RE = re.compile(r"[^\w\u3400-\u9fff-]+", re.UNICODE)
_EVIDENCE_NAME_RE = re.compile(r"evidence-[0-9a-f]{64}-[0-9a-f]{64}-[0-9a-f]{64}\.json")
_HEX64_RE = re.compile(r"[0-9a-f]{64}")
_EMAIL_RE = re.compile(r"(?i)[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}")
_PHONE_RE = re.compile(r"(?<!\d)(?:\+\d{1,3}(?:[- ]?\d){7,14}|(?:\+?\d{1,3}[- ]?)?(?:1[3-9]\d{9}|0\d{2,3}[- ]?\d{7,8}))(?!\d)")
_ID_CARD_RE = re.compile(r"(?<!\d)(?:\d{15}|\d{17}[0-9Xx])(?!\d)")
_URL_RE = re.compile(r"(?i)[a-z][a-z0-9+.-]*://")


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _canonical_root(path: Path | str) -> Path:
    candidate = Path(path).expanduser()
    absolute = Path(os.path.abspath(os.path.normpath(os.fspath(candidate))))
    try:
        parent = absolute.parent.resolve(strict=True)
    except OSError as exc:
        raise CliError(RENDER_INPUT_INVALID, "证据根父目录不存在或不安全。") from exc
    return parent / absolute.name


def _open_root_no_follow(path: Path, *, create: bool) -> int:
    if not path.is_absolute():
        raise CliError(RENDER_INPUT_INVALID, "证据根授权路径无效。")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(path.anchor, flags)
    try:
        for index, component in enumerate(path.parts[1:]):
            try:
                child = os.open(component, flags, dir_fd=descriptor)
            except FileNotFoundError:
                if not create or index != len(path.parts[1:]) - 1:
                    raise
                os.mkdir(component, 0o700, dir_fd=descriptor)
                child = os.open(component, flags, dir_fd=descriptor)
            os.close(descriptor)
            descriptor = child
        return descriptor
    except Exception:
        os.close(descriptor)
        raise


class EvidenceSink:
    """Caller-authorized, no-follow persistent sink for private condition evidence."""

    def __init__(self, root: Path | str, *, delivery_root: Path | str | None = None, create: bool = True) -> None:
        self.path = _canonical_root(root)
        self.delivery_path = None if delivery_root is None else _canonical_root(delivery_root)
        self.create = create
        self._descriptor: int | None = None
        self.identity: tuple[int, int] | None = None

    def __enter__(self) -> "EvidenceSink":
        if self.delivery_path is not None:
            evidence = self.path.parts
            delivery = self.delivery_path.parts
            if evidence == delivery or evidence[: len(delivery)] == delivery or delivery[: len(evidence)] == evidence:
                raise CliError(RENDER_INPUT_INVALID, "隐藏证据根必须与正式投递根完全分离。")
        try:
            self._descriptor = _open_root_no_follow(self.path, create=self.create)
            stat = os.fstat(self._descriptor)
            if not stat.st_mode & 0o040000:
                raise OSError
            self.identity = (stat.st_dev, stat.st_ino)
            self._inspect_existing()
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as exc:
            self.close()
            raise CliError(RENDER_INPUT_INVALID, "隐藏证据根包含未知、不完整或不安全节点。") from exc
        return self

    def close(self) -> None:
        if self._descriptor is not None:
            os.close(self._descriptor)
            self._descriptor = None

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self.close()

    @property
    def descriptor(self) -> int:
        if self._descriptor is None:
            raise CliError(RENDER_INPUT_INVALID, "隐藏证据根尚未打开。")
        return self._descriptor

    def assert_identity(self) -> None:
        try:
            current = _open_root_no_follow(self.path, create=False)
            try:
                stat = os.fstat(current)
                identity = (stat.st_dev, stat.st_ino)
            finally:
                os.close(current)
        except OSError as exc:
            raise CliError(RENDER_INPUT_INVALID, "隐藏证据根身份已变化。") from exc
        if identity != self.identity:
            raise CliError(RENDER_INPUT_INVALID, "隐藏证据根身份已变化。")

    @staticmethod
    def _validate_payload(payload: Any) -> None:
        if not isinstance(payload, dict) or set(payload) != {
            "canonical_hash", "projection_digest", "condition_digest", "condition_evidence"
        }:
            raise ValueError
        if any(not isinstance(payload[key], str) or not _HEX64_RE.fullmatch(payload[key]) for key in (
            "canonical_hash", "projection_digest", "condition_digest"
        )):
            raise ValueError
        evidence = payload["condition_evidence"]
        if not isinstance(evidence, dict) or set(evidence) != {
            "target_id", "matrix", "counts", "warnings", "gap_allowed", "evidence_digest"
        }:
            raise ValueError
        digest_payload = {key: value for key, value in evidence.items() if key != "evidence_digest"}
        if evidence["evidence_digest"] != payload["condition_digest"] or hashlib.sha256(_json_bytes(digest_payload)).hexdigest() != payload["condition_digest"]:
            raise ValueError

    def _read(self, name: str) -> bytes:
        flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(name, flags, dir_fd=self.descriptor)
        try:
            stat = os.fstat(descriptor)
            if not stat.st_mode & 0o100000 or stat.st_size <= 0:
                raise OSError
            chunks: list[bytes] = []
            while True:
                chunk = os.read(descriptor, 65536)
                if not chunk:
                    break
                chunks.append(chunk)
            return b"".join(chunks)
        finally:
            os.close(descriptor)

    def _inspect_existing(self) -> None:
        for name in sorted(os.listdir(self.descriptor)):
            if not _EVIDENCE_NAME_RE.fullmatch(name):
                raise ValueError
            raw = self._read(name)
            payload = json.loads(raw)
            self._validate_payload(payload)
            if raw != _json_bytes(payload):
                raise ValueError

    def persist(self, *, canonical_hash: str, projection: VersionProjection, condition_evidence: Mapping[str, Any]) -> str:
        evidence = dict(condition_evidence)
        payload = {
            "canonical_hash": canonical_hash,
            "projection_digest": projection.digest,
            "condition_digest": projection.condition_digest,
            "condition_evidence": evidence,
        }
        self._validate_payload(payload)
        if (
            evidence["target_id"] != projection.target_id
            or evidence["counts"] != dict(projection.condition_summary)
            or evidence["gap_allowed"] is not projection.gap_allowed
        ):
            raise CliError(RENDER_INPUT_INVALID, "条件证据与版本投影不一致。")
        name = f"evidence-{canonical_hash}-{projection.digest}-{projection.condition_digest}.json"
        if not _EVIDENCE_NAME_RE.fullmatch(name):
            raise CliError(RENDER_INPUT_INVALID, "条件证据文件名无效。")
        raw = _json_bytes(payload)
        try:
            existing = self._read(name)
        except FileNotFoundError:
            existing = None
        if existing is not None:
            if existing == raw:
                return name
            raise CliError(RENDER_INPUT_INVALID, "同名条件证据与既有绑定冲突。")
        temporary = f".evidence-work-{os.getpid()}-{hashlib.sha256(raw).hexdigest()[:16]}"
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(temporary, flags, 0o600, dir_fd=self.descriptor)
        try:
            offset = 0
            while offset < len(raw):
                offset += os.write(descriptor, raw[offset:])
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        renamed = False
        try:
            os.rename(temporary, name, src_dir_fd=self.descriptor, dst_dir_fd=self.descriptor)
            renamed = True
            os.fsync(self.descriptor)
            self.assert_identity()
        except BaseException:
            if renamed:
                try:
                    os.unlink(name, dir_fd=self.descriptor)
                    os.fsync(self.descriptor)
                except OSError:
                    pass
            raise
        return name

    def persist_many(
        self,
        records: Iterable[tuple[str, VersionProjection, Mapping[str, Any]]],
    ) -> tuple[str, ...]:
        """Persist one publication's evidence and remove its new files on failure."""
        created: list[str] = []
        names: list[str] = []
        try:
            for canonical_hash, projection, condition_evidence in records:
                name = (
                    f"evidence-{canonical_hash}-{projection.digest}-{projection.condition_digest}.json"
                )
                try:
                    self._read(name)
                    existed = True
                except FileNotFoundError:
                    existed = False
                names.append(self.persist(
                    canonical_hash=canonical_hash,
                    projection=projection,
                    condition_evidence=condition_evidence,
                ))
                if not existed:
                    created.append(name)
        except BaseException:
            for name in reversed(created):
                try:
                    os.unlink(name, dir_fd=self.descriptor)
                except FileNotFoundError:
                    pass
            if created:
                os.fsync(self.descriptor)
            raise
        return tuple(names)


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


def _reject_sensitive_component(value: str) -> None:
    if _EMAIL_RE.search(value) or _PHONE_RE.search(value) or _ID_CARD_RE.search(value) or _URL_RE.search(value):
        raise CliError(RENDER_INPUT_INVALID, "文件名组件包含禁止的敏感标识。")


def safe_component(value: str, *, max_bytes: int = 48) -> str:
    if not isinstance(value, str):
        raise CliError(RENDER_INPUT_INVALID, "文件名组件无效。")
    normalized = unicodedata.normalize("NFKC", value)
    _reject_sensitive_component(normalized)
    normalized = "".join("-" if char.isspace() or char in "/\\:|" else char for char in normalized if unicodedata.category(char) != "Cc")
    normalized = _SAFE_RE.sub("-", normalized)
    normalized = re.sub(r"-+", "-", normalized).strip("-_.")
    if not normalized:
        raise CliError(RENDER_INPUT_INVALID, "文件名组件规范化后为空。")
    if max_bytes < 12:
        raise CliError(RENDER_INPUT_INVALID, "文件名组件长度预算无效。")
    if len(normalized.encode("utf-8")) > max_bytes:
        digest = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:10]
        prefix: list[str] = []
        used = 0
        for char in normalized:
            size = len(char.encode("utf-8"))
            if used + size > max_bytes - 11:
                break
            prefix.append(char)
            used += size
        normalized = "".join(prefix).rstrip("-_.") + "-" + digest
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


def _compile_typst(typst_path: Path, pdf_path: Path, fonts_root: Path, typst_executable: TypstExecutable) -> None:
    completed = typst_executable.run(
        ("compile", "--font-path", str(fonts_root), "--ignore-system-fonts", "--creation-timestamp", "0", str(typst_path), str(pdf_path)),
        cwd=typst_path.parent,
    )
    if completed.returncode or not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        raise CliError(RENDER_MATRIX_FAILED, "Typst/PDF 候选编译失败。")


def render_candidate_matrix(
    candidate_root: Path | str, facts: Mapping[str, Any], projection: VersionProjection, *,
    canonical_hash: str, target: Mapping[str, Any] | None = None,
    typst_executable: TypstExecutable, photo_bytes: bytes | None = None,
    font_manifest_hash: str,
    fail_theme: str | None = None,
    condition_evidence: Mapping[str, Any] | None = None,
    evidence_root: Path | str | EvidenceSink | None = None,
    persist_evidence: bool = True,
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
    font_hash = font_manifest_hash
    view = selected_fact_view(facts, projection.selected_fact_ids)
    photo_mode = "photo" if photo_bytes is not None else "no-photo"
    normalized_photo = None if photo_bytes is None else normalize_photo_bytes(photo_bytes, typst_executable)
    photo = None if normalized_photo is None else PhotoAsset("embedded-normalized.png")
    root.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix="matrix-", dir=root.parent))
    try:
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
            _compile_typst(typ_path, pdf_path, fonts_root, typst_executable)
        actual = {path.name for path in stage.iterdir() if path.is_file()}
        if actual != set(matrix.managed_files) or any((stage / name).stat().st_size == 0 for name in actual):
            raise CliError(RENDER_MATRIX_FAILED, "候选三件套集合不完整。")
        root.mkdir(exist_ok=True)
        for name in matrix.managed_files:
            os.replace(stage / name, root / name)
        if projection.target_id is not None and persist_evidence:
            if condition_evidence is None or evidence_root is None:
                raise CliError(RENDER_INPUT_INVALID, "定向渲染必须提供授权隐藏证据根。")
            if isinstance(evidence_root, EvidenceSink):
                evidence_root.persist(
                    canonical_hash=canonical_hash, projection=projection,
                    condition_evidence=condition_evidence,
                )
            else:
                with EvidenceSink(evidence_root) as sink:
                    sink.persist(
                        canonical_hash=canonical_hash, projection=projection,
                        condition_evidence=condition_evidence,
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
    "EvidenceSink", "RenderItem", "RenderMatrix", "build_render_matrix", "build_stem",
    "render_candidate_matrix", "safe_component",
]
