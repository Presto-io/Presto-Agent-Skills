#!/usr/bin/env python3
"""Phase 46 offline CLI for the graduate-resume skill."""

from __future__ import annotations

import argparse
import contextlib
import copy
import hashlib
import json
import os
import re
import shutil
import stat
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from graduate_resume_typst_runtime import TypstExecutable


STATUS_VALUES = {"verified", "pending", "declined"}
MAX_CANONICAL_BYTES = 4 * 1024 * 1024
CANONICAL_READ_CHUNK = 64 * 1024
STABLE_FACT_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,127}")
URL_RE = re.compile(r"(?i)^[a-z][a-z0-9+.-]*://")
TOP_LEVEL_FIELDS = {
    "candidate",
    "education",
    "skills",
    "certificates",
    "projects",
    "training",
    "experience",
    "targets",
    "photo",
    "preferences",
}
FRONTMATTER_FIELDS = {"schema", "profile", "photo", "preferences"}
MARKDOWN_SECTIONS = {
    "个人信息": "candidate",
    "教育经历": "education",
    "专业技能": "skills",
    "证书与资格": "certificates",
    "项目经历": "projects",
    "实训经历": "training",
    "相关经历": "experience",
    "求职目标": "targets",
}
SECTION_TITLES = {
    "education": "school",
    "skills": "group",
    "certificates": "name",
    "projects": "title",
    "training": "title",
    "experience": "title",
    "targets": "company",
}
FIELD_NAMES = {
    "求职方向": "directions", "个人概述": "summary", "求职标题": "headline",
    "电话": "phone", "邮箱": "email", "城市": "city", "地址": "address",
    "网站": "website", "GitHub": "github", "微信": "wechat",
    "学校": "school", "专业": "major", "学历": "degree", "开始时间": "start", "结束时间": "end",
    "核心课程": "courses", "荣誉": "honors", "技能": "items", "说明": "note",
    "发证机构": "issuer", "取得日期": "issued_on", "有效期至": "expires_on",
    "角色": "role", "项目概述": "summary", "成果": "outcomes", "工具": "tools",
    "单位": "organization", "岗位": "role", "来源": "source", "截至日期": "as_of",
    "招聘要求": "requirements", "已确认": "confirmed",
}
SECTION_SCHEMAS: dict[str, set[str]] = {
    "candidate": {"name", "status", "headline", "summary", "contact", "directions"},
    "contact": {"phone", "email", "city", "address", "website", "github", "wechat"},
    "education": {"id", "status", "school", "major", "degree", "start", "end", "courses", "honors"},
    "skills": {"id", "status", "group", "items", "note"},
    "certificates": {"id", "status", "name", "issuer", "issued_on", "expires_on", "note"},
    "projects": {"id", "status", "title", "role", "start", "end", "summary", "outcomes", "tools"},
    "training": {"id", "status", "title", "organization", "start", "end", "summary", "outcomes"},
    "experience": {"id", "status", "title", "organization", "start", "end", "summary", "outcomes"},
    "targets": {"id", "company", "role", "source", "as_of", "confirmed", "requirements", "note"},
    "photo": {"status", "path"},
    "preferences": {"theme", "preferred_pages", "photo_mode"},
}
ENTRY_SECTIONS = ("education", "skills", "certificates", "projects", "training", "experience")
VALID_FIXTURES = (
    "valid-photo-single-target.md",
    "valid-no-photo.md",
    "valid-generic-no-target.md",
    "valid-multi-target.md",
)
INVALID_FIXTURES = (
    "error-missing-required.md",
    "error-unknown-field.md",
    "error-duplicate-id.md",
    "error-pending-core-fact.md",
    "error-photo-invalid-path.md",
    "error-unconfirmed-target.md",
)


class CliError(Exception):
    """Stable CLI failure with code and message."""

    def __init__(self, code: str, message: str, details: list[str] | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details or []


@dataclass(frozen=True)
class ResumeDocument:
    path: Path
    body: str
    data: dict[str, Any]
    source_bytes: bytes
    source_sha256: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="graduate-resume.sh",
        description="主题可用 --theme <key> 选择：保守稳妥 (conservative)、现代简洁 (modern)、个性设计 (expressive)。",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="校验 Phase 46 资料契约。")
    validate.add_argument("--input", required=True, help="输入 Markdown 路径。")

    target = subparsers.add_parser("target", help="输出归一化 target brief 摘要。")
    target.add_argument("--input", required=True, help="输入 Markdown 路径。")

    plan = subparsers.add_parser("plan", help="输出受控主题、照片模式与布局输入摘要。")
    plan.add_argument("--input", required=True, help="输入 Markdown 路径。")
    plan.add_argument("--theme", help="使用 --theme <key> 选择：保守稳妥 (conservative)、现代简洁 (modern)、个性设计 (expressive)。")
    plan.add_argument("--pages", choices=("auto", "1", "2"), default="auto", help="页数偏好。")
    plan.add_argument("--photo-mode", choices=("auto", "photo", "no-photo"), default="auto", help="照片模式覆盖。")
    plan.add_argument("--assets-root", help="本地照片资源根目录，默认输入 Markdown 的父目录。")

    render = subparsers.add_parser("render", help="预检并发布通用版或一个定向版的三主题三件套。")
    _add_publication_arguments(render)
    selector = render.add_mutually_exclusive_group(required=True)
    selector.add_argument("--generic", action="store_true", help="生成通用版。")
    selector.add_argument("--target", metavar="TARGET_ID", help="生成一个稳定目标 ID 的定向版。")

    batch = subparsers.add_parser("batch", help="预检并权威发布通用版与全部已确认目标的三主题矩阵。")
    _add_publication_arguments(batch)

    verify = subparsers.add_parser("verify", help="运行 Phase 46 fixture 回归与依赖探测。")
    verify.add_argument(
        "--fixtures-root",
        default=str(default_skill_root() / "fixtures"),
        help="fixture 根目录，默认使用 skills/graduate-resume/fixtures。",
    )
    return parser.parse_args()


