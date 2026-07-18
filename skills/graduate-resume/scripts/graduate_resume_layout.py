"""Immutable, fail-closed layout plans for verified graduate-resume facts."""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import Any

from graduate_resume_cli import CliError

FONT_MANIFEST_INVALID = "FONT_MANIFEST_INVALID"
PHOTO_ASSET_INVALID = "PHOTO_ASSET_INVALID"
THEME_INVALID = "THEME_INVALID"
LAYOUT_UNSATISFIABLE = "LAYOUT_UNSATISFIABLE"
LAYOUT_PLAN_INVALID = "LAYOUT_PLAN_INVALID"
_LIST_SECTIONS = frozenset(("projects", "training", "experience", "certificates"))
_FACT_SECTIONS = frozenset(("candidate", "summary", "education", "skills"))
_SECTION_LABELS = {"candidate": "个人信息", "summary": "个人概述", "education": "教育经历", "skills": "专业技能", "certificates": "证书与资格", "projects": "项目经历", "training": "实训经历", "experience": "相关经历"}


@dataclass(frozen=True, slots=True)
class PhotoFitPolicy:
    photo_fit: str = "contain"
    crop_policy: str = "forbid"
    preserve_aspect_ratio: bool = True
    allow_stretch: bool = False
    allow_controlled_crop: bool = False
    subject_safe_area_contract: str | None = None


@dataclass(frozen=True, slots=True)
class PhotoSlot:
    width_mm: float
    height_mm: float
    position: str


@dataclass(frozen=True, slots=True)
class ThemeSpec:
    key: str
    label: str
    layout: str
    photo_slot: PhotoSlot
    no_photo_behavior: str
    safe_margins_mm: tuple[int, int, int, int]
    column_ratio: tuple[int, int]
    palette: tuple[str, str, str]
    typography_pt: tuple[float, float, float, float]
    spacing_tokens: tuple[str, ...]
    photo_policy: PhotoFitPolicy = PhotoFitPolicy()


@dataclass(frozen=True, slots=True)
class PhotoAsset:
    logical_path: str
    mode: str = "photo"


@dataclass(frozen=True, slots=True)
class ContainerPlan:
    id: str
    kind: str
    section: str
    source_fact_ids: tuple[str, ...]
    fields: tuple[tuple[str, str], ...]
    page_number: int
    height_mm: float

    def to_projection(self) -> dict[str, Any]:
        return {"id": self.id, "kind": self.kind, "section": self.section, "source_fact_ids": list(self.source_fact_ids), "fields": dict(self.fields), "page_number": self.page_number, "height_mm": self.height_mm}


@dataclass(frozen=True, slots=True)
class EntryBudget:
    container_id: str
    source_fact_id: str
    height_mm: float
    atomic: bool = True

    def to_projection(self) -> dict[str, Any]:
        return {"container_id": self.container_id, "source_fact_id": self.source_fact_id, "height_mm": self.height_mm, "atomic": self.atomic}


@dataclass(frozen=True, slots=True)
class PagePlan:
    number: int
    usable_height_mm: float
    used_height_mm: float
    utilization: float
    anchors: tuple[str, ...]
    containers: tuple[str, ...]

    def to_projection(self) -> dict[str, Any]:
        return {"number": self.number, "usable_height_mm": self.usable_height_mm, "used_height_mm": self.used_height_mm, "utilization": self.utilization, "anchors": list(self.anchors), "containers": list(self.containers)}


@dataclass(frozen=True, slots=True)
class PageRecommendation:
    recommended_pages: int
    requested_pages: str
    comparison_pages: int | None
    advisory: str | None

    def to_projection(self) -> dict[str, Any]:
        return {"recommended_pages": self.recommended_pages, "requested_pages": self.requested_pages, "comparison_pages": self.comparison_pages, "advisory": self.advisory}


