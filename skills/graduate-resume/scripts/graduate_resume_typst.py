"""Mechanical Typst emission from a validated frozen resume plan only."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from graduate_resume_cli import CliError
from graduate_resume_layout import FrozenResumePlan, LAYOUT_PLAN_INVALID


def typst_content(value: str) -> str:
    """Escape every candidate-controlled character before it becomes Typst content."""
    return value.replace("\\", "\\\\").replace("#", "\\#").replace("[", "\\[").replace("]", "\\]").replace("\n", "#linebreak()")


def validate_emit_inputs(plan: FrozenResumePlan, facts: dict[str, Any]) -> None:
    if not isinstance(plan, FrozenResumePlan) or not isinstance(facts, dict) or facts.get("__verified__") is not True:
        raise CliError(LAYOUT_PLAN_INVALID, "Typst 发射只接受已验证事实和完整冻结计划。")
    plan.validate(facts)
    if plan.photo_mode == "no-photo" and (plan.photo is not None or plan.photo_slot is not None):
        raise CliError(LAYOUT_PLAN_INVALID, "无照片计划不得保留照片资源或槽位。")
    if plan.photo_mode == "photo" and (plan.photo is None or plan.photo_slot is None):
        raise CliError(LAYOUT_PLAN_INVALID, "照片计划缺少已验证逻辑媒体标识。")


def _container_text(container: Any) -> str:
    values = [value for _, value in container.fields]
    return " · ".join(values)


def emit_typst(plan: FrozenResumePlan, facts: dict[str, Any]) -> str:
    """Emit a fixed sequence; no pagination, sorting, measurement, or asset resolution occurs here."""
    validate_emit_inputs(plan, facts)
    template = Path(__file__).resolve().parent.parent / "templates" / "resume-themes.typ"
    if not template.is_file():
        raise CliError(LAYOUT_PLAN_INVALID, "受控 Typst 主题模板缺失。")
    by_id = {container.id: container for container in plan.containers}
    pages: list[str] = []
    for page in plan.pages:
        body: list[str] = []
        for container_id in page.containers:
            container = by_id[container_id]
            heading = typst_content(container.section)
            content = typst_content(_container_text(container))
            if container.kind == "list-entry":
                body.append(f'#resume.list-entry("{heading}", "{container.id}", [{content}])')
            else:
                body.append(f'#resume.fact-block("{heading}", [{content}])')
        pages.append("\n".join(body))
    prefix = '#import "resume-themes.typ" as resume\n'
    return prefix + "\n#pagebreak()\n".join(pages) + "\n"