def _add_publication_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--input", required=True, help="输入 Markdown 路径。")
    parser.add_argument("--delivery-root", required=True, help="正式三件套投递根。")
    parser.add_argument("--evidence-root", help="定向条件完整证据的独立隐藏根。")
    parser.add_argument("--retain", metavar="FACT_ID", action="append", default=[], help="本次保留的稳定事实 ID，可重复。")
    parser.add_argument("--exclude", metavar="FACT_ID", action="append", default=[], help="本次排除的稳定事实 ID，可重复。")
    parser.add_argument("--pin", metavar="FACT_ID", action="append", default=[], help="本次置顶的稳定事实 ID，可重复。")
    parser.add_argument(
        "--not-applicable", metavar=("TARGET_ID", "CONDITION_ID", "REASON"), nargs=3,
        action="append", default=[], help="本次目标条件不适用覆盖，可重复。",
    )
    parser.add_argument(
        "--allow-gap-target", metavar="TARGET_ID", action="append", default=[],
        help="本次明确放行存在已核实缺口的目标 ID，可重复。",
    )
    parser.add_argument("--pages", choices=("auto", "1", "2"), default="auto", help="三主题共享页数偏好。")
    parser.add_argument("--photo-mode", choices=("auto", "photo", "no-photo"), default="auto", help="照片模式覆盖。")
    parser.add_argument("--assets-root", help="本地照片资源根，默认输入 Markdown 的父目录。")
    parser.add_argument("--confirm", action="store_true", help="确认发布当前预检摘要；省略时只预检。")
    parser.add_argument("--approval-digest", help="上一独立预检进程输出的 64 位小写 SHA-256。")


