"""Immutable, fail-closed layout plans for verified graduate-resume facts."""

from __future__ import annotations

import hashlib
import json
import math
import os
import stat
import subprocess
import tempfile
import unicodedata
from dataclasses import dataclass, replace
from functools import lru_cache
from pathlib import Path, PurePosixPath
from typing import Any, Callable, Mapping

from graduate_resume_cli import CliError
from graduate_resume_typst_runtime import TypstExecutable

FONT_MANIFEST_INVALID = "FONT_MANIFEST_INVALID"
PHOTO_ASSET_INVALID = "PHOTO_ASSET_INVALID"
THEME_INVALID = "THEME_INVALID"
LAYOUT_UNSATISFIABLE = "LAYOUT_UNSATISFIABLE"
LAYOUT_PLAN_INVALID = "LAYOUT_PLAN_INVALID"
MAX_PHOTO_BYTES = 20 * 1024 * 1024
PHOTO_READ_CHUNK = 64 * 1024
_LIST_SECTIONS = frozenset(("projects", "training", "experience", "certificates"))
_FACT_SECTIONS = frozenset(("candidate", "summary", "education", "skills"))
_SECTION_LABELS = {"candidate": "个人信息", "summary": "个人概述", "education": "教育经历", "skills": "专业技能", "certificates": "证书与资格", "projects": "项目经历", "training": "实训经历", "experience": "相关经历"}
_CONTACT_FIELDS = (
    ("phone", "电话"), ("email", "邮箱"), ("city", "城市"),
    ("address", "地址"), ("website", "网站"), ("github", "GitHub"),
    ("wechat", "微信"),
)
_DISPLAY_FIELDS = {
    "candidate": (
        ("name", "姓名", "string"), ("headline", "求职标题", "string"),
        ("summary", "个人概述", "string"), ("contact", "联系方式", "contact"),
        ("directions", "求职方向", "list"),
    ),
    "education": (
        ("school", "学校", "string"), ("major", "专业", "string"),
        ("degree", "学历", "string"), ("start", "开始时间", "string"),
        ("end", "结束时间", "string"), ("courses", "核心课程", "list"),
        ("honors", "荣誉", "list"),
    ),
    "skills": (
        ("group", "技能方向", "string"), ("items", "技能", "list"),
        ("note", "说明", "string"),
    ),
    "certificates": (
        ("name", "证书", "string"), ("issuer", "发证机构", "string"),
        ("issued_on", "取得日期", "string"), ("expires_on", "有效期至", "string"),
        ("note", "说明", "string"),
    ),
    "projects": (
        ("title", "项目", "string"), ("role", "角色", "string"),
        ("start", "开始时间", "string"), ("end", "结束时间", "string"),
        ("summary", "项目概述", "string"), ("outcomes", "成果", "list"),
        ("tools", "工具", "list"),
    ),
    "training": (
        ("title", "实训", "string"), ("organization", "单位", "string"),
        ("start", "开始时间", "string"), ("end", "结束时间", "string"),
        ("summary", "项目概述", "string"), ("outcomes", "成果", "list"),
    ),
    "experience": (
        ("title", "经历", "string"), ("organization", "单位", "string"),
        ("start", "开始时间", "string"), ("end", "结束时间", "string"),
        ("summary", "项目概述", "string"), ("outcomes", "成果", "list"),
    ),
}


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
class ResolvedPhotoAsset:
    logical_path: str
    source_bytes: bytes
    source_sha256: str
    st_dev: int
    st_ino: int


@dataclass(frozen=True, slots=True)
class ContainerPlan:
    id: str
    kind: str
    section: str
    source_fact_ids: tuple[str, ...]
    fields: tuple[tuple[str, str], ...]
    page_number: int
    height_mm: float
    emphasis_terms: tuple[str, ...] = ()

    def to_projection(self) -> dict[str, Any]:
        return {"id": self.id, "kind": self.kind, "section": self.section, "source_fact_ids": list(self.source_fact_ids), "field_names": [key for key, _ in self.fields], "page_number": self.page_number, "height_mm": self.height_mm}


@dataclass(frozen=True, slots=True)
class EntryBudget:
    container_id: str
    source_fact_id: str
    height_mm: float
    atomic: bool = True

    def to_projection(self) -> dict[str, Any]:
        return {"container_id": self.container_id, "source_fact_id": self.source_fact_id, "height_mm": self.height_mm, "atomic": self.atomic}


