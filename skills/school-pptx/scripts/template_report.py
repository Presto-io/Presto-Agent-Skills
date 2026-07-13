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


def validate_manifest(data: dict, manifest_path: Path, template_path: Path, tolerance: int) -> dict[str, object]:
    failures: list[str] = []
    warnings: list[str] = []
    slots_evidence: list[dict[str, object]] = []
    layout_evidence: list[dict[str, object]] = []

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

    for layout_id in REQUIRED_LAYOUTS:
        layout = manifest_layouts.get(layout_id)
        if not isinstance(layout, dict):
            continue
        slot_list = layout.get("slots")
        if not isinstance(slot_list, list) or not slot_list:
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
            elif budget.get("overflow") not in ALLOWED_OVERFLOW:
                failures.append(f'槽位 "{layout_id}.{slot_id}" 的 overflow 不受支持。')
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