@dataclass(frozen=True, slots=True)
class FrozenResumePlan:
    theme_key: str
    theme_label: str
    page_preference: str
    page_count: int
    photo_mode: str
    photo: PhotoAsset | None
    photo_fit: str
    crop_policy: str
    preserve_aspect_ratio: bool
    allow_stretch: bool
    allow_controlled_crop: bool
    subject_safe_area_contract: str | None
    photo_slot: PhotoSlot | None
    no_photo_behavior: str
    font_manifest_hash: str
    measurement_version: str
    measurement_hash: str
    pages: tuple[PagePlan, ...]
    containers: tuple[ContainerPlan, ...]
    entry_budget: tuple[EntryBudget, ...]
    reorder_reason: str | None
    recommendation: PageRecommendation

    def to_projection(self) -> dict[str, Any]:
        return {"theme": {"key": self.theme_key, "label": self.theme_label}, "page_count": self.page_count, "page_preference": self.page_preference, "photo_mode": self.photo_mode, "has_photo": self.photo is not None, "photo_policy": {"photo_fit": self.photo_fit, "crop_policy": self.crop_policy, "preserve_aspect_ratio": self.preserve_aspect_ratio, "allow_stretch": self.allow_stretch, "allow_controlled_crop": self.allow_controlled_crop, "subject_safe_area_contract": self.subject_safe_area_contract}, "photo_slot": None if self.photo_slot is None else {"width_mm": self.photo_slot.width_mm, "height_mm": self.photo_slot.height_mm, "position": self.photo_slot.position}, "no_photo_behavior": self.no_photo_behavior, "font_manifest_hash": self.font_manifest_hash, "measurement_version": self.measurement_version, "measurement_hash": self.measurement_hash, "pages": [page.to_projection() for page in self.pages], "containers": [container.to_projection() for container in self.containers], "entry_budget": [budget.to_projection() for budget in self.entry_budget], "reorder_reason": self.reorder_reason, "recommendation": self.recommendation.to_projection()}

    def validate(self, facts: dict[str, Any]) -> None:
        if not all((self.theme_key in THEME_SPECS, self.page_count in (1, 2), self.font_manifest_hash, self.measurement_version, self.measurement_hash, self.pages, self.containers)):
            raise CliError(LAYOUT_PLAN_INVALID, "冻结布局计划缺少必填字段。")
        spec = THEME_SPECS[self.theme_key]
        policy = spec.photo_policy
        if (self.photo_fit, self.crop_policy, self.preserve_aspect_ratio, self.allow_stretch, self.allow_controlled_crop, self.subject_safe_area_contract) != (policy.photo_fit, policy.crop_policy, policy.preserve_aspect_ratio, policy.allow_stretch, policy.allow_controlled_crop, policy.subject_safe_area_contract):
            raise CliError(LAYOUT_PLAN_INVALID, "冻结照片策略与主题不一致。")
        if self.allow_stretch or (self.crop_policy == "controlled" and not self.allow_controlled_crop):
            raise CliError(LAYOUT_PLAN_INVALID, "冻结照片策略不安全。")
        if self.photo_slot and (self.photo_slot.width_mm > 35 or self.photo_slot.height_mm > 49):
            raise CliError(LAYOUT_PLAN_INVALID, "照片槽位超过上限。")
        if self.pages[0].containers[:1] != ("profile",) or "profile" not in self.pages[0].anchors:
            raise CliError(LAYOUT_PLAN_INVALID, "个人信息必须是首页首位锚点。")
        if len(self.pages) != self.page_count or any(page.number != index + 1 for index, page in enumerate(self.pages)):
            raise CliError(LAYOUT_PLAN_INVALID, "页序列无效。")
        ids = {container.id for container in self.containers}
        if any(container_id not in ids for page in self.pages for container_id in page.containers):
            raise CliError(LAYOUT_PLAN_INVALID, "页面引用未知容器。")
        if not isinstance(facts.get("candidate"), dict) or not facts["candidate"].get("name"):
            raise CliError(LAYOUT_PLAN_INVALID, "布局缺少已验证个人信息。")
        known_ids = {"profile"}
        for section in ("education", "skills", "certificates", "projects", "training", "experience"):
            known_ids.update(str(item.get("id")) for item in facts.get(section, ()) if isinstance(item, dict))
        for container in self.containers:
            if any(fact_id not in known_ids for fact_id in container.source_fact_ids):
                raise CliError(LAYOUT_PLAN_INVALID, "布局包含未验证事实。")
        for page in self.pages[1:]:
            if page.containers and not any(container.section in _SECTION_LABELS for container in self.containers if container.id == page.containers[0]):
                raise CliError(LAYOUT_PLAN_INVALID, "续页不得以无标题内容开始。")


