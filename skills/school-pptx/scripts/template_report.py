from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZipFile

import yaml

REQUIRED_LAYOUTS = [
    "cover",
    "contents",
    "section",
    "title-content",
    "two-column",
    "image-text",
    "table",
    "timeline",
    "gallery",
    "code",
    "closing",
]
TEXT_BUDGET_KEYS = ["max_chars", "max_lines", "font_size_min", "font_size_max", "overflow"]
ALLOWED_OVERFLOW = {"shrink", "paginate", "fail"}
ALLOWED_EMPTY_SLOT = {"hide", "preserve", "fail"}
ALLOWED_CONTINUATION = {"none", "paginate", "repeat_header"}
ALLOWED_SCHEME_COLORS = {
    "dk1", "lt1", "dk2", "lt2", "accent1", "accent2", "accent3",
    "accent4", "accent5", "accent6", "hlink", "folHlink",
}
NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
}


def fail(message: str) -> None:
    print(message, file=sys.stderr)
    sys.exit(1)


def read_yaml(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        fail(f"manifest not found: {path}")
    except yaml.YAMLError as exc:
        fail(f"manifest yaml invalid: {exc}")
    if not isinstance(data, dict):
        fail("manifest root must be a mapping")
    return data


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def load_shape_index(template_path: Path) -> dict[str, dict[int, dict[str, object]]]:
    try:
        with ZipFile(template_path) as pptx:
            index: dict[str, dict[int, dict[str, object]]] = {}
            for name in pptx.namelist():
                if not name.startswith("ppt/slideLayouts/slideLayout") or not name.endswith(".xml"):
                    continue
                root = ET.fromstring(pptx.read(name))
                shapes: dict[int, dict[str, object]] = {}
                for shape in root.findall(".//p:sp", NS):
                    cnv = shape.find("./p:nvSpPr/p:cNvPr", NS)
                    if cnv is None or "id" not in cnv.attrib:
                        continue
                    xfrm = shape.find("./p:spPr/a:xfrm", NS)
                    geometry = None
                    if xfrm is not None:
                        off = xfrm.find("./a:off", NS)
                        ext = xfrm.find("./a:ext", NS)
                        if off is not None and ext is not None:
                            geometry = {
                                "x": int(off.attrib.get("x", "0")),
                                "y": int(off.attrib.get("y", "0")),
                                "width": int(ext.attrib.get("cx", "0")),
                                "height": int(ext.attrib.get("cy", "0")),
                            }
                    placeholder = shape.find("./p:nvSpPr/p:nvPr/p:ph", NS)
                    shapes[int(cnv.attrib["id"])] = {
                        "name": cnv.attrib.get("name", ""),
                        "geometry": geometry,
                        "type": placeholder.attrib.get("type", "") if placeholder is not None else "",
                        "idx": placeholder.attrib.get("idx", "") if placeholder is not None else "",
                    }
                index[name] = shapes
            return index
    except FileNotFoundError:
        fail(f"template not found: {template_path}")
    except (BadZipFile, ET.ParseError) as exc:
        fail(f"template pptx invalid: {exc}")


def slot_error(layout_id: str, slot_id: str, message: str) -> str:
    return message.format(layout=layout_id, slot=slot_id)


def valid_geometry(value: object) -> bool:
    return (
        isinstance(value, dict)
        and set(value) == {"x", "y", "width", "height"}
        and all(isinstance(value[key], int) and value[key] >= 0 for key in value)
        and value["width"] > 0
        and value["height"] > 0
    )


def contains(parent: dict, child: dict) -> bool:
    return (
        child["x"] >= parent["x"]
        and child["y"] >= parent["y"]
        and child["x"] + child["width"] <= parent["x"] + parent["width"]
        and child["y"] + child["height"] <= parent["y"] + parent["height"]
    )


def overlaps(first: dict, second: dict) -> bool:
    return not (
        first["x"] + first["width"] <= second["x"]
        or second["x"] + second["width"] <= first["x"]
        or first["y"] + first["height"] <= second["y"]
        or second["y"] + second["height"] <= first["y"]
    )


def validate_text_budget(value: object) -> bool:
    return (
        isinstance(value, dict)
        and all(key in value for key in TEXT_BUDGET_KEYS)
        and all(isinstance(value[key], int) and value[key] >= 0 for key in TEXT_BUDGET_KEYS[:-1])
        and value["font_size_min"] <= value["font_size_max"]
        and value["overflow"] in ALLOWED_OVERFLOW
    )


def validate_subregions(
    owner: str,
    parent: dict,
    regions: object,
    failures: list[str],
    *,
    local_coordinates: bool = False,
) -> list[dict[str, object]]:
    evidence: list[dict[str, object]] = []
    if not isinstance(regions, dict) or not regions:
        failures.append(f'区域 "{owner}" 缺少 manifest 所有的子区域。')
        return evidence
    for name, region in regions.items():
        if not isinstance(region, dict) or not valid_geometry(region.get("geometry")):
            failures.append(f'子区域 "{owner}.{name}" 的 geometry 必须是非负 EMU 矩形。')
            continue
        geometry = region["geometry"]
        container = parent
        if local_coordinates:
            container = {"x": 0, "y": 0, "width": parent["width"], "height": parent["height"]}
        if not contains(container, geometry):
            failures.append(f'子区域 "{owner}.{name}" 超出父区域。')
        budget = region.get("text_budget")
        if budget is not None and not validate_text_budget(budget):
            failures.append(f'子区域 "{owner}.{name}" 的文本预算无效。')
        evidence.append({"owner": owner, "name": str(name), "geometry": geometry, "text_budget": budget})
    return evidence


def validate_manifest(data: dict, manifest_path: Path, template_path: Path, tolerance: int) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    slots_evidence: list[dict[str, object]] = []
    layout_evidence: list[dict[str, object]] = []
    renderer_regions: list[dict[str, object]] = []

    available = data.get("available_themes") or []
    theme_id = data.get("theme_id")
    if theme_id != "standard-school":
        failures.append('未知主题 "{}"。可用主题：{}。'.format(theme_id, "、".join(map(str, available))))
    if available != ["standard-school"]:
        failures.append("available_themes must contain only standard-school")

    manifest_layouts = data.get("layouts")
    if not isinstance(manifest_layouts, dict):
        failures.append("layouts must be a mapping")
        manifest_layouts = {}

    layout_ids = set(manifest_layouts.keys())
    for layout_id in REQUIRED_LAYOUTS:
        if layout_id not in layout_ids:
            failures.append(f'模板缺少布局 "{layout_id}"。Phase 41 必须覆盖 11 个受控布局。')
    for layout_id in sorted(layout_ids - set(REQUIRED_LAYOUTS)):
        failures.append(f'模板包含不受控布局 "{layout_id}"。Phase 41 只允许 11 个受控布局。')

    shape_index = load_shape_index(template_path)

    highlight = data.get("inline_styles", {}).get("highlight", {}) if isinstance(data.get("inline_styles"), dict) else {}
    scheme_color = highlight.get("scheme_color") if isinstance(highlight, dict) else None
    if scheme_color not in ALLOWED_SCHEME_COLORS:
        failures.append("inline_styles.highlight.scheme_color 必须引用受控 PowerPoint theme scheme token。")

    for layout_id in REQUIRED_LAYOUTS:
        layout = manifest_layouts.get(layout_id)
        if not isinstance(layout, dict):
            continue
        slot_list = layout.get("slots")
        pptx_layout = layout.get("pptx_layout")
        if not isinstance(pptx_layout, str) or pptx_layout not in shape_index:
            failures.append(f'布局 "{layout_id}" 的 PPTX part path 不存在。')
        fixed_template_page = layout.get("fixed_template_page") is True
        if not isinstance(slot_list, list) or (not slot_list and not fixed_template_page):
            failures.append(f'模板缺少布局 "{layout_id}"。Phase 41 必须覆盖 11 个受控布局。')
            slot_list = []
        required_slots = layout.get("required_slots") or []
        slot_ids = [slot.get("id") for slot in slot_list if isinstance(slot, dict)]
        for required_slot in required_slots:
            if required_slot not in slot_ids:
                failures.append(f'布局 "{layout_id}" 缺少槽位 "{required_slot}"。请恢复占位符映射或更新 manifest。')
        seen: set[str] = set()
        for slot in slot_list:
            if not isinstance(slot, dict):
                failures.append(f'布局 "{layout_id}" 存在非法槽位。请保留对象格式。')
                continue
            slot_id = str(slot.get("id", ""))
            if slot_id in seen:
                failures.append(f'布局 "{layout_id}" 存在重复槽位 "{slot_id}"。请保留唯一语义槽位 id。')
            seen.add(slot_id)
            placeholder = slot.get("placeholder") if isinstance(slot.get("placeholder"), dict) else {}
            file_name = str(placeholder.get("file", layout.get("pptx_layout", "")))
            shape_id = placeholder.get("shape_id")
            shape = shape_index.get(file_name, {}).get(int(shape_id)) if isinstance(shape_id, int) else None
            if not shape or (placeholder.get("name") and placeholder.get("name") != shape.get("name")):
                failures.append(f'槽位 "{layout_id}.{slot_id}" 找不到对应 PPTX 占位符。请勿删除或替换映射锚点。')
            expected_geometry = slot.get("geometry") if isinstance(slot.get("geometry"), dict) else None
            actual_geometry = shape.get("geometry") if shape else None
            if not expected_geometry or not actual_geometry:
                failures.append(f'槽位 "{layout_id}.{slot_id}" 的 PPTX 几何与 manifest 不一致。请同步 manifest 或重新调整模板。')
            elif any(abs(int(expected_geometry[key]) - int(actual_geometry[key])) > tolerance for key in ("x", "y", "width", "height")):
                failures.append(f'槽位 "{layout_id}.{slot_id}" 的 PPTX 几何与 manifest 不一致。请同步 manifest 或重新调整模板。')
            budget = slot.get("text_budget")
            if not isinstance(budget, dict) or any(key not in budget for key in TEXT_BUDGET_KEYS):
                failures.append(f'槽位 "{layout_id}.{slot_id}" 的文本预算不完整。必须包含 max_chars、max_lines、font_size_min、font_size_max 和 overflow。')
            elif not validate_text_budget(budget):
                failures.append(f'槽位 "{layout_id}.{slot_id}" 的文本预算类型、范围或 overflow 不受支持。')
            if slot.get("empty_slot") not in ALLOWED_EMPTY_SLOT:
                failures.append(f'槽位 "{layout_id}.{slot_id}" 的 empty_slot 不受支持。')
            if slot.get("continuation") not in ALLOWED_CONTINUATION:
                failures.append(f'槽位 "{layout_id}.{slot_id}" 的 continuation 不受支持。')
            slots_evidence.append(
                {
                    "layout": layout_id,
                    "slot": slot_id,
                    "kind": slot.get("kind"),
                    "placeholder_file": file_name,
                    "shape_id": shape_id,
                    "geometry": expected_geometry,
                    "text_budget": budget,
                    "empty_slot": slot.get("empty_slot"),
                    "continuation": slot.get("continuation"),
                }
            )

            if layout_id == "table" and slot_id == "table":
                table_regions = validate_subregions(
                    "table.table", expected_geometry or {}, slot.get("subregions"), failures
                ) if valid_geometry(expected_geometry) else []
                renderer_regions.extend(table_regions)
                table_name = next((item for item in table_regions if item["name"] == "table_name"), None)
                raw_table_name = slot.get("subregions", {}).get("table_name", {}) if isinstance(slot.get("subregions"), dict) else {}
                if table_name is None or raw_table_name.get("empty_slot") != "preserve":
                    failures.append("table.table_name 必须保留空编辑槽。")
                if table_name is None or not validate_text_budget(raw_table_name.get("text_budget")):
                    failures.append("table.table_name 必须拥有完整文字预算。")

            if layout_id == "timeline" and slot_id == "timeline_items" and valid_geometry(expected_geometry):
                timeline_regions = validate_subregions(
                    "timeline.timeline_items", expected_geometry, slot.get("subregions"), failures
                )
                renderer_regions.extend(timeline_regions)
                if {item["name"] for item in timeline_regions} != {"axis", "node_band"}:
                    failures.append("timeline 必须完整定义 axis 与 node_band 子区域。")
                node_template = slot.get("node_template")
                if not isinstance(node_template, dict) or not valid_geometry(node_template.get("geometry")):
                    failures.append("timeline.node_template 必须定义非负本地 geometry。")
                else:
                    node_regions = validate_subregions(
                        "timeline.node_template",
                        node_template["geometry"],
                        node_template.get("subregions"),
                        failures,
                        local_coordinates=True,
                    )
                    renderer_regions.extend(node_regions)
                    if {item["name"] for item in node_regions} != {"marker", "time", "title", "description"}:
                        failures.append("timeline node 必须完整定义 marker/time/title/description。")

            if layout_id == "gallery" and slot_id == "gallery_items" and valid_geometry(expected_geometry):
                presets = slot.get("item_presets")
                if not isinstance(presets, dict) or set(presets) != {1, 2, 3, 4}:
                    failures.append("gallery.item_presets 必须完整定义 1/2/3/4 项。")
                else:
                    for count in range(1, 5):
                        cards = presets[count]
                        if not isinstance(cards, list) or len(cards) != count:
                            failures.append(f"gallery {count} 项 preset 的卡片数量不正确。")
                            continue
                        card_geometries: list[dict] = []
                        for index, card in enumerate(cards, start=1):
                            if not isinstance(card, dict) or any(not valid_geometry(card.get(key)) for key in ("card", "picture", "caption")):
                                failures.append(f"gallery {count} 项 preset 第 {index} 张卡片结构无效。")
                                continue
                            card_geometry = card["card"]
                            if not contains(expected_geometry, card_geometry):
                                failures.append(f"gallery {count} 项 preset 第 {index} 张卡片越界。")
                            if not contains(card_geometry, card["picture"]) or not contains(card_geometry, card["caption"]):
                                failures.append(f"gallery {count} 项 preset 第 {index} 张图片或图注越界。")
                            card_geometries.append(card_geometry)
                            renderer_regions.append({"owner": f"gallery.preset.{count}", "name": str(index), "geometry": card_geometry})
                        for first in range(len(card_geometries)):
                            for second in range(first + 1, len(card_geometries)):
                                if overlaps(card_geometries[first], card_geometries[second]):
                                    failures.append(f"gallery {count} 项 preset 卡片发生重叠。")
        layout_evidence.append(
            {
                "id": layout_id,
                "label": layout.get("label"),
                "pptx_layout": layout.get("pptx_layout"),
                "required_slots": required_slots,
                "slot_count": len(slot_list),
            }
        )

    return {
        "theme_id": theme_id,
        "template_path": str(template_path),
        "manifest_path": str(manifest_path),
        "layouts": layout_evidence,
        "slots": slots_evidence,
        "renderer_contract": {
            "closing_part_path": manifest_layouts.get("closing", {}).get("pptx_layout"),
            "highlight_scheme_color": scheme_color,
            "gallery_caption_empty_slot": next(
                (item["empty_slot"] for item in slots_evidence if item["layout"] == "gallery" and item["slot"] == "caption"),
                None,
            ),
            "regions": renderer_regions,
            "cover_subtitle_budget": next(
                (item["text_budget"] for item in slots_evidence if item["layout"] == "cover" and item["slot"] == "subtitle"),
                None,
            ),
        },
        "failures": failures,
        "warnings": warnings,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def markdown_report(evidence: dict[str, object], out_json: Path | None) -> str:
    failures = evidence["failures"]
    warnings = evidence["warnings"]
    lines = [
        "# school-pptx 模板报告",
        "",
        "## 校验结果",
        "",
        "PASS" if not failures else "FAIL",
        "",
        "## 主题",
        "",
        f"- 当前主题：`{evidence['theme_id']}`",
        "- 可用主题：`standard-school`",
        f"- 模板：`{evidence['template_path']}`",
        f"- Manifest：`{evidence['manifest_path']}`",
        "",
        "## 布局覆盖",
        "",
        "| 布局 | PPTX 映射 | 槽位数 |",
        "|------|-----------|--------|",
    ]
    for layout in evidence["layouts"]:
        lines.append(f"| `{layout['id']}` | `{layout['pptx_layout']}` | {layout['slot_count']} |")
    lines.extend(["", "## 槽位映射", "", "| 布局 | 槽位 | 类型 | 占位符 |", "|------|------|------|--------|"])
    for slot in evidence["slots"]:
        lines.append(
            f"| `{slot['layout']}` | `{slot['slot']}` | `{slot['kind']}` | `{slot['placeholder_file']}#{slot['shape_id']}` |"
        )
    lines.extend(["", "## 文本预算", "", "| 布局 | 槽位 | max_chars | max_lines | overflow |", "|------|------|-----------|-----------|----------|"])
    for slot in evidence["slots"]:
        budget = slot.get("text_budget") or {}
        lines.append(
            f"| `{slot['layout']}` | `{slot['slot']}` | {budget.get('max_chars')} | {budget.get('max_lines')} | `{budget.get('overflow')}` |"
        )
    contract = evidence["renderer_contract"]
    lines.extend(
        [
            "",
            "## Phase 43 渲染契约",
            "",
            f"- closing part path：`{contract['closing_part_path']}`",
            f"- highlight theme scheme：`{contract['highlight_scheme_color']}`",
            f"- gallery caption empty slot：`{contract['gallery_caption_empty_slot']}`",
            f"- 动态子区域证据：{len(contract['regions'])} 项",
            f"- cover subtitle budget：`max_chars={contract['cover_subtitle_budget']['max_chars']}`、`max_lines={contract['cover_subtitle_budget']['max_lines']}`",
        ]
    )
    lines.extend(
        [
            "",
            "## 手动编辑守则",
            "",
            "- 允许：drag and resize mapped placeholders；add decorative template-owned shapes；refine template-owned typography, colors, and polish。",
            "- 禁止：delete mapped placeholders；replace mapped placeholders with ordinary shapes；remove mapping anchors；duplicate slots without unique ids；add content slots without manifest entries。",
            "- 编辑后必须重新运行 `template-report --theme standard-school --out-md ... --out-json ...`。",
            "",
            "## 校验结果详情",
            "",
        ]
    )
    if failures:
        lines.extend(f"- FAIL: {item}" for item in failures)
    else:
        lines.append("- PASS: manifest、布局、槽位、占位符、几何和文本预算一致。")
    if warnings:
        lines.extend(f"- WARNING: {item}" for item in warnings)
    if out_json:
        lines.extend(["", f"JSON evidence path: `{out_json}`"])
    return "\n".join(lines) + "\n"


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="school-pptx.sh template-report")
    parser.add_argument("skill_dir")
    parser.add_argument("--theme", required=True)
    parser.add_argument("--out-md")
    parser.add_argument("--out-json")
    parser.add_argument("--manifest")
    parser.add_argument("--template")
    parser.add_argument("--geometry-tolerance-emu", type=int)
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    skill_dir = Path(args.skill_dir).resolve()
    manifest_path = Path(args.manifest).resolve() if args.manifest else skill_dir / "templates" / "standard-school.manifest.yaml"
    data = read_yaml(manifest_path)
    available = data.get("available_themes") or []
    if args.theme not in available:
        print(f'未知主题 "{args.theme}"。可用主题：{"、".join(map(str, available))}。', file=sys.stderr)
        return 1
    template_path = (
        Path(args.template).resolve()
        if args.template
        else skill_dir / "templates" / str(data.get("template", {}).get("path", "standard-school.pptx"))
    )
    tolerance = args.geometry_tolerance_emu
    if tolerance is None:
        tolerance = int(data.get("template", {}).get("geometry_tolerance_emu", 2000))
    evidence = validate_manifest(data, manifest_path, template_path, tolerance)
    out_json = Path(args.out_json).resolve() if args.out_json else None
    out_md = Path(args.out_md).resolve() if args.out_md else None
    if out_json:
        write_text(out_json, json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    if out_md:
        write_text(out_md, markdown_report(evidence, out_json))
    for failure in evidence["failures"]:
        print(failure, file=sys.stderr)
    return 1 if evidence["failures"] else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
