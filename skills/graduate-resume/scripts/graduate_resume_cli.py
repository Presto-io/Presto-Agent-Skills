#!/usr/bin/env python3
"""Phase 46 offline CLI for the graduate-resume skill."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


STATUS_VALUES = {"verified", "pending", "declined"}
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


@dataclass
class ResumeDocument:
    path: Path
    body: str
    data: dict[str, Any]


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

    render = subparsers.add_parser("render", help="保留给后续阶段。")
    render.add_argument("--input", required=False, help="输入 Markdown 路径。")

    batch = subparsers.add_parser("batch", help="保留给后续阶段。")
    batch.add_argument("--input", required=False, help="输入 Markdown 路径。")

    verify = subparsers.add_parser("verify", help="运行 Phase 46 fixture 回归与依赖探测。")
    verify.add_argument(
        "--fixtures-root",
        default=str(default_skill_root() / "fixtures"),
        help="fixture 根目录，默认使用 skills/graduate-resume/fixtures。",
    )
    return parser.parse_args()


def default_skill_root() -> Path:
    return Path(__file__).resolve().parent.parent


def load_resume(path_value: str) -> ResumeDocument:
    path = Path(path_value).expanduser().resolve()
    if not path.is_file():
        raise CliError("INPUT_NOT_FOUND", f"输入文件不存在: {path}")
    raw = path.read_text(encoding="utf-8")
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
    )


def parse_metadata(raw: str, area: str) -> dict[str, str]:
    match = re.fullmatch(r"<!--\s*resume:\s*(.*?)\s*-->", raw.strip())
    if not match:
        raise CliError("MARKDOWN_INVALID", f"{area} 的 resume 元数据格式无效。")
    values: dict[str, str] = {}
    for token in match.group(1).split():
        if "=" not in token:
            raise CliError("MARKDOWN_INVALID", f"{area} 的 resume 元数据必须使用 key=value。")
        key, value = token.split("=", 1)
        values[key] = value
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
    unknown_fields: list[str] = []
    for line_number, raw_line in enumerate(body.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("# "):
            # 文档标题仅用于人类阅读；profile 是信息栏的唯一事实源。
            pending_area = None
            continue
        if line.startswith("## "):
            title = line[3:].strip()
            section = MARKDOWN_SECTIONS.get(title)
            if section is None:
                unknown_fields.append(f"第 {line_number} 行包含未知模块: {title}")
            entry = None
            pending_area = None
            continue
        if line.startswith("### "):
            if section not in SECTION_TITLES:
                unknown_fields.append(f"第 {line_number} 行的条目不属于可重复模块。")
                continue
            entry = {SECTION_TITLES[section]: line[4:].strip()}
            data[section].append(entry)
            pending_area = (section, entry)
            continue
        if line.startswith("<!--"):
            if not line.startswith("<!-- resume:"):
                continue
            if pending_area is None:
                unknown_fields.append(f"第 {line_number} 行的 resume 元数据没有对应标题。")
                continue
            metadata = parse_metadata(line, f"第 {line_number} 行")
            target = pending_area[1]
            if pending_area[0] != "targets":
                target["id"] = metadata.get("id")
                target["status"] = metadata.get("status", "verified")
            else:
                target["id"] = metadata.get("id")
            continue
        bullet = re.fullmatch(r"-\s+([^：:]+)[：:]\s*(.*)", line)
        if bullet:
            label, raw_value = bullet.groups()
            field = FIELD_NAMES.get(label)
            if field is None:
                unknown_fields.append(f"第 {line_number} 行包含未知字段: {label}")
                continue
            if entry is not None:
                entry[field] = parse_value(field, raw_value)
            else:
                unknown_fields.append(f"第 {line_number} 行的字段没有所属条目。")
            continue
        unknown_fields.append(f"第 {line_number} 行无法解析。")
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


def validate_status(value: Any, area: str, issues: list[str]) -> None:
    if value not in STATUS_VALUES:
        issues.append(f"{area} 必须是 {sorted(STATUS_VALUES)} 之一。")


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
        contact = ensure_mapping(candidate["contact"], "candidate.contact")
        validate_unknown_fields(contact, SECTION_SCHEMAS["contact"], "candidate.contact", issues)
    if "directions" in candidate and not isinstance(candidate["directions"], list):
        issues.append("candidate.directions 必须是字符串列表。")


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
        validate_status(entry.get("status"), f"{area}.status", issues)
        if entry.get("status") == "pending":
            issues.append(f"{area}.status 仍为 pending，不能进入 final render。")
        entry_id = entry.get("id")
        if isinstance(entry_id, str) and entry_id.strip():
            previous = seen_ids.get(entry_id)
            if previous is not None:
                issues.append(f"发现重复事实 ID: {entry_id} 同时出现在 {previous} 和 {area}")
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
        entry_id = target.get("id")
        if isinstance(entry_id, str) and entry_id.strip():
            previous = seen_ids.get(entry_id)
            if previous is not None:
                issues.append(f"发现重复事实 ID: {entry_id} 同时出现在 {previous} 和 {area}")
            else:
                seen_ids[entry_id] = area
        if target.get("confirmed") is not True:
            issues.append(f"{area}.confirmed 必须为 true，才能进入定向流程。")
        requirements = target.get("requirements")
        if requirements is not None and not isinstance(requirements, list):
            issues.append(f"{area}.requirements 必须是字符串列表。")
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
    from graduate_resume_layout import build_frozen_plan, resolve_layout_photo, resolve_theme, validate_font_manifest

    document = load_resume(args.input)
    validate_document(document)
    data = document.data
    targets = data.get("targets", [])
    photo = data.get("photo", {})
    preferences = data.get("preferences", {})
    theme = resolve_theme(args.theme or preferences.get("theme"))
    assets_root = Path(args.assets_root).expanduser() if args.assets_root else document.path.parent
    requested_photo_mode = resolve_photo_mode(photo, preferences) if args.photo_mode == "auto" else args.photo_mode
    photo_asset = resolve_layout_photo(document.path, assets_root, photo, {"photo_mode": requested_photo_mode})
    font_manifest_hash = validate_font_manifest(default_skill_root() / "fonts")
    frozen_plan = build_frozen_plan(theme, requested_photo_mode, photo_asset, font_manifest_hash, args.pages)
    payload = {
        "status": "passed",
        "phase": 47,
        "plan_type": "controlled-layout-inputs",
        "resume_mode": "generic" if not targets else "targeted",
        "target_count": len(targets),
        "resolved_photo_mode": frozen_plan.photo_mode,
        "preferred_pages": args.pages,
        "theme": {"key": theme.key, "label": theme.label},
        "theme_selection": "--theme <key>",
        "available_themes": [{"key": item.key, "label": item.label} for item in THEME_SPECS_FOR_HELP()],
        "frozen_layout": frozen_plan.to_projection(),
        "font_manifest_hash": font_manifest_hash,
        "next_phase_inputs": {
            "schema_frozen": True,
            "target_briefs_ready": bool(targets),
            "photo_contract_ready": photo.get("status") in {"provided", "no-photo"},
        },
        "runtime_probe": runtime_probe(),
    }
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def THEME_SPECS_FOR_HELP() -> tuple[Any, ...]:
    from graduate_resume_layout import THEME_SPECS
    return tuple(THEME_SPECS[key] for key in ("conservative", "modern", "expressive"))


def command_reserved(command_name: str) -> int:
    raise CliError(
        "NOT_IMPLEMENTED",
        f"{command_name} 保留给后续阶段；Phase 46 只冻结离线零 token 边界，不提供最终渲染。",
    )


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
    payload = {
        "status": "passed",
        "fixtures_root": str(fixtures_root),
        "valid_fixture_count": len(VALID_FIXTURES),
        "invalid_fixture_count": len(INVALID_FIXTURES),
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
        if args.command in {"render", "batch"}:
            return command_reserved(args.command)
        raise CliError("UNKNOWN_COMMAND", f"未知命令: {args.command}")
    except CliError as exc:
        payload = {"status": "failed", "code": exc.code, "message": exc.message}
        if exc.details:
            payload["issues"] = exc.details
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2 if exc.code in {"VALIDATION_FAILED", "NOT_IMPLEMENTED"} else 64


if __name__ == "__main__":
    sys.exit(main())