_COMMON = {"safe_margins_mm": (14, 14, 15, 15), "typography_pt": (9, 10.5, 14, 22), "spacing_tokens": ("xs", "sm", "md", "lg", "xl"), "photo_policy": PhotoFitPolicy()}
THEME_SPECS = {
    "conservative": ThemeSpec("conservative", "保守稳妥", "single-column-right-photo", PhotoSlot(32, 42, "top-right"), "remove-slot-and-decoration", **_COMMON, column_ratio=(100, 0), palette=("#FFFFFF", "#F2F4F7", "#1F4E79")),
    "modern": ThemeSpec("modern", "现代简洁", "sidebar-photo", PhotoSlot(28, 36, "left-sidebar"), "move-sidebar-content-up", **_COMMON, column_ratio=(31, 69), palette=("#FFFFFF", "#EFF5F4", "#0F766E")),
    "expressive": ThemeSpec("expressive", "个性设计", "header-photo", PhotoSlot(30, 40, "header-right"), "expand-identity-bar", **_COMMON, column_ratio=(38, 62), palette=("#FFFEFA", "#F3F1EA", "#8A6A20")),
}
_ALIASES = {spec.label: key for key, spec in THEME_SPECS.items()}


def resolve_theme(value: str | None) -> ThemeSpec:
    key = _ALIASES.get((value or "conservative").strip(), (value or "conservative").strip())
    if key not in THEME_SPECS:
        raise CliError(THEME_INVALID, "主题必须是 conservative、modern 或 expressive。")
    return THEME_SPECS[key]


def _strings(value: Any) -> tuple[str, ...]:
    if isinstance(value, str): return (value,) if value.strip() else ()
    if isinstance(value, (list, tuple)): return tuple(part for item in value for part in _strings(item))
    if isinstance(value, dict): return tuple(part for item in value.values() for part in _strings(item))
    return ()


def _height(values: tuple[str, ...]) -> float:
    width = 32
    lines = sum(max(1, math.ceil(len(value) / width)) for value in values)
    return round(6.0 + lines * 5.4, 2)


def project_containers(verified_data: dict[str, Any], overrides: dict[str, str] | None = None) -> tuple[ContainerPlan, ...]:
    overrides = overrides or {}
    containers: list[ContainerPlan] = []
    profile = verified_data.get("candidate")
    if not isinstance(profile, dict) or not profile:
        raise CliError(LAYOUT_PLAN_INVALID, "已验证资料缺少个人信息。")
    containers.append(ContainerPlan("profile", "fact-block", "candidate", ("profile",), tuple((key, value) for key, value in profile.items() if isinstance(value, str) and value), 1, _height(_strings(profile))))
    for section in ("education", "skills", "certificates", "projects", "training", "experience"):
        raw = verified_data.get(section, ())
        if not raw: continue
        if section not in _FACT_SECTIONS and section not in _LIST_SECTIONS and section not in overrides:
            continue
        items = raw if isinstance(raw, list) else [raw]
        for index, item in enumerate(items):
            if not isinstance(item, dict): continue
            fact_id = str(item.get("id") or f"{section}-{index + 1}")
            fields = tuple((key, value) for key, value in item.items() if key not in {"id", "status"} and isinstance(value, str) and value)
            if not fields and not _strings(item): continue
            kind = overrides.get(section, "list-entry" if section in _LIST_SECTIONS else "fact-block")
            if kind not in {"fact-block", "list-entry"}: raise CliError(LAYOUT_PLAN_INVALID, "容器覆盖无效。")
            containers.append(ContainerPlan(fact_id, kind, section, (fact_id,), fields, 1, _height(_strings(item))))
    return tuple(containers)


def _measurement(theme_key: str) -> tuple[dict[str, float], str, str]:
    path = Path(__file__).resolve().parent.parent / "templates" / "layout-measurement.json"
    raw = path.read_bytes()
    try:
        payload = json.loads(raw)
        version = payload["measurement_version"]
        values = payload["themes"][theme_key]
        if not isinstance(version, str) or not version or set(values) != {"one_page_clear_max", "one_page_critical_max", "two_page_min_page_utilization", "epsilon_mm"}:
            raise ValueError
        return values, version, hashlib.sha256(raw).hexdigest()
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise CliError(LAYOUT_PLAN_INVALID, "布局测量配置无效。") from exc


