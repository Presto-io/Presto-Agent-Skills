"""Fail-closed PDF/PNG evidence checks for immutable resume layout plans."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import fitz
from PIL import Image

from graduate_resume_cli import CliError
from graduate_resume_layout import FrozenResumePlan

LAYOUT_RENDER_MISMATCH = "LAYOUT_RENDER_MISMATCH"


def _fail(message: str) -> None:
    raise CliError(LAYOUT_RENDER_MISMATCH, message)


def _compact(value: str) -> str:
    return re.sub(r"\s+", "", value)


def _page_texts(pdf_path: Path) -> list[str]:
    if not pdf_path.read_bytes().startswith(b"%PDF-"):
        _fail("受控产物不是 PDF。")
    try:
        document = fitz.open(pdf_path)
        return [page.get_text("text") for page in document]
    except Exception as exc:
        raise CliError(LAYOUT_RENDER_MISMATCH, "无法提取受控 PDF 的逐页文字。") from exc


def _verify_png_bounds(png_path: Path, margins_mm: tuple[int, int, int, int]) -> None:
    try:
        with Image.open(png_path) as image:
            rgb = image.convert("RGB")
            width, height = rgb.size
            # Four corners are the per-page background contract. A 12-level tolerance
            # avoids antialiasing noise while still catching visible edge injection.
            corners = [rgb.getpixel(point) for point in ((0, 0), (width - 1, 0), (0, height - 1), (width - 1, height - 1))]
            background = tuple(sum(pixel[index] for pixel in corners) // len(corners) for index in range(3))
            left = round(margins_mm[2] / 210 * width)
            right = width - round(margins_mm[3] / 210 * width)
            top = round(margins_mm[0] / 297 * height)
            bottom = height - round(margins_mm[1] / 297 * height)
            for y in range(height):
                for x in range(width):
                    pixel = rgb.getpixel((x, y))
                    visible = max(abs(pixel[index] - background[index]) for index in range(3)) > 12
                    if visible and (x < left - 2 or x > right + 2 or y < top - 2 or y > bottom + 2):
                        _fail("PNG 出现安全区外可见内容。")
    except CliError:
        raise
    except Exception as exc:
        raise CliError(LAYOUT_RENDER_MISMATCH, "无法检查受控 PNG 页面边界。") from exc


def verify_rendered_layout(plan: FrozenResumePlan, facts: dict[str, Any], pdf_path: Path, png_paths: list[Path]) -> None:
    """Compare physical PDF pages to immutable plan assignments, never Typst input."""
    plan.validate(facts)
    page_texts = _page_texts(pdf_path)
    if len(page_texts) != plan.page_count or len(page_texts) not in (1, 2) or len(png_paths) != plan.page_count:
        _fail("PDF/PNG 页数与冻结计划不一致。")
    containers = {container.id: container for container in plan.containers}
    for index, page in enumerate(plan.pages):
        text = _compact(page_texts[index])
        if index == 0 and _compact(str(facts["candidate"]["name"])) not in text[:200]:
            _fail("首页没有以个人信息锚点开始。")
        if index > 0:
            first = containers[page.containers[0]]
            if not text.startswith(_compact(first.section)):
                _fail("第二页没有以合法模块标题开始。")
        for container_id in page.containers:
            container = containers[container_id]
            for _, value in container.fields:
                expected = _compact(str(value))
                if expected and expected not in text:
                    _fail("PDF 缺少冻结条目事实。")
            for other_index, other_text in enumerate(page_texts):
                if other_index == index:
                    continue
                other_expected = {
                    _compact(str(value))
                    for other_id in plan.pages[other_index].containers
                    for _, value in containers[other_id].fields
                }
                for _, value in container.fields:
                    expected = _compact(str(value))
                    if expected and expected in _compact(other_text) and expected not in other_expected:
                        _fail("PDF 将冻结条目事实放入错误页面。")
        _verify_png_bounds(png_paths[index], (14, 14, 15, 15))
