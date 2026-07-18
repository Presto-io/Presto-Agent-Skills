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
    for page_index, page in enumerate(plan.pages):
        body: list[str] = []
        previous_section: str | None = None
        for container_id in page.containers:
            container = by_id[container_id]
            heading = typst_content(container.section)
            content = typst_content(_container_text(container))
            if container.kind == "list-entry":
                show_heading = "true" if container.section != previous_section else "false"
                body.append(f'#resume.list-entry("{heading}", "{container.id}", [{content}], show-heading: {show_heading})')
            else:
                body.append(f'#resume.fact-block("{heading}", [{content}])')
            previous_section = container.section
        # The frozen plan owns the theme and photo decision.  The template only
        # realizes that decision; it never chooses another layout or asset.
        photo = "none"
        if page_index == 0 and plan.photo is not None:
            photo = f'image("{plan.photo.logical_path}", fit: "contain")'
        pages.append(
            f'#resume.theme-layout("{plan.theme_key}", photo: {photo})[\n'
            + "\n".join(body)
            + "\n]"
        )
    prefix = '#import "resume-themes.typ" as resume\n'
    return prefix + "\n#pagebreak()\n".join(pages) + "\n"