def _paginate(containers: tuple[ContainerPlan, ...], count: int, epsilon: float) -> tuple[tuple[ContainerPlan, ...], tuple[PagePlan, ...]]:
    usable = 269.0
    pages: list[list[ContainerPlan]] = [[] for _ in range(count)]
    used = [0.0] * count
    page = 0
    for container in containers:
        if container.height_mm > usable: raise CliError(LAYOUT_UNSATISFIABLE, "单个完整条目超过可读页面边界。")
        if used[page] + container.height_mm > usable:
            page += 1
            if page >= count: raise CliError(LAYOUT_UNSATISFIABLE, "内容无法在请求页数内完整排入。")
        pages[page].append(container)
        used[page] += container.height_mm
    if count == 2 and not pages[1]:
        movable = pages[0][-1:]
        if not movable or movable[0].id == "profile": raise CliError(LAYOUT_UNSATISFIABLE, "无法生成有效第二页。")
        pages[0] = pages[0][:-1]; pages[1] = movable; used[0] -= movable[0].height_mm; used[1] += movable[0].height_mm
    frozen = tuple(tuple(ContainerPlan(item.id, item.kind, item.section, item.source_fact_ids, item.fields, number + 1, item.height_mm) for item in items) for number, items in enumerate(pages))
    plans = tuple(PagePlan(index + 1, usable, round(used[index], 2), (round(used[index], 2) + epsilon) / usable, ("profile",) if index == 0 else (f"section:{frozen[index][0].section}",), tuple(item.id for item in frozen[index])) for index in range(count))
    return frozen, plans


def build_frozen_resume_plan(verified_data: dict[str, Any], theme: ThemeSpec, photo_mode: str, photo: PhotoAsset | None, font_manifest_hash: str, page_preference: str, overrides: dict[str, str] | None = None) -> FrozenResumePlan:
    if page_preference not in {"auto", "1", "2"} or not isinstance(font_manifest_hash, str) or len(font_manifest_hash) != 64:
        raise CliError(LAYOUT_PLAN_INVALID, "冻结布局参数无效。")
    values, version, digest = _measurement(theme.key)
    policy = theme.photo_policy
    if policy.allow_stretch or (policy.crop_policy == "controlled" and not (policy.allow_controlled_crop and policy.subject_safe_area_contract)):
        raise CliError(LAYOUT_PLAN_INVALID, "主题照片策略无效。")
    containers = project_containers(verified_data, overrides)
    one: tuple[tuple[ContainerPlan, ...], tuple[PagePlan, ...]] | None = None
    two: tuple[tuple[ContainerPlan, ...], tuple[PagePlan, ...]] | None = None
    try: one = _paginate(containers, 1, values["epsilon_mm"])
    except CliError: pass
    try: two = _paginate(containers, 2, values["epsilon_mm"])
    except CliError: pass
    if page_preference == "auto":
        if one and one[1][0].utilization <= values["one_page_clear_max"]:
            chosen, recommended, comparison, advisory = one, 1, None, None
        elif not one and two and all(page.utilization >= values["two_page_min_page_utilization"] for page in two[1]):
            chosen, recommended, comparison, advisory = two, 2, None, None
        elif one and one[1][0].utilization <= values["one_page_critical_max"] and two:
            chosen, recommended, comparison, advisory = one, 1, 2, "内容处于临界区，已保留两页对照方案。"
        elif one and two:
            chosen, recommended, comparison, advisory = two, 2, 1, "内容接近单页上限，建议使用两页。"
        elif two:
            chosen, recommended, comparison, advisory = two, 2, None, None
        else: raise CliError(LAYOUT_UNSATISFIABLE, "内容无法在一页或两页可读边界内完整排入。")
    elif page_preference == "1":
        if not one: raise CliError(LAYOUT_UNSATISFIABLE, "强制一页无法保持完整条目与可读边界。")
        chosen, recommended, comparison, advisory = one, 2 if two else 1, 2 if two else None, "已按强制一页生成；建议同时审阅两页对照方案。" if two else None
    else:
        if not two: raise CliError(LAYOUT_UNSATISFIABLE, "强制两页无法保持完整条目与页首规则。")
        chosen, recommended, comparison, advisory = two, 1 if one else 2, 1 if one else None, "已按强制两页生成；内容更适合一页。" if one else None
    flattened = tuple(item for page in chosen[0] for item in page)
    budgets = tuple(EntryBudget(item.id, item.source_fact_ids[0], item.height_mm) for item in flattened if item.kind == "list-entry")
    plan = FrozenResumePlan(theme.key, theme.label, page_preference, len(chosen[1]), "photo" if photo else "no-photo", photo, policy.photo_fit, policy.crop_policy, policy.preserve_aspect_ratio, policy.allow_stretch, policy.allow_controlled_crop, policy.subject_safe_area_contract, theme.photo_slot if photo else None, theme.no_photo_behavior, font_manifest_hash, version, digest, chosen[1], flattened, budgets, "preserved-profile-and-education-front" if len(chosen[1]) == 2 else None, PageRecommendation(recommended, page_preference, comparison, advisory))
    plan.validate(verified_data)
    return plan


