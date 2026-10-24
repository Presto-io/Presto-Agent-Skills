"""Lossless field extraction for a standard personal-information sentence."""

from __future__ import annotations

import re


def paragraph_text(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    if text.endswith(("！", "？", "!", "?")):
        return text
    return text.rstrip("。.;；,，、:： ") + "。"


def personal_fields(summary: str) -> tuple[tuple[str, str], ...]:
    labelled = re.fullmatch(
        r"出生日期：([^；]+)；籍贯：([^；]+)；民族：([^；]+)；政治面貌：([^；。]+)。?",
        summary.strip(),
    )
    if labelled is not None:
        return tuple(zip(("出生日期", "籍贯", "民族", "政治面貌"), labelled.groups()))
    matched = re.fullmatch(
        r"\s*(男|女)，\s*(\d{4}年\d{1,2}月\d{1,2}日)出生，\s*([^，。]+族)，\s*籍贯([^，。]+)。?\s*",
        summary,
    )
    if matched is None:
        return ()
    return tuple(zip(("性别", "出生日期", "民族", "籍贯"), matched.groups()))