def default_skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _read_canonical_snapshot(path: Path) -> tuple[bytes, str]:
    nofollow = getattr(os, "O_NOFOLLOW", None)
    if nofollow is None:
        raise CliError("CANONICAL_INPUT_INVALID", "当前运行时不支持安全读取 canonical 输入。")
    flags = os.O_RDONLY | nofollow | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NONBLOCK", 0)
    file_descriptor = -1
    try:
        file_descriptor = os.open(path, flags)
        before = os.fstat(file_descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_CANONICAL_BYTES:
            raise CliError("CANONICAL_INPUT_INVALID", "canonical 输入必须是大小受限的普通文件。")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(file_descriptor, min(CANONICAL_READ_CHUNK, MAX_CANONICAL_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_CANONICAL_BYTES:
                raise CliError("CANONICAL_INPUT_INVALID", "canonical 输入超出大小上限。")
        after = os.fstat(file_descriptor)
        identity_before = (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns)
        identity_after = (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns, after.st_ctime_ns)
        if identity_after != identity_before or total != before.st_size:
            raise CliError("CANONICAL_INPUT_INVALID", "canonical 输入在读取期间发生变化。")
    except CliError:
        raise
    except OSError as exc:
        raise CliError("CANONICAL_INPUT_INVALID", "无法安全读取 canonical 输入。") from exc
    finally:
        if file_descriptor >= 0:
            try:
                os.close(file_descriptor)
            except OSError:
                pass
    source_bytes = b"".join(chunks)
    return source_bytes, hashlib.sha256(source_bytes).hexdigest()


def load_resume(path_value: str) -> ResumeDocument:
    expanded = Path(path_value).expanduser()
    try:
        absolute = expanded if expanded.is_absolute() else Path.cwd() / expanded
        path = absolute.parent.resolve(strict=True) / absolute.name
    except OSError as exc:
        raise CliError("CANONICAL_INPUT_INVALID", "canonical 输入父目录无效。") from exc
    source_bytes, source_sha256 = _read_canonical_snapshot(path)
    try:
        raw = source_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CliError("CANONICAL_INPUT_INVALID", "canonical 输入必须使用有效 UTF-8。") from exc
    if not raw.startswith("---\n"):
        raise CliError("FRONTMATTER_REQUIRED", "输入缺少 YAML frontmatter。")
    parts = raw.split("\n---\n", 1)
    if len(parts) != 2:
        raise CliError("FRONTMATTER_INVALID", "输入必须只包含一个闭合的 YAML frontmatter。")
    frontmatter = parts[0][4:]
    body = parts[1]
    try:
        parsed = yaml.safe_load(frontmatter) or {}
    except yaml.YAMLError as exc:
        raise CliError("YAML_PARSE_FAILED", f"YAML frontmatter 解析失败: {exc}") from exc
    if not isinstance(parsed, dict):
        raise CliError("YAML_ROOT_INVALID", "YAML frontmatter 顶层必须是映射对象。")
    unknown = sorted(set(parsed) - FRONTMATTER_FIELDS)
    if unknown:
        raise CliError("FRONTMATTER_INVALID", f"frontmatter 只允许 schema、profile、photo、preferences；发现: {', '.join(unknown)}")
    if parsed.get("schema") != "graduate-resume/v2":
        raise CliError("SCHEMA_VERSION_INVALID", "frontmatter.schema 必须为 graduate-resume/v2。")
    return ResumeDocument(
        path=path,
        body=body,
        data=parse_markdown_facts(
            body, parsed.get("profile") or {}, parsed.get("photo"), parsed.get("preferences") or {}
        ),
        source_bytes=source_bytes,
        source_sha256=source_sha256,
    )


def parse_metadata(raw: str, area: str, expected_fields: frozenset[str]) -> dict[str, str]:
    match = re.fullmatch(r"<!--\s*resume:\s*(.*?)\s*-->", raw.strip())
    if not match:
        raise CliError("MARKDOWN_INVALID", f"{area} 的 resume 元数据格式无效。")
    values: dict[str, str] = {}
    for token in match.group(1).split():
        if token.count("=") != 1:
            raise CliError("MARKDOWN_INVALID", f"{area} 的 resume 元数据必须使用 key=value。")
        key, value = token.split("=", 1)
        if not key or not value:
            raise CliError("MARKDOWN_INVALID", f"{area} 的 resume 元数据键和值均不能为空。")
        if key in values:
            raise CliError("MARKDOWN_INVALID", f"{area} 的 resume 元数据键不得重复。")
        values[key] = value
    if frozenset(values) != expected_fields:
        raise CliError("MARKDOWN_INVALID", f"{area} 的 resume 元数据字段集合无效。")
    if "status" in values and values["status"] not in STATUS_VALUES:
        raise CliError("MARKDOWN_INVALID", f"{area} 的 resume 元数据状态无效。")
    return values


def parse_value(field: str, raw: str) -> Any:
    value = raw.strip()
    if field in {"directions", "courses", "honors", "items", "outcomes", "tools", "requirements"}:
        return [item.strip() for item in value.split("；") if item.strip()]
    if field == "confirmed":
        return value == "是"
    return value


def parse_markdown_facts(body: str, profile: Any, photo_path: Any, preferences: Any) -> dict[str, Any]:
    if not isinstance(profile, dict):
        raise CliError("FRONTMATTER_INVALID", "frontmatter.profile 必须是对象。")
    if not isinstance(preferences, dict):
        raise CliError("FRONTMATTER_INVALID", "frontmatter.preferences 必须是对象。")
    if photo_path is None:
        photo = {"status": "no-photo"}
    elif isinstance(photo_path, str) and photo_path.strip():
        photo = {"status": "provided", "path": photo_path}
    else:
        raise CliError("FRONTMATTER_INVALID", "frontmatter.photo 必须是非空本地路径；无照片时省略该字段。")
    data: dict[str, Any] = {
        "candidate": profile, "education": [], "skills": [], "certificates": [], "projects": [],
        "training": [], "experience": [], "targets": [], "photo": photo, "preferences": preferences,
    }
    section: str | None = None
    entry: dict[str, Any] | None = None
    pending_area: tuple[str, dict[str, Any]] | None = None
    metadata_consumed = False
    unknown_fields: list[str] = []

    def require_metadata() -> None:
        if pending_area is not None and not metadata_consumed:
            raise CliError("MARKDOWN_INVALID", "Markdown 条目缺少必需的 resume 元数据。")

    for line_number, raw_line in enumerate(body.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            # 文档标题仅用于人类阅读；profile 是信息栏的唯一事实源。
            require_metadata()
            pending_area = None
            metadata_consumed = False
            continue
        if line.startswith("## "):
            require_metadata()
            title = line[3:].strip()
            section = MARKDOWN_SECTIONS.get(title)
            if section is None:
                unknown_fields.append(f"第 {line_number} 行包含未知模块: {title}")
            entry = None
            pending_area = None
            metadata_consumed = False
            continue
        if line.startswith("### "):
            require_metadata()
            if section not in SECTION_TITLES:
                unknown_fields.append(f"第 {line_number} 行的条目不属于可重复模块。")
                continue
            entry = {SECTION_TITLES[section]: line[4:].strip()}
            data[section].append(entry)
            pending_area = (section, entry)
            metadata_consumed = False
            continue
        if line.startswith("<!--"):
            if not line.startswith("<!-- resume:"):
                continue
            if pending_area is None:
                unknown_fields.append(f"第 {line_number} 行的 resume 元数据没有对应标题。")
                continue
            if metadata_consumed:
                raise CliError("MARKDOWN_INVALID", f"第 {line_number} 行的条目包含重复 resume 元数据。")
            expected_fields = frozenset({"id"}) if pending_area[0] == "targets" else frozenset({"id", "status"})
            metadata = parse_metadata(line, f"第 {line_number} 行", expected_fields)
            target = pending_area[1]
            if pending_area[0] != "targets":
                target["id"] = metadata["id"]
                target["status"] = metadata["status"]
            else:
                target["id"] = metadata["id"]
            metadata_consumed = True
            continue
        bullet = re.fullmatch(r"-\s+([^：:]+)[：:]\s*(.*)", line)
        if bullet:
            require_metadata()
            label, raw_value = bullet.groups()
            field = FIELD_NAMES.get(label)
            if field is None:
                unknown_fields.append(f"第 {line_number} 行包含未知字段: {label}")
                continue
            if entry is not None:
                if field in entry:
                    raise CliError("MARKDOWN_INVALID", f"第 {line_number} 行重复字段: {label}")
                entry[field] = parse_value(field, raw_value)
            else:
                unknown_fields.append(f"第 {line_number} 行的字段没有所属条目。")
            continue
        unknown_fields.append(f"第 {line_number} 行无法解析。")
    require_metadata()
    data["__markdown_issues__"] = unknown_fields
    return data


def ensure_mapping(value: Any, area: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CliError("SCHEMA_INVALID", f"{area} 必须是对象。")
    return value


def ensure_list(value: Any, area: str) -> list[Any]:
    if not isinstance(value, list):
        raise CliError("SCHEMA_INVALID", f"{area} 必须是列表。")
    return value


def require_nonempty_string(value: Any, area: str, issues: list[str]) -> None:
    if not isinstance(value, str) or not value.strip():
        issues.append(f"{area} 必须是非空字符串。")


def validate_string_list(value: Any, area: str, issues: list[str], *, required: bool = False) -> None:
    if not isinstance(value, list) or (required and not value) or any(not isinstance(item, str) or not item.strip() for item in value):
        issues.append(f"{area} 必须是{'非空' if required else ''}字符串列表。")


def validate_optional_values(section: dict[str, Any], area: str, issues: list[str]) -> None:
    list_fields = {"directions", "courses", "honors", "items", "outcomes", "tools"}
    ignored_fields = {"id", "status", "confirmed", "requirements", "contact"}
    for field, value in section.items():
        if field in list_fields:
            validate_string_list(value, f"{area}.{field}", issues)
        elif field not in ignored_fields:
            require_nonempty_string(value, f"{area}.{field}", issues)


def validate_status(value: Any, area: str, issues: list[str]) -> None:
    if value not in STATUS_VALUES:
        issues.append(f"{area} 必须是 {sorted(STATUS_VALUES)} 之一。")


def is_stable_fact_id(value: Any, *, profile: bool = False) -> bool:
    if profile:
        return value == "profile"
    return value != "profile" and isinstance(value, str) and STABLE_FACT_ID_RE.fullmatch(value) is not None


def validate_stable_fact_id(value: Any, area: str, issues: list[str]) -> None:
    if not is_stable_fact_id(value):
        issues.append(f"{area} 必须使用稳定事实 ID。")


def validate_unknown_fields(section: dict[str, Any], allowed: set[str], area: str, issues: list[str]) -> None:
    for key in sorted(section):
        if key not in allowed:
            issues.append(f"{area} 包含未知字段: {key}")


def validate_top_level(data: dict[str, Any], issues: list[str]) -> None:
    for key in sorted(data):
        if key not in TOP_LEVEL_FIELDS and key != "__markdown_issues__":
            issues.append(f"top-level 包含未知字段: {key}")
    issues.extend(data.get("__markdown_issues__", []))
    for required in ("candidate", "education", "targets", "photo"):
        if required not in data:
            issues.append(f"缺少必填 top-level 字段: {required}")


def validate_candidate(candidate_value: Any, issues: list[str]) -> None:
    candidate = ensure_mapping(candidate_value, "candidate")
    validate_unknown_fields(candidate, SECTION_SCHEMAS["candidate"], "candidate", issues)
    require_nonempty_string(candidate.get("name"), "candidate.name", issues)
    validate_status(candidate.get("status"), "candidate.status", issues)
    if candidate.get("status") == "pending":
        issues.append("candidate.status 仍为 pending，不能进入 final render。")
    if "contact" in candidate:
        if not isinstance(candidate["contact"], dict):
            issues.append("candidate.contact 必须是对象。")
        else:
            contact = candidate["contact"]
            validate_unknown_fields(contact, SECTION_SCHEMAS["contact"], "candidate.contact", issues)
            validate_optional_values(contact, "candidate.contact", issues)
    if "directions" in candidate and not isinstance(candidate["directions"], list):
        issues.append("candidate.directions 必须是字符串列表。")
    validate_optional_values(candidate, "candidate", issues)


def validate_entry_list(
    section_name: str,
    entries_value: Any,
    required_fields: tuple[str, ...],
    issues: list[str],
    seen_ids: dict[str, str],
) -> None:
    entries = ensure_list(entries_value, section_name)
    allowed = SECTION_SCHEMAS[section_name]
    for index, raw in enumerate(entries, start=1):
        area = f"{section_name}[{index}]"
        entry = ensure_mapping(raw, area)
        validate_unknown_fields(entry, allowed, area, issues)
        for field in required_fields:
            require_nonempty_string(entry.get(field), f"{area}.{field}", issues)
        validate_optional_values(entry, area, issues)
        validate_status(entry.get("status"), f"{area}.status", issues)
        if entry.get("status") == "pending":
            issues.append(f"{area}.status 仍为 pending，不能进入 final render。")
        entry_id = entry.get("id")
        validate_stable_fact_id(entry_id, f"{area}.id", issues)
        if is_stable_fact_id(entry_id):
            previous = seen_ids.get(entry_id)
            if previous is not None:
                issues.append(f"{area}.id 与其他事实 ID 重复。")
            else:
                seen_ids[entry_id] = area


def validate_targets(targets_value: Any, issues: list[str], seen_ids: dict[str, str]) -> list[dict[str, Any]]:
    targets = ensure_list(targets_value, "targets")
    for index, raw in enumerate(targets, start=1):
        area = f"targets[{index}]"
        target = ensure_mapping(raw, area)
        validate_unknown_fields(target, SECTION_SCHEMAS["targets"], area, issues)
        for field in ("id", "company", "role", "source", "as_of"):
            require_nonempty_string(target.get(field), f"{area}.{field}", issues)
        source = target.get("source")
        if isinstance(source, str) and URL_RE.match(source.strip()):
            issues.append(f"{area}.source 必须是来源描述，不能是 URL。")
        entry_id = target.get("id")
        validate_stable_fact_id(entry_id, f"{area}.id", issues)
        if is_stable_fact_id(entry_id):
            previous = seen_ids.get(entry_id)
            if previous is not None:
                issues.append(f"{area}.id 与其他事实 ID 重复。")
            else:
                seen_ids[entry_id] = area
        if target.get("confirmed") is not True:
            issues.append(f"{area}.confirmed 必须为 true，才能进入定向流程。")
        validate_string_list(target.get("requirements"), f"{area}.requirements", issues, required=True)
        if "note" in target:
            require_nonempty_string(target["note"], f"{area}.note", issues)
    return targets


def validate_photo(photo_value: Any, issues: list[str]) -> dict[str, Any]:
    photo = ensure_mapping(photo_value, "photo")
    validate_unknown_fields(photo, SECTION_SCHEMAS["photo"], "photo", issues)
    status = photo.get("status")
    if status not in {"provided", "no-photo"}:
        issues.append("photo 必须由受控解析器解析为 provided 或 no-photo。")
        return photo
    path = photo.get("path")
    if status == "provided":
        require_nonempty_string(path, "photo.path", issues)
        if isinstance(path, str) and path.startswith(("http://", "https://")):
            issues.append("photo.path 必须是本地路径，不能是远程 URL。")
    if status == "no-photo" and path is not None:
        issues.append("无照片时不得生成 photo.path。")
    return photo


def validate_preferences(preferences_value: Any, issues: list[str]) -> dict[str, Any]:
    preferences = ensure_mapping(preferences_value, "preferences")
    validate_unknown_fields(preferences, SECTION_SCHEMAS["preferences"], "preferences", issues)
    photo_mode = preferences.get("photo_mode")
    if photo_mode is not None and photo_mode not in {"auto", "photo", "no-photo"}:
        issues.append("preferences.photo_mode 必须是 auto、photo 或 no-photo。")
    preferred_pages = preferences.get("preferred_pages")
    if preferred_pages is not None and preferred_pages not in {"auto", 1, 2}:
        issues.append("preferences.preferred_pages 必须是 auto、1 或 2。")
    return preferences


def validate_document(document: ResumeDocument) -> dict[str, Any]:
    data = document.data
    issues: list[str] = []
    validate_top_level(data, issues)
    if "candidate" in data:
        validate_candidate(data["candidate"], issues)
    seen_ids: dict[str, str] = {}
    if "education" in data:
        validate_entry_list("education", data["education"], ("id", "school", "major"), issues, seen_ids)
    for section in ("skills", "certificates", "projects", "training", "experience"):
        if section in data:
            required = {
                "skills": ("id", "group"),
                "certificates": ("id", "name"),
                "projects": ("id", "title"),
                "training": ("id", "title"),
                "experience": ("id", "title"),
            }[section]
            validate_entry_list(section, data[section], required, issues, seen_ids)
    targets: list[dict[str, Any]] = []
    if "targets" in data:
        targets = validate_targets(data["targets"], issues, seen_ids)
    photo = {}
    if "photo" in data:
        photo = validate_photo(data["photo"], issues)
    preferences = {}
    if "preferences" in data:
        preferences = validate_preferences(data["preferences"], issues)
    valid = not issues
    summary = {
        "input": str(document.path),
        "status": "passed" if valid else "failed",
        "candidate_name": data.get("candidate", {}).get("name"),
        "target_count": len(targets),
        "photo_status": photo.get("status"),
        "entry_counts": {section: len(data.get(section, [])) for section in ENTRY_SECTIONS},
        "preferences": preferences,
        "issues": issues,
    }
    if not valid:
        raise CliError("VALIDATION_FAILED", "资料未通过 Phase 46 校验。", issues)
    return summary


def runtime_probe() -> dict[str, Any]:
    typst_path = shutil.which("typst")
    return {
        "offline_only": True,
        "token_free": True,
        "python3": sys.executable,
        "pyyaml": yaml.__version__,
        "typst": {"available": typst_path is not None, "path": typst_path},
        "font_policy": {
            "status": "phase-46-baseline",
            "require_skill_local_cjk_fonts": True,
            "recommended_flag": "--ignore-system-fonts",
            "note": "后续 Typst 渲染必须使用受控中文字体，不依赖系统 fallback。",
        },
    }


def command_validate(args: argparse.Namespace) -> int:
    document = load_resume(args.input)
    summary = validate_document(document)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


def command_target(args: argparse.Namespace) -> int:
    document = load_resume(args.input)
    validate_document(document)
    targets = document.data.get("targets", [])
    if not targets:
        payload = {
            "status": "passed",
            "mode": "generic",
            "message": "未提供 target；按一次确认后生成通用版基线。",
            "target_count": 0,
            "targets": [],
        }
    else:
        payload = {
            "status": "passed",
            "mode": "targeted",
            "message": "target brief 已归一化，可供后续阶段做定向选择。",
            "target_count": len(targets),
            "targets": [
                {
                    "id": item["id"],
                    "company": item["company"],
                    "role": item["role"],
                    "source": item["source"],
                    "as_of": item["as_of"],
                }
                for item in targets
            ],
        }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def resolve_photo_mode(photo: dict[str, Any], preferences: dict[str, Any]) -> str:
    declared = preferences.get("photo_mode")
    if declared == "no-photo":
        return "no-photo"
    if photo.get("status") == "no-photo":
        return "no-photo"
    if photo.get("status") == "provided":
        return "photo"
    return "auto"


def command_plan(args: argparse.Namespace) -> int:
    # Keep layout-only imports out of the Phase 46 validation path.
    from graduate_resume_layout import PhotoAsset, build_frozen_resume_plan, resolve_layout_photo, resolve_theme, validate_font_manifest
    from graduate_resume_typst_runtime import resolve_typst_executable

    document = load_resume(args.input)
    validate_document(document)
    data = document.data
    targets = data.get("targets", [])
    photo = data.get("photo", {})
    preferences = data.get("preferences", {})
    theme = resolve_theme(args.theme or preferences.get("theme"))
    assets_root = Path(args.assets_root).expanduser() if args.assets_root else document.path.parent
    requested_photo_mode = resolve_photo_mode(photo, preferences) if args.photo_mode == "auto" else args.photo_mode
    with resolve_typst_executable() as typst_executable:
        resolved_photo = resolve_layout_photo(document.path, assets_root, photo, {"photo_mode": requested_photo_mode})
        photo_asset = None if resolved_photo is None else PhotoAsset("embedded-normalized.png")
        font_manifest_hash = validate_font_manifest(default_skill_root() / "fonts", typst_executable)
        frozen_plan = build_frozen_resume_plan(data, theme, requested_photo_mode, photo_asset, font_manifest_hash, args.pages)
    payload = {
        "status": "passed",
        "phase": 47,
        "plan_type": "frozen-resume-layout",
        "resume_mode": "generic" if not targets else "targeted",
        "target_count": len(targets),
        "resolved_photo_mode": frozen_plan.photo_mode,
        "preferred_pages": args.pages,
        "theme": {"key": theme.key, "label": theme.label},
        "theme_selection": "--theme <key>",
        "available_themes": [{"key": item.key, "label": item.label} for item in THEME_SPECS_FOR_HELP()],
        "frozen_layout": frozen_plan.to_projection(),
        "font_manifest_hash": font_manifest_hash,
        "advisory": frozen_plan.recommendation.advisory,
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def THEME_SPECS_FOR_HELP() -> tuple[Any, ...]:
    from graduate_resume_layout import THEME_SPECS
    return tuple(THEME_SPECS[key] for key in ("conservative", "modern", "expressive"))


_CONDITION_ID_RE = re.compile(r"condition-[0-9a-f]{20}")


def _validate_stable_id(value: str, *, condition: bool = False) -> str:
    valid = (
        isinstance(value, str) and _CONDITION_ID_RE.fullmatch(value) is not None
        if condition
        else is_stable_fact_id(value)
    )
    if not valid:
        raise CliError("TARGET_CONDITION_INVALID", "目标或条件必须使用稳定 ID。")
    return value


def _publication_request(args: argparse.Namespace, document: ResumeDocument, *, batch: bool) -> tuple[list[dict[str, Any] | None], dict[str, list[tuple[str, str, str]]]]:
    targets = document.data.get("targets", [])
    target_map = {str(item["id"]): item for item in targets}
    selected: list[dict[str, Any] | None]
    if batch:
        selected = [None, *targets]
    elif args.generic:
        selected = [None]
    else:
        target_id = _validate_stable_id(args.target)
        if target_id not in target_map:
            raise CliError("TARGET_NOT_SELECTED", "指定目标不存在或未确认。")
        selected = [target_map[target_id]]
    selected_ids = {str(item["id"]) for item in selected if item is not None}
    allowed = tuple(_validate_stable_id(item) for item in args.allow_gap_target)
    if len(allowed) != len(set(allowed)) or any(item not in selected_ids for item in allowed):
        raise CliError("TARGET_CONDITION_INVALID", "缺口放行重复或引用未选择目标。")
    grouped: dict[str, list[tuple[str, str, str]]] = {}
    seen: set[tuple[str, str]] = set()
    for target_id, condition_id, raw_reason in args.not_applicable:
        target_id = _validate_stable_id(target_id)
        condition_id = _validate_stable_id(condition_id, condition=True)
        reason = raw_reason.strip()
        if not 1 <= len(reason) <= 200 or any(unicodedata.category(character).startswith("C") for character in reason):
            raise CliError("TARGET_CONDITION_INVALID", "不适用理由长度或字符无效。")
        pair = (target_id, condition_id)
        if pair in seen or target_id not in selected_ids:
            raise CliError("TARGET_CONDITION_INVALID", "不适用覆盖重复或引用未选择目标。")
        seen.add(pair)
        grouped.setdefault(target_id, []).append((target_id, condition_id, reason))
    if selected == [None] and (allowed or grouped):
        raise CliError("TARGET_CONDITION_INVALID", "通用版不得携带目标条件覆盖或缺口放行。")
    return selected, grouped


def _resolve_publication_photo(args: argparse.Namespace, document: ResumeDocument, typst_executable: "TypstExecutable") -> tuple[str, bytes | None, Any | None, str]:
    from graduate_resume_layout import PhotoAsset, resolve_layout_photo, validate_font_manifest

    photo = document.data.get("photo", {})
    preferences = document.data.get("preferences", {})
    requested = resolve_photo_mode(photo, preferences) if args.photo_mode == "auto" else args.photo_mode
    assets_root = Path(args.assets_root).expanduser() if args.assets_root else document.path.parent
    resolved = resolve_layout_photo(document.path, assets_root, photo, {"photo_mode": requested})
    photo_bytes = None
    feedback_photo = None
    photo_mode = "no-photo"
    if resolved is not None:
        photo_bytes = resolved.source_bytes
        feedback_photo = PhotoAsset("embedded-normalized.png")
        photo_mode = "photo"
    font_hash = validate_font_manifest(default_skill_root() / "fonts", typst_executable)
    return photo_mode, photo_bytes, feedback_photo, font_hash


def _discover_current_stems(delivery_root: Path, candidate_name: str) -> tuple[str, ...]:
    from graduate_resume_render import safe_component

    try:
        if delivery_root.is_symlink() or not delivery_root.exists():
            return ()
        entries = tuple(delivery_root.iterdir())
    except OSError:
        return ()
    prefix = f"{safe_component(candidate_name)}简历-"
    theme_suffixes = tuple(safe_component(item.label) for item in THEME_SPECS_FOR_HELP())
    stems: set[str] = set()
    for path in entries:
        if path.suffix not in {".md", ".typ", ".pdf"}:
            continue
        stem = path.stem
        if stem.startswith(prefix) and any(stem.endswith(f"-{theme}") for theme in theme_suffixes):
            stems.add(stem)
    return tuple(sorted(stems))


def _projection_public(projection: Any) -> dict[str, Any]:
    return {
        "version": projection.version_id,
        "target_id": projection.target_id,
        "source": projection.target_source,
        "as_of": projection.target_as_of,
        "selected_fact_digest": hashlib.sha256("\0".join(projection.selected_fact_ids).encode("utf-8")).hexdigest(),
        "conditions": dict(projection.condition_summary),
        "condition_digest": projection.condition_digest,
        "gap_allowed": projection.gap_allowed,
        "pages": {item.theme_key: item.page_count for item in projection.layout_feedback},
    }


def publication_fact_view(data: dict[str, Any]) -> dict[str, Any]:
    """Return an isolated view containing only facts eligible for publication."""
    candidate = data.get("candidate")
    if not isinstance(candidate, dict) or candidate.get("status") != "verified":
        raise CliError("PUBLICATION_FACT_INVALID", "正式渲染要求已核实的个人信息。")
    view = copy.deepcopy(data)
    for section in ENTRY_SECTIONS:
        entries = view.get(section, [])
        if any(not isinstance(item, dict) or item.get("status") != "verified" for item in entries):
            raise CliError("PUBLICATION_FACT_INVALID", "正式渲染只接受已核实事实。")
        view[section] = [item for item in entries if isinstance(item, dict) and item.get("status") == "verified"]
    return view


def _command_publication(args: argparse.Namespace, *, batch: bool) -> int:
    from graduate_resume_typst_runtime import resolve_typst_executable

    if args.confirm != bool(args.approval_digest):
        raise CliError("APPROVAL_DIGEST_INVALID", "--confirm 与 --approval-digest 必须同时提供。")
    if args.approval_digest and not re.fullmatch(r"[0-9a-f]{64}", args.approval_digest):
        raise CliError("APPROVAL_DIGEST_INVALID", "approval digest 必须是 64 位小写十六进制。")
    document = load_resume(args.input)
    validate_document(document)
    publication_data = publication_fact_view(document.data)
    publication_document = ResumeDocument(
        document.path, document.body, publication_data, document.source_bytes, document.source_sha256,
    )
    selected, not_applicable = _publication_request(args, publication_document, batch=batch)
    with resolve_typst_executable() as typst_executable:
        return _execute_publication(
            args,
            batch=batch,
            document=document,
            publication_data=publication_data,
            selected=selected,
            not_applicable=not_applicable,
            typst_executable=typst_executable,
        )


def _execute_publication(
    args: argparse.Namespace,
    *,
    batch: bool,
    document: ResumeDocument,
    publication_data: dict[str, Any],
    selected: list[dict[str, Any] | None],
    not_applicable: dict[str, list[tuple[str, str, str]]],
    typst_executable: "TypstExecutable",
) -> int:
    from graduate_resume_delivery import DeliveryError, DeliverySession, DeliverySpec
    from graduate_resume_layout import build_layout_feedback_adapter
    from graduate_resume_render import EvidenceSink, build_render_matrix, render_candidate_matrix, safe_component
    from graduate_resume_targeting import PageBudgetRequest, evaluate_hard_conditions, resolve_version_projection

    photo_mode, photo_bytes, feedback_photo, font_hash = _resolve_publication_photo(args, document, typst_executable)
    page_budget = PageBudgetRequest(args.pages)
    feedback = build_layout_feedback_adapter(publication_data, photo_mode, feedback_photo, font_hash)
    overrides = {"retain": args.retain, "exclude": args.exclude, "pin": args.pin}
    projections = []
    condition_evidence: dict[str, dict[str, Any]] = {}
    condition_public: dict[str, dict[str, Any]] = {}
    allowed = tuple(args.allow_gap_target)
    for target in selected:
        target_id = None if target is None else str(target["id"])
        target_overrides = () if target_id is None else tuple(not_applicable.get(target_id, ()))
        projection = resolve_version_projection(
            publication_data, target, page_budget, feedback, overrides=overrides,
            not_applicable_overrides=target_overrides,
            allowed_gap_target_ids=() if target is None else allowed,
        )
        projections.append(projection)
        if target is not None:
            evaluation = evaluate_hard_conditions(
                publication_data, target, not_applicable_overrides=target_overrides,
                allowed_gap_target_ids=allowed,
            )
            condition_public[target_id] = {
                **evaluation.to_public_projection(),
                "conditions": [
                    {"condition_id": item.condition_id, "predicate": item.predicate, "state": item.state}
                    for item in evaluation.matrix
                ],
            }
            condition_evidence[target_id] = evaluation.to_evidence_projection()
    target_map = {str(item["id"]): item for item in publication_data.get("targets", [])}
    planned = build_render_matrix(publication_data["candidate"]["name"], tuple(projections), targets=target_map)
    delivery_root = Path(args.delivery_root).expanduser()
    known_stems = tuple(dict.fromkeys((
        *(item.stem for item in planned.items),
        *_discover_current_stems(delivery_root, publication_data["candidate"]["name"]),
    )))
    theme_suffixes = tuple(safe_component(item.label) for item in THEME_SPECS_FOR_HELP())
    canonical_hash = document.source_sha256
    mode = "authority" if batch else "patch"
    if condition_evidence and not args.evidence_root:
        raise CliError("EVIDENCE_ROOT_REQUIRED", "定向渲染必须显式授权独立隐藏证据根。")
    try:
        evidence_context = (
            EvidenceSink(args.evidence_root, delivery_root=delivery_root, create=False)
            if condition_evidence else contextlib.nullcontext(None)
        )
        with evidence_context as evidence_sink, tempfile.TemporaryDirectory(prefix="graduate-resume-render-") as temporary:
            rendered_roots: list[Path] = []
            for index, (projection, target) in enumerate(zip(projections, selected)):
                result = render_candidate_matrix(
                    Path(temporary) / f"version-{index}" / "candidate", publication_data, projection,
                    canonical_hash=canonical_hash, target=target, photo_bytes=photo_bytes,
                    typst_executable=typst_executable, font_manifest_hash=font_hash,
                    condition_evidence=None if target is None else condition_evidence[str(target["id"])],
                    evidence_root=evidence_sink,
                    persist_evidence=False,
                )
                if not result.publishable or result.candidate_root is None:
                    raise CliError("RENDER_MATRIX_FAILED", "候选矩阵未完成。")
                rendered_roots.append(result.candidate_root)
            owner_prefix = f"{safe_component(publication_data['candidate']['name'])}简历-"
            evidence_path = None if evidence_sink is None else os.fspath(evidence_sink.path)
            evidence_identity = None if evidence_sink is None else evidence_sink.identity
            spec = DeliverySpec(
                delivery_root, known_stems, theme_suffixes, mode, owner_prefix,
                canonical_hash, evidence_path, evidence_identity,
            )
            with DeliverySession(spec) as session:
                for rendered_root in rendered_roots:
                    for path in rendered_root.iterdir():
                        if path.is_file():
                            session.candidate_path(path.name).write_bytes(path.read_bytes())
                delta = session.preflight()
                if evidence_sink is not None:
                    evidence_sink.assert_identity()
                publication = None
                if args.confirm:
                    if evidence_sink is not None:
                        evidence_sink.assert_identity()
                    publication = session.publish(
                        approval_digest=args.approval_digest,
                    )
                    if evidence_sink is not None:
                        for projection, target in zip(projections, selected):
                            if target is not None:
                                evidence_sink.persist(
                                    canonical_hash=canonical_hash,
                                    projection=projection,
                                    condition_evidence=condition_evidence[str(target["id"])],
                                )
    except DeliveryError as exc:
        raise CliError("DELIVERY_PREFLIGHT_FAILED", "正式投递预检或发布失败。") from exc
    versions = [_projection_public(item) for item in projections]
    payload = {
        "status": "published" if args.confirm else "preflight",
        "mode": mode,
        "publication": publication,
        "versions": [item.version_id for item in projections],
        "matrix": versions,
        "stems": [item.stem for item in planned.items],
        "photo_mode": photo_mode,
        "gap_allow_target_ids": list(allowed),
        "added": list(delta.added),
        "updated": list(delta.updated),
        "unchanged": list(delta.unchanged),
        "removed": list(delta.removed),
        "approval_digest": delta.approval_digest,
    }
    payload["target_conditions"] = condition_public
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def command_render(args: argparse.Namespace) -> int:
    return _command_publication(args, batch=False)


def command_batch(args: argparse.Namespace) -> int:
    return _command_publication(args, batch=True)


def command_verify(args: argparse.Namespace) -> int:
    fixtures_root = Path(args.fixtures_root).expanduser().resolve()
    if not fixtures_root.is_dir():
        raise CliError("FIXTURES_NOT_FOUND", f"fixtures 目录不存在: {fixtures_root}")
    results: list[dict[str, Any]] = []
    for fixture_name in VALID_FIXTURES:
        summary = validate_document(load_resume(str(fixtures_root / fixture_name)))
        results.append({"fixture": fixture_name, "expected": "pass", "actual": summary["status"]})
    for fixture_name in INVALID_FIXTURES:
        try:
            validate_document(load_resume(str(fixtures_root / fixture_name)))
        except CliError as exc:
            if exc.code != "VALIDATION_FAILED":
                raise
            results.append({"fixture": fixture_name, "expected": "fail", "actual": "failed"})
        else:
            raise CliError("VERIFY_FAILED", f"负例 fixture 意外通过: {fixture_name}")
    # The Phase 47 matrix is intentionally literal and uses disposable evidence
    # roots; it cannot discover user fixtures or publish delivery artifacts.
    from test_layout_fixtures import LAYOUT_FIXTURES, run_layout_fixture_matrix
    run_layout_fixture_matrix()
    results.extend({"fixture": f"layout/{fixture_name}", "expected": "pass", "actual": "passed"} for fixture_name in LAYOUT_FIXTURES[:-1])
    results.append({"fixture": f"layout/{LAYOUT_FIXTURES[-1]}", "expected": "fail", "actual": "failed"})
    payload = {
        "status": "passed",
        "fixtures_root": str(fixtures_root),
        "valid_fixture_count": len(VALID_FIXTURES),
        "invalid_fixture_count": len(INVALID_FIXTURES),
        "layout_fixture_count": len(LAYOUT_FIXTURES),
        "results": results,
        "runtime_probe": runtime_probe(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def main() -> int:
    args = parse_args()
    try:
        if args.command == "validate":
            return command_validate(args)
        if args.command == "target":
            return command_target(args)
        if args.command == "plan":
            return command_plan(args)
        if args.command == "verify":
            return command_verify(args)
        if args.command == "render":
            return command_render(args)
        if args.command == "batch":
            return command_batch(args)
        raise CliError("UNKNOWN_COMMAND", f"未知命令: {args.command}")
    except Exception as exc:
        # ``graduate_resume_layout`` can import this script by module name while
        # this entry point is running as ``__main__``.  Normalize every stable
        # CLI-shaped error here so layout failures never leak a traceback.
        if not isinstance(getattr(exc, "code", None), str) or not isinstance(getattr(exc, "message", None), str):
            payload = {"status": "failed", "code": "INTERNAL_ERROR", "message": "离线命令执行失败，正式投递未改变。"}
            print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
            return 70
        payload = {"status": "failed", "code": exc.code, "message": exc.message}
        if getattr(exc, "details", None):
            payload["issues"] = exc.details
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2 if exc.code in {"VALIDATION_FAILED", "NOT_IMPLEMENTED"} else 64


if __name__ == "__main__":
    sys.exit(main())