# Compatibility entry point retained for the Phase 47-01 theme-only contract.
def build_frozen_plan(theme: ThemeSpec, photo_mode: str, photo: PhotoAsset | None, font_manifest_hash: str, page_preference: str) -> FrozenResumePlan:
    digest = font_manifest_hash if len(font_manifest_hash) == 64 else hashlib.sha256(font_manifest_hash.encode("utf-8")).hexdigest()
    return build_frozen_resume_plan({"candidate": {"name": "已验证候选人"}, "education": []}, theme, photo_mode, photo, digest, page_preference)


def _manifest_error() -> CliError: return CliError(FONT_MANIFEST_INVALID, "受控字体清单无效。")
def _validate_font_visibility(fonts_root: Path, entries: list[dict[str, Any]]) -> None:
    typst = shutil.which("typst")
    if typst is None: raise _manifest_error()
    completed = subprocess.run([typst, "fonts", "--font-path", str(fonts_root), "--ignore-system-fonts", "--variants"], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    output = completed.stdout
    if completed.returncode or "Noto Sans Mono CJK SC" not in output: raise _manifest_error()
    expected = {400: "Weight: 400", 600: "Weight: 700"}
    if any(entry["path"] not in output or expected[entry["weight"]] not in output for entry in entries): raise _manifest_error()
def validate_font_manifest(fonts_root: Path) -> str:
    try:
        manifest = json.loads((fonts_root / "manifest.json").read_text(encoding="utf-8")); entries = manifest["fonts"]
        if manifest["family"] != "Noto Sans Mono CJK SC" or {item["weight"] for item in entries} != {400, 600}: raise ValueError
        digest = hashlib.sha256()
        for item in sorted(entries, key=lambda value: value["weight"]):
            path = fonts_root / PurePosixPath(item["path"])
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != item["sha256"]: raise ValueError
            digest.update(actual.encode("ascii"))
        _validate_font_visibility(fonts_root, entries); return digest.hexdigest()
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError, subprocess.SubprocessError) as exc: raise _manifest_error() from exc
def _photo_error() -> CliError: return CliError(PHOTO_ASSET_INVALID, "照片资源无效。")
def resolve_layout_photo(input_path: Path, assets_root: Path, photo: dict[str, Any], preferences: dict[str, Any]) -> PhotoAsset | None:
    if preferences.get("photo_mode") == "no-photo" or photo.get("status") == "no-photo": return None
    raw = photo.get("path")
    if not isinstance(raw, str) or not raw:
        if preferences.get("photo_mode") == "photo": raise _photo_error()
        return None
    pure = PurePosixPath(raw)
    if pure.is_absolute() or "\\" in raw or ":" in raw or any(part in {"", ".", ".."} for part in raw.split("/")): raise _photo_error()
    try:
        root = assets_root.resolve(strict=True); candidate = root.joinpath(*pure.parts)
        if not candidate.is_file() or candidate.is_symlink() or not candidate.resolve().is_relative_to(root): raise ValueError
        prefix = candidate.read_bytes()[:16]
        if not ((candidate.suffix.lower() in {".jpg", ".jpeg"} and prefix.startswith(b"\xff\xd8")) or (candidate.suffix.lower() == ".png" and prefix.startswith(b"\x89PNG\r\n\x1a\n"))): raise ValueError
    except (OSError, ValueError) as exc: raise _photo_error() from exc
    return PhotoAsset(pure.as_posix())