@dataclass(frozen=True, slots=True)
class ColumnComposition:
    sidebar_sections: tuple[str, ...] = ()
    sidebar_width_mm: float = 0.0
    leading_em: float = 0.95
    sidebar_gap_mm: float = 0.0
    main_gap_mm: float = 0.0
    natural_height_mm: float = 0.0
    sidebar_height_mm: float = 0.0
    main_height_mm: float = 0.0
    filled_height_mm: float = 0.0
    fill_satisfied: bool = False
    detail_gap_mm: float = 0.0
    sidebar_container_ids: tuple[str, ...] = ()

    def is_sidebar(self, container: ContainerPlan) -> bool:
        return container.id in self.sidebar_container_ids if self.sidebar_container_ids else container.section in self.sidebar_sections

    def to_projection(self) -> dict[str, Any]:
        return {key: getattr(self, key) for key in self.__dataclass_fields__}


@dataclass(frozen=True, slots=True)
class PagePlan:
    number: int
    usable_height_mm: float
    used_height_mm: float
    utilization: float
    elastic_gap_mm: float
    anchors: tuple[str, ...]
    containers: tuple[str, ...]
    composition: ColumnComposition = ColumnComposition()

    def to_projection(self) -> dict[str, Any]:
        return {"number": self.number, "usable_height_mm": self.usable_height_mm, "used_height_mm": self.used_height_mm, "utilization": self.utilization, "elastic_gap_mm": self.elastic_gap_mm, "anchors": list(self.anchors), "containers": list(self.containers), "composition": self.composition.to_projection()}


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
        if self.photo_mode not in {"photo", "no-photo"} or (self.photo_mode == "photo") != (self.photo is not None):
            raise CliError(LAYOUT_PLAN_INVALID, "冻结照片模式与资源不一致。")
        if (self.photo_mode == "photo") != (self.photo_slot is not None):
            raise CliError(LAYOUT_PLAN_INVALID, "冻结照片模式与槽位不一致。")
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
        container_ids = tuple(container.id for container in self.containers)
        page_ids = tuple(container_id for page in self.pages for container_id in page.containers)
        if len(container_ids) != len(set(container_ids)) or len(page_ids) != len(set(page_ids)):
            raise CliError(LAYOUT_PLAN_INVALID, "冻结布局容器不得重复。")
        if page_ids != container_ids:
            raise CliError(LAYOUT_PLAN_INVALID, "冻结布局页面归属不完整或顺序无效。")
        containers_by_id = {container.id: container for container in self.containers}
        for page in self.pages:
            composition = page.composition
            if self.theme_key != "conservative" and (
                not composition.sidebar_sections or not composition.sidebar_width_mm
                or not any(composition.is_sidebar(containers_by_id[container_id]) for container_id in page.containers)
                or not any(not composition.is_sidebar(containers_by_id[container_id]) and containers_by_id[container_id].section != "candidate" for container_id in page.containers)
            ):
                raise CliError(LAYOUT_PLAN_INVALID, "双栏主题的每一页必须同时具有左右两栏正文，禁止退回单栏。")
            if composition.sidebar_container_ids and (
                len(set(composition.sidebar_container_ids)) != len(composition.sidebar_container_ids)
                or not set(composition.sidebar_container_ids) <= set(page.containers) - {"profile"}
            ):
                raise CliError(LAYOUT_PLAN_INVALID, "双栏条目归属必须绑定当前页面的完整正文条目。")
            if (
                composition.sidebar_width_mm not in ((0, 60, 70, 80, 88) if self.theme_key == "modern" else (0, 70, 80, 88))
                or not 0 <= composition.sidebar_gap_mm <= 10
                or not 0 <= composition.main_gap_mm <= 10
                or composition.detail_gap_mm not in (0, 1.5, 3, 4.5)
                or composition.leading_em != 0.95
                or abs(page.used_height_mm - composition.filled_height_mm) > 0.02
                or page.used_height_mm > page.usable_height_mm
            ):
                raise CliError(LAYOUT_PLAN_INVALID, "冻结栏位或间隙超出可读边界。")
            for container_id in page.containers:
                container = containers_by_id.get(container_id)
                if container is None:
                    raise CliError(LAYOUT_PLAN_INVALID, "页面引用未知容器。")
                if container.page_number != page.number:
                    raise CliError(LAYOUT_PLAN_INVALID, "容器页码与冻结页面不一致。")
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


_COMMON = {"safe_margins_mm": (14, 14, 15, 15), "spacing_tokens": ("xs", "sm", "md", "lg", "xl"), "photo_policy": PhotoFitPolicy()}
THEME_SPECS = {
    "conservative": ThemeSpec("conservative", "保守稳妥", "single-column-right-photo", PhotoSlot(32, 42, "top-right"), "remove-slot-and-decoration", **_COMMON, column_ratio=(100, 0), palette=("#FFFFFF", "#F2F4F7", "#183B62"), typography_pt=(9, 10.5, 12, 27)),
    "modern": ThemeSpec("modern", "现代简洁", "sidebar-photo", PhotoSlot(28, 36, "top-right"), "move-sidebar-content-up", **_COMMON, column_ratio=(33, 67), palette=("#FFFFFF", "#EAF4F2", "#0F766E"), typography_pt=(9, 10.2, 12, 27)),
    "expressive": ThemeSpec("expressive", "个性设计", "header-photo", PhotoSlot(30, 40, "header-right"), "expand-identity-bar", **_COMMON, column_ratio=(37, 63), palette=("#FFFEFA", "#F0E8D9", "#9A6C18"), typography_pt=(9, 10.2, 12, 27)),
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


def _display_string(value: Any) -> str:
    if not isinstance(value, str) or not value.strip() or any(
        unicodedata.category(character).startswith("C") for character in value
    ):
        raise CliError(LAYOUT_PLAN_INVALID, "展示字段必须是非空安全字符串。")
    return value.strip()


def _display_fields(section: str, item: Mapping[str, Any]) -> tuple[tuple[str, str], ...]:
    schema = _DISPLAY_FIELDS.get(section)
    if schema is None or set(item) - {"id", "status"} - {field for field, _, _ in schema}:
        raise CliError(LAYOUT_PLAN_INVALID, "展示事实包含未登记字段。")
    fields: list[tuple[str, str]] = []
    for field, label, kind in schema:
        if field not in item:
            continue
        value = item[field]
        if kind == "string":
            fields.append((field, _display_string(value)))
        elif kind == "list":
            if not isinstance(value, (list, tuple)):
                raise CliError(LAYOUT_PLAN_INVALID, "展示列表字段类型无效。")
            fields.extend(
                (f"{field}[{index}]", _display_string(entry))
                for index, entry in enumerate(value, start=1)
            )
        elif kind == "contact":
            if not isinstance(value, Mapping) or set(value) - {key for key, _ in _CONTACT_FIELDS}:
                raise CliError(LAYOUT_PLAN_INVALID, "联系方式字段无效。")
            fields.extend(
                (f"contact.{key}", _display_string(value[key]))
                for key, contact_label in _CONTACT_FIELDS
                if key in value
            )
        else:
            raise CliError(LAYOUT_PLAN_INVALID, "展示字段类型无效。")
    return tuple(fields)


def project_containers(verified_data: dict[str, Any], overrides: dict[str, str] | None = None, *, job_context: str = "") -> tuple[ContainerPlan, ...]:
    from graduate_resume_emphasis import ordered_courses, relevance, relevant_terms
    overrides = overrides or {}
    containers: list[ContainerPlan] = []
    profile = verified_data.get("candidate")
    if not isinstance(profile, dict) or not profile:
        raise CliError(LAYOUT_PLAN_INVALID, "已验证资料缺少个人信息。")
    profile_fields = _display_fields("candidate", profile)
    terms = relevant_terms(profile, job_context)
    course_context = job_context or "；".join((str(profile.get("headline", "")), *profile.get("directions", ())))
    containers.append(ContainerPlan("profile", "fact-block", "candidate", ("profile",), profile_fields, 1, 0.0))
    for section in ("education", "skills", "certificates", "projects", "training", "experience"):
        raw = verified_data.get(section, ())
        if not raw: continue
        if section not in _FACT_SECTIONS and section not in _LIST_SECTIONS and section not in overrides:
            continue
        items = raw if isinstance(raw, list) else [raw]
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                raise CliError(LAYOUT_PLAN_INVALID, "展示事实必须是映射。")
            fact_id = str(item.get("id") or f"{section}-{index + 1}")
            fields = _display_fields(section, item)
            if section == "education":
                fields = tuple((key, ordered_courses(value, terms, course_context) if key.split("[", 1)[0] == "courses" else value) for key, value in fields)
                courses = iter(sorted((value for key, value in fields if key.split("[", 1)[0] == "courses"), key=lambda value: -relevance(value, terms, course_context)))
                fields = tuple((key, next(courses) if key.split("[", 1)[0] == "courses" else value) for key, value in fields)
            if not fields:
                raise CliError(LAYOUT_PLAN_INVALID, "展示事实缺少可见内容。")
            kind = overrides.get(section, "list-entry" if section in _LIST_SECTIONS else "fact-block")
            if kind not in {"fact-block", "list-entry"}: raise CliError(LAYOUT_PLAN_INVALID, "容器覆盖无效。")
            containers.append(ContainerPlan(fact_id, kind, section, (fact_id,), fields, 1, 0.0, terms))
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


@lru_cache(maxsize=64)
def _query_layout_heights(source: str, font_hash: str, executable: TypstExecutable) -> tuple[dict[str, float], ...]:
    fonts = Path(__file__).resolve().parent.parent / "fonts"
    with tempfile.TemporaryDirectory(prefix="resume-measure-") as temporary:
        probe = Path(temporary) / "measure.typ"
        probe.write_text(source, encoding="utf-8")
        completed = executable.run((
            "query", "--font-path", str(fonts), "--ignore-system-fonts",
            str(probe), "<resume-measurement>", "--field", "value",
        ), text=True)
        if completed.returncode:
            raise CliError(LAYOUT_PLAN_INVALID, "Typst 实际栏宽测量失败。")
        try:
            heights = tuple({key: float(value[key]) for key in ("header", "sidebar", "main")} for value in json.loads(completed.stdout))
            if not heights or any(not math.isfinite(height) or height < 0 for record in heights for height in record.values()):
                raise ValueError
            return heights
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            raise CliError(LAYOUT_PLAN_INVALID, "Typst 实际高度测量无效。") from exc


def _measure_compositions(containers: tuple[ContainerPlan, ...], theme: ThemeSpec, photo_mode: str, font_hash: str, executable: TypstExecutable | None) -> tuple[tuple[ContainerPlan, ...], tuple[ColumnComposition, ...]]:
    from graduate_resume_typst import emit_page_body
    from graduate_resume_typst_runtime import resolve_typst_executable

    template = Path(__file__).resolve().parent.parent / "templates" / "resume-themes.typ"
    compositions = [(containers, False)]
    for split in range(1, len(containers)):
        compositions.extend(((containers[:split], False), (containers[split:], True)))
    compositions.extend(((container,), False) for container in containers)
    probes = []
    options_by_page = []
    for items, continuation in compositions:
        photo = 'rect(width: 100%, height: 100%, fill: white)' if photo_mode == "photo" and items[0].id == "profile" else "none"
        options = []
        section_sets = [()] if theme.key == "conservative" else [
            ("education", "skills", "certificates"),
            ("skills", "certificates", "training"),
            ("skills", "certificates"),
        ]
        for sections in section_sets:
            has_sidebar = any(item.section in sections for item in items)
            has_main = any(item.section not in (*sections, "candidate") for item in items)
            if sections and not (has_sidebar and has_main):
                continue
            widths = (60.0, 70.0, 80.0, 88.0) if theme.key == "modern" else (70.0, 80.0, 88.0)
            for width in (widths if sections else (0.0,)):
                for detail_gap in (0.0, 1.5, 3.0, 4.5):
                    option = ColumnComposition(sections, width, 0.95, detail_gap_mm=detail_gap)
                    options.append(option)
        if theme.key != "conservative":
            body = tuple(item for item in items if item.section != "candidate")
            for split in range(1, len(body)):
                left = body[:split]
                sections = tuple(dict.fromkeys(item.section for item in left))
                for detail_gap in (0.0, 1.5, 3.0, 4.5):
                    options.append(ColumnComposition(sections, 88.0, 0.95, detail_gap_mm=detail_gap, sidebar_container_ids=tuple(item.id for item in left)))
        if not options:
            options = [ColumnComposition()]
        options_by_page.append(options)
        for option in options:
            probes.append(emit_page_body(items, theme.key, photo, continuation, "resume-metrics", option))
    source = template.read_text(encoding="utf-8") + "\n" + "\n".join(probes)
    if executable is None:
        with resolve_typst_executable() as measured_executable:
            heights = _query_layout_heights(source, font_hash, measured_executable)
    else:
        heights = _query_layout_heights(source, font_hash, executable)
    if len(heights) != sum(len(options) for options in options_by_page):
        raise CliError(LAYOUT_PLAN_INVALID, "Typst 栏位测量集合不完整。")
    choices = []
    offset = 0
    target = 252.0
    for (items, _), options in zip(compositions, options_by_page):
        candidates = []
        for option, metric in zip(options, heights[offset:offset + len(options)]):
            header, side, main = (metric[key] for key in ("header", "sidebar", "main"))
            side_count = sum(option.is_sidebar(item) for item in items)
            main_count = sum(not option.is_sidebar(item) and item.section != "candidate" for item in items)
            natural = header + max(side, main)
            body_target = max(side, main, target - header)
            side_gap = min(10.0, max(0.0, (body_target - side) / max(1, side_count - 1))) if side_count > 1 else 0.0
            main_gap = min(10.0, max(0.0, (body_target - main) / max(1, main_count - 1))) if main_count > 1 else 0.0
            filled_side = side + side_gap * max(0, side_count - 1)
            filled_main = main + main_gap * max(0, main_count - 1)
            filled = header + max(filled_side, filled_main)
            minimum = header + min(filled_side, filled_main) if side_count else filled
            satisfied = minimum >= 240.0 and filled <= 265.0
            choice = replace(option, sidebar_gap_mm=round(side_gap, 4), main_gap_mm=round(main_gap, 4), natural_height_mm=natural, sidebar_height_mm=side, main_height_mm=main, filled_height_mm=filled, fill_satisfied=satisfied)
            score = (natural > 265.0, not satisfied, max(0.0, 240.0 - minimum), bool(option.sidebar_container_ids), not bool(option.sidebar_sections) if theme.key != "conservative" else False, abs(filled_side - filled_main) if side_count else 0.0, option.detail_gap_mm, side_gap + main_gap)
            candidates.append((score, choice))
        choices.append(min(candidates, key=lambda item: item[0])[1])
        offset += len(options)
    measured = tuple(replace(container, height_mm=round(choice.natural_height_mm, 3)) for container, choice in zip(containers, choices[-len(containers):]))
    return measured, tuple(choices[:1 + 2 * (len(containers) - 1)])


def _paginate(containers: tuple[ContainerPlan, ...], count: int, epsilon: float, heights: tuple[ColumnComposition, ...], *, require_columns: bool = False) -> tuple[tuple[ContainerPlan, ...], tuple[PagePlan, ...]]:
    usable = 267.0
    if count == 1:
        pages = (containers,)
        compositions = (heights[0],)
        if require_columns and not compositions[0].sidebar_sections:
            raise CliError(LAYOUT_UNSATISFIABLE, "当前内容无法组成左右两栏，禁止退回单栏。")
    else:
        candidates = []
        for split in range(1, len(containers)):
            first, second = heights[2 * split - 1:2 * split + 1]
            if require_columns and (not first.sidebar_sections or not second.sidebar_sections):
                continue
            if any(item.section == "education" for item in containers) and not any(item.section == "education" for item in containers[:split]):
                continue
            if max(first.filled_height_mm, second.filled_height_mm) + epsilon <= usable:
                deficit = sum(max(0.0, 240.0 - item.filled_height_mm) for item in (first, second))
                candidates.append((not (first.fill_satisfied and second.fill_satisfied), deficit, abs(first.natural_height_mm - second.natural_height_mm), split, first, second))
        if not candidates:
            raise CliError(LAYOUT_UNSATISFIABLE, "内容无法在两页内保持完整条目与可读边界。")
        _, _, _, split, first, second = min(candidates)
        pages, compositions = (containers[:split], containers[split:]), (first, second)
    used = tuple(item.filled_height_mm for item in compositions)
    if max(used) + epsilon > usable:
        raise CliError(LAYOUT_UNSATISFIABLE, "实际排版高度超过页面可读边界。")
    frozen = tuple(tuple(replace(item, page_number=number + 1) for item in items) for number, items in enumerate(pages))
    plans = tuple(
        PagePlan(
            index + 1, usable, round(used[index], 2), (round(used[index], 2) + epsilon) / usable,
            max(compositions[index].sidebar_gap_mm, compositions[index].main_gap_mm),
            ("profile",) if index == 0 else (f"section:{frozen[index][0].section}",), tuple(item.id for item in frozen[index]), compositions[index],
        )
        for index in range(count)
    )
    return frozen, plans


def build_frozen_resume_plan(verified_data: dict[str, Any], theme: ThemeSpec, photo_mode: str, photo: PhotoAsset | None, font_manifest_hash: str, page_preference: str, overrides: dict[str, str] | None = None, *, typst_executable: TypstExecutable | None = None, job_context: str = "") -> FrozenResumePlan:
    if (
        page_preference not in {"auto", "1", "2"}
        or not isinstance(font_manifest_hash, str)
        or len(font_manifest_hash) != 64
        or photo_mode not in {"photo", "no-photo"}
        or (photo_mode == "photo") != (photo is not None)
    ):
        raise CliError(LAYOUT_PLAN_INVALID, "冻结布局参数无效。")
    values, version, digest = _measurement(theme.key)
    policy = theme.photo_policy
    if policy.allow_stretch or (policy.crop_policy == "controlled" and not (policy.allow_controlled_crop and policy.subject_safe_area_contract)):
        raise CliError(LAYOUT_PLAN_INVALID, "主题照片策略无效。")
    containers, heights = _measure_compositions(project_containers(verified_data, overrides, job_context=job_context), theme, photo_mode, font_manifest_hash, typst_executable)
    one: tuple[tuple[ContainerPlan, ...], tuple[PagePlan, ...]] | None = None
    two: tuple[tuple[ContainerPlan, ...], tuple[PagePlan, ...]] | None = None
    try: one = _paginate(containers, 1, values["epsilon_mm"], heights, require_columns=theme.key != "conservative")
    except CliError: pass
    try: two = _paginate(containers, 2, values["epsilon_mm"], heights, require_columns=theme.key != "conservative")
    except CliError: pass
    if page_preference == "auto":
        if one:
            chosen, recommended, comparison, advisory = one, 1, None, None
        elif not one and two and all(page.utilization >= values["two_page_min_page_utilization"] for page in two[1]):
            chosen, recommended, comparison, advisory = two, 2, None, None
        elif two and all(page.composition.fill_satisfied for page in two[1]):
            chosen, recommended, comparison, advisory = two, 2, None, None
        else: raise CliError(LAYOUT_UNSATISFIABLE, "内容无法在指定主题的一页或两页结构内完整排入；双栏主题禁止退回单栏。")
    elif page_preference == "1":
        if not one: raise CliError(LAYOUT_UNSATISFIABLE, "强制一页无法保持完整条目与可读边界。")
        chosen, recommended, comparison, advisory = one, 1, None, None
    else:
        if not two: raise CliError(LAYOUT_UNSATISFIABLE, "强制两页无法保持完整条目与页首规则。")
        chosen, recommended, comparison, advisory = two, 1 if one else 2, 1 if one else None, "已按强制两页生成；内容更适合一页。" if one else None
    if not all(page.composition.fill_satisfied for page in chosen[1]):
        advisory = "资料不足以在受控间隙内达到逐栏铺满标准；保留真实内容。" + ("用户强制双页产生留白，建议改单页。" if page_preference == "2" else "不自动扩展为双页。")
    flattened = tuple(item for page in chosen[0] for item in page)
    budgets = tuple(EntryBudget(item.id, item.source_fact_ids[0], item.height_mm) for item in flattened if item.kind == "list-entry")
    plan = FrozenResumePlan(theme.key, theme.label, page_preference, len(chosen[1]), photo_mode, photo, policy.photo_fit, policy.crop_policy, policy.preserve_aspect_ratio, policy.allow_stretch, policy.allow_controlled_crop, policy.subject_safe_area_contract, theme.photo_slot if photo_mode == "photo" else None, theme.no_photo_behavior, font_manifest_hash, version, digest, chosen[1], flattened, budgets, "preserved-profile-and-education-front" if len(chosen[1]) == 2 else None, PageRecommendation(recommended, page_preference, comparison, advisory))
    plan.validate(verified_data)
    return plan


def selected_fact_view(facts: Mapping[str, Any], selected_fact_ids: tuple[str, ...]) -> dict[str, Any]:
    """Project only the shared selected ID tuple; never score or restore facts."""
    selected = frozenset(selected_fact_ids)
    if len(selected) != len(selected_fact_ids) or "profile" not in selected:
        raise CliError(LAYOUT_PLAN_INVALID, "所选事实视图无效。")
    result: dict[str, Any] = {"candidate": facts.get("candidate")}
    known = {"profile"}
    for section in ("education", "skills", "certificates", "projects", "training", "experience"):
        items = []
        for item in facts.get(section, ()) or ():
            if isinstance(item, Mapping) and isinstance(item.get("id"), str):
                known.add(item["id"])
                if item["id"] in selected:
                    items.append(dict(item))
        result[section] = items
    if selected - known:
        raise CliError(LAYOUT_PLAN_INVALID, "所选事实视图包含未知 ID。")
    return result


def build_layout_feedback_adapter(
    facts: Mapping[str, Any], photo_mode: str, photo: PhotoAsset | None,
    font_manifest_hash: str,
    typst_executable: TypstExecutable | None = None,
    *, job_context: str = "",
):
    """Return the Phase 48 real feedback callback for the shared fact tuple."""
    from graduate_resume_targeting import LayoutFeedback

    def feedback(theme_key: str, selected_ids: tuple[str, ...], request: Any) -> LayoutFeedback:
        view = selected_fact_view(facts, selected_ids)
        try:
            plan = build_frozen_resume_plan(
                view, resolve_theme(theme_key), photo_mode, photo, font_manifest_hash,
                request.requested_pages, typst_executable=typst_executable, job_context=job_context,
            )
            return LayoutFeedback(theme_key, True, plan.page_count, ())
        except CliError as exc:
            if exc.code != LAYOUT_UNSATISFIABLE:
                raise
            overflow = tuple(container.id for container in project_containers(view))
            return LayoutFeedback(theme_key, False, 3, overflow)

    return feedback


# Compatibility entry point retained for the Phase 47-01 theme-only contract.
def build_frozen_plan(theme: ThemeSpec, photo_mode: str, photo: PhotoAsset | None, font_manifest_hash: str, page_preference: str) -> FrozenResumePlan:
    digest = font_manifest_hash if len(font_manifest_hash) == 64 else hashlib.sha256(font_manifest_hash.encode("utf-8")).hexdigest()
    return build_frozen_resume_plan({"candidate": {"name": "已验证候选人"}, "education": []}, theme, photo_mode, photo, digest, page_preference)


def _manifest_error() -> CliError: return CliError(FONT_MANIFEST_INVALID, "受控字体清单无效。")
def _validate_font_visibility(fonts_root: Path, entries: list[dict[str, Any]], typst_executable: TypstExecutable) -> None:
    completed = typst_executable.run(("fonts", "--font-path", str(fonts_root), "--ignore-system-fonts", "--variants"), text=True)
    output = completed.stdout
    if completed.returncode or "Noto Sans Mono CJK SC" not in output: raise _manifest_error()
    expected = {400: "Weight: 400", 600: "Weight: 700"}
    if any(entry["path"] not in output or expected[entry["weight"]] not in output for entry in entries): raise _manifest_error()
def validate_font_manifest(fonts_root: Path, typst_executable: TypstExecutable) -> str:
    try:
        manifest = json.loads((fonts_root / "manifest.json").read_text(encoding="utf-8")); entries = manifest["fonts"]
        if manifest["family"] != "Noto Sans Mono CJK SC" or {item["weight"] for item in entries} != {400, 600}: raise ValueError
        digest = hashlib.sha256()
        for item in sorted(entries, key=lambda value: value["weight"]):
            path = fonts_root / PurePosixPath(item["path"])
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
            if actual != item["sha256"]: raise ValueError
            digest.update(actual.encode("ascii"))
        _validate_font_visibility(fonts_root, entries, typst_executable); return digest.hexdigest()
    except (OSError, KeyError, ValueError, TypeError, json.JSONDecodeError, subprocess.SubprocessError) as exc: raise _manifest_error() from exc
def _photo_error() -> CliError: return CliError(PHOTO_ASSET_INVALID, "照片资源无效。")


def _canonical_assets_root(path: Path) -> Path:
    absolute = Path(os.path.abspath(os.path.normpath(os.fspath(path))))
    parent = absolute.parent.resolve(strict=True)
    return parent / absolute.name


def _photo_identity(metadata: os.stat_result) -> tuple[int, int, int, int, int, int]:
    return (
        metadata.st_dev,
        metadata.st_ino,
        metadata.st_size,
        metadata.st_mode,
        metadata.st_mtime_ns,
        metadata.st_ctime_ns,
    )


def _valid_photo_bytes(path: PurePosixPath, source: bytes) -> bool:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return len(source) >= 4 and source.startswith(b"\xff\xd8") and source.endswith(b"\xff\xd9")
    if suffix == ".png":
        return (
            len(source) >= 20
            and source.startswith(b"\x89PNG\r\n\x1a\n")
            and source.endswith(b"\x00\x00\x00\x00IEND\xaeB\x60\x82")
        )
    return False


def resolve_layout_photo(
    input_path: Path,
    assets_root: Path,
    photo: dict[str, Any],
    preferences: dict[str, Any],
    *,
    _after_leaf_read: Callable[[], None] | None = None,
    _read_chunk_hook: Callable[[int], None] | None = None,
) -> ResolvedPhotoAsset | None:
    requested = preferences.get("photo_mode", "auto")
    if requested not in {"auto", "photo", "no-photo"}:
        raise _photo_error()
    if requested == "no-photo":
        return None
    if photo.get("status") != "provided":
        if requested == "photo":
            raise _photo_error()
        return None
    raw = photo.get("path")
    if not isinstance(raw, str) or not raw:
        raise _photo_error()
    pure = PurePosixPath(raw)
    if pure.is_absolute() or "\\" in raw or ":" in raw or any(part in {"", ".", ".."} for part in raw.split("/")): raise _photo_error()
    root_descriptor = -1
    current_descriptor = -1
    leaf_descriptor = -1
    try:
        root = _canonical_assets_root(assets_root)
        directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
        root_descriptor = os.open(root, directory_flags)
        root_before = os.fstat(root_descriptor)
        if not stat.S_ISDIR(root_before.st_mode):
            raise ValueError
        current_descriptor = os.dup(root_descriptor)
        for component in pure.parts[:-1]:
            child = os.open(component, directory_flags, dir_fd=current_descriptor)
            os.close(current_descriptor)
            current_descriptor = child
        leaf_descriptor = os.open(
            pure.parts[-1],
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0),
            dir_fd=current_descriptor,
        )
        before = os.fstat(leaf_descriptor)
        if (
            not stat.S_ISREG(before.st_mode)
            or before.st_mode & 0o444 == 0
            or not 8 <= before.st_size <= MAX_PHOTO_BYTES
        ):
            raise ValueError
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(leaf_descriptor, PHOTO_READ_CHUNK)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_PHOTO_BYTES:
                raise ValueError
            chunks.append(chunk)
            if _read_chunk_hook is not None:
                _read_chunk_hook(total)
        source = b"".join(chunks)
        after = os.fstat(leaf_descriptor)
        if _photo_identity(before) != _photo_identity(after) or total != before.st_size:
            raise ValueError
        if not _valid_photo_bytes(pure, source):
            raise ValueError
        if _after_leaf_read is not None:
            _after_leaf_read()
        root_after = os.fstat(root_descriptor)
        if (root_before.st_dev, root_before.st_ino, root_before.st_mode) != (
            root_after.st_dev,
            root_after.st_ino,
            root_after.st_mode,
        ):
            raise ValueError
        return ResolvedPhotoAsset(
            pure.as_posix(),
            source,
            hashlib.sha256(source).hexdigest(),
            before.st_dev,
            before.st_ino,
        )
    except (OSError, ValueError) as exc:
        raise _photo_error() from exc
    finally:
        for descriptor in (leaf_descriptor, current_descriptor, root_descriptor):
            if descriptor >= 0:
                os.close(descriptor)
