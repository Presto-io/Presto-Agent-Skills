#!/usr/bin/env python3
"""Task-local regression gates for the Phase 43 renderer contract and model."""

from __future__ import annotations

import argparse
import ast
import copy
import json
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET
from zipfile import BadZipFile, ZIP_DEFLATED, ZipFile

import pptx_paginate
import template_report
from markdown_contract import load_manifest, parse_document


SKILL_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
MANIFEST_PATH = SKILL_DIR / "templates" / "standard-school.manifest.yaml"
TEMPLATE_PATH = SKILL_DIR / "templates" / "standard-school.pptx"
MAX_ZIP_ENTRIES = 256
MAX_ZIP_ENTRY_BYTES = 4 * 1024 * 1024
MAX_ZIP_TOTAL_BYTES = 32 * 1024 * 1024
FORBIDDEN_XML_MARKERS = (b"<!DOCTYPE", b"<!ENTITY")
PRESENTATION_NS = {"p": "http://schemas.openxmlformats.org/presentationml/2006/main"}


class GateFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise GateFailure(message)


def safe_package_entries(path: Path) -> dict[str, bytes]:
    try:
        with ZipFile(path) as package:
            infos = package.infolist()
            require(len(infos) <= MAX_ZIP_ENTRIES, "ZIP_ENTRY_LIMIT")
            names: set[str] = set()
            total = 0
            result: dict[str, bytes] = {}
            for info in infos:
                name = info.filename
                pure = PurePosixPath(name)
                require(not pure.is_absolute() and ".." not in pure.parts, "ZIP_PATH_INVALID")
                require(name not in names, "ZIP_DUPLICATE_ENTRY")
                names.add(name)
                require(info.file_size <= MAX_ZIP_ENTRY_BYTES, "ZIP_ENTRY_SIZE_LIMIT")
                total += info.file_size
                require(total <= MAX_ZIP_TOTAL_BYTES, "ZIP_TOTAL_SIZE_LIMIT")
                if name.endswith(".xml") or name.endswith(".rels"):
                    payload = package.read(info)
                    upper = payload.upper()
                    require(not any(marker in upper for marker in FORBIDDEN_XML_MARKERS), "XML_EXTERNAL_ENTITY_FORBIDDEN")
                    try:
                        ET.fromstring(payload)
                    except ET.ParseError as exc:
                        raise GateFailure("XML_MALFORMED") from exc
                    result[name] = payload
            return result
    except (BadZipFile, OSError) as exc:
        raise GateFailure("ZIP_MALFORMED") from exc


def run_template_report(workdir: Path) -> dict[str, object]:
    report_json = workdir / "template-report.json"
    report_md = workdir / "template-report.md"
    completed = subprocess.run(
        [
            str(SCRIPTS_DIR / "school-pptx.sh"),
            "template-report",
            "--theme",
            "standard-school",
            "--out-md",
            str(report_md),
            "--out-json",
            str(report_json),
        ],
        cwd=SKILL_DIR.parent.parent,
        text=True,
        capture_output=True,
        timeout=30,
        check=False,
    )
    require(completed.returncode == 0, "controlled template-report failed")
    require("Traceback" not in completed.stdout + completed.stderr, "template-report leaked traceback")
    data = json.loads(report_json.read_text(encoding="utf-8"))
    require(not data.get("failures"), "template-report contains failures")
    require(report_md.is_file(), "template-report markdown evidence missing")
    return data


def manifest_renderer_contract_gate(workdir: Path) -> dict[str, object]:
    report = run_template_report(workdir)
    manifest = template_report.read_yaml(MANIFEST_PATH)
    layouts = manifest["layouts"]
    table = next(slot for slot in layouts["table"]["slots"] if slot["id"] == "table")
    gallery_items = next(slot for slot in layouts["gallery"]["slots"] if slot["id"] == "gallery_items")
    gallery_caption = next(slot for slot in layouts["gallery"]["slots"] if slot["id"] == "caption")
    timeline = next(slot for slot in layouts["timeline"]["slots"] if slot["id"] == "timeline_items")
    table_name = table["subregions"]["table_name"]
    require(table_name["empty_slot"] == "preserve", "D-14 table_name empty slot not preserved")
    require(gallery_caption["empty_slot"] == "preserve", "D-14 gallery caption empty slot not preserved")
    require(template_report.validate_text_budget(table_name["text_budget"]), "table_name budget invalid")
    require(set(gallery_items["item_presets"]) == {1, 2, 3, 4}, "gallery presets incomplete")
    require(set(timeline["subregions"]) == {"axis", "node_band"}, "timeline subdivisions incomplete")
    require(
        set(timeline["node_template"]["subregions"]) == {"marker", "time", "title", "description"},
        "timeline node subdivisions incomplete",
    )
    require(manifest["inline_styles"]["highlight"]["scheme_color"] in template_report.ALLOWED_SCHEME_COLORS,
            "highlight scheme token invalid")
    require(layouts["closing"]["pptx_layout"] == "ppt/slideLayouts/slideLayout7.xml", "closing part path invalid")
    require(len(report["layouts"]) == 11 and len(report["slots"]) >= 1, "layout regression")

    invalid = copy.deepcopy(manifest)
    invalid_gallery = next(slot for slot in invalid["layouts"]["gallery"]["slots"] if slot["id"] == "gallery_items")
    invalid_gallery["item_presets"][1][0]["card"]["x"] = invalid_gallery["geometry"]["x"] - 1
    bounded = template_report.validate_manifest(invalid, MANIFEST_PATH, TEMPLATE_PATH, 2000)
    require(any("越界" in item for item in bounded["failures"]), "out-of-bounds preset did not fail")
    return {
        "layout_count": len(report["layouts"]),
        "closing_part_path": layouts["closing"]["pptx_layout"],
        "highlight_scheme_color": manifest["inline_styles"]["highlight"]["scheme_color"],
        "gallery_presets": sorted(gallery_items["item_presets"]),
        "table_name_empty_slot": table_name["empty_slot"],
    }


def local_import_graph(root: Path) -> set[Path]:
    pending = [root]
    visited: set[Path] = set()
    while pending:
        path = pending.pop()
        if path in visited:
            continue
        visited.add(path)
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            names: list[str] = []
            if isinstance(node, ast.Import):
                names.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                names.append(node.module)
            for name in names:
                require(name != "pptx" and not name.startswith("pptx."), "pptx import boundary violated")
                candidate = SCRIPTS_DIR / f"{name.split('.')[0]}.py"
                if candidate.is_file():
                    pending.append(candidate)
    return visited


def model_determinism_gate(workdir: Path) -> dict[str, object]:
    del workdir
    first = pptx_paginate.run_contract_model_self_check()
    second = pptx_paginate.run_contract_model_self_check()
    require(first == second, "model self-check evidence is not deterministic")
    require(first["model_equal"] is True and first["model_immutable"] is True, "frozen model contract failed")
    graph = local_import_graph(SCRIPTS_DIR / "pptx_paginate.py")
    return {"model_equal": True, "model_immutable": True, "import_graph": sorted(path.name for path in graph)}


def expect_package_failure(path: Path, expected: str) -> None:
    try:
        safe_package_entries(path)
    except GateFailure as exc:
        require(str(exc) == expected, f"expected {expected}, got {exc}")
        return
    raise GateFailure(f"negative package did not fail: {expected}")


def measurement_gate(workdir: Path) -> dict[str, object]:
    evidence = pptx_paginate.run_contract_model_self_check()
    vectors = evidence["vectors"]
    require(vectors["explicit_newline"]["display_lines"] == 3, "explicit newline vector failed")
    require(vectors["font_clamp"]["font_size"] == 18.0, "font clamp vector failed")
    try:
        pptx_paginate.TextMeasure().measure(
            "测" * (pptx_paginate.MAX_TEXT_BYTES + 1),
            width_emu=1_270_000,
            font_size=16,
            font_size_min=12,
            font_size_max=18,
        )
    except ValueError as exc:
        require(str(exc) == "text exceeds bounded measurement input", "unbounded text failure")
    else:
        raise GateFailure("oversized text did not fail")

    controlled = safe_package_entries(TEMPLATE_PATH)
    presentation = ET.fromstring(controlled["ppt/presentation.xml"])
    seed_count = len(presentation.findall(".//p:sldId", PRESENTATION_NS))
    require(seed_count == 5, "controlled template seed count is not 5")

    malformed = workdir / "malformed.pptx"
    malformed.write_bytes(b"not-a-zip")
    expect_package_failure(malformed, "ZIP_MALFORMED")

    xxe = workdir / "xxe.pptx"
    with ZipFile(xxe, "w", ZIP_DEFLATED) as package:
        package.writestr("ppt/presentation.xml", '<!DOCTYPE x [<!ENTITY e SYSTEM "file:///etc/passwd">]><x>&e;</x>')
    expect_package_failure(xxe, "XML_EXTERNAL_ENTITY_FORBIDDEN")

    malformed_xml = workdir / "malformed-xml.pptx"
    with ZipFile(malformed_xml, "w", ZIP_DEFLATED) as package:
        package.writestr("ppt/presentation.xml", "<x>")
    expect_package_failure(malformed_xml, "XML_MALFORMED")

    bomb = workdir / "entry-bomb.pptx"
    with ZipFile(bomb, "w", ZIP_DEFLATED) as package:
        package.writestr("ppt/presentation.xml", b" " * (MAX_ZIP_ENTRY_BYTES + 1))
    expect_package_failure(bomb, "ZIP_ENTRY_SIZE_LIMIT")
    return {"seed_slide_count": seed_count, "vectors": sorted(vectors), "security_negative_cases": 4}


GATES = {
    "manifest_renderer_contract_gate": manifest_renderer_contract_gate,
    "model_determinism_gate": model_determinism_gate,
    "measurement_gate": measurement_gate,
}


def _minimal_document(slides: list[dict[str, object]]) -> dict[str, object]:
    return {
        "document_title": "测试文稿",
        "logical_slides": slides,
        "implicit_slides": [{"layout": "closing", "position": "end_of_deck", "fixed_template_page": True}],
        "contents_entries": [],
    }


def pagination_text_code_gate(workdir: Path) -> dict[str, object]:
    del workdir
    manifest = load_manifest(SKILL_DIR)
    sentence = "第一句完整结束。第二句仍然很长！第三句结束？"
    sentence_parts = pptx_paginate.split_semantic_text(sentence, 12)
    require("".join(sentence_parts) == sentence and sentence_parts[0].endswith("。"), "D-02 sentence split")
    weak = "前半部分，后半部分仍然很长"
    weak_parts = pptx_paginate.split_semantic_text(weak, 6)
    require("".join(weak_parts) == weak and weak_parts[0].endswith("，"), "D-02 weak punctuation split")
    unicode_text = "A\u0301👩\u200d🏭️B"
    unicode_parts = pptx_paginate.split_semantic_text(unicode_text, 1)
    require("".join(unicode_parts) == unicode_text and unicode_parts[0] == "A\u0301", "D-02 grapheme split")

    long_code_line = "x = '" + "中" * 2000 + "'"
    code_text = "line_1\n" + "\n".join(f"line_{index}" for index in range(2, 28)) + "\n" + long_code_line
    document = _minimal_document([
        {"layout": "title-content", "title": "正文", "source_line": 1, "notes": None, "blocks": [
            {"kind": "paragraph", "source_line": 2, "heading": "同一标题", "text": "短块完整保留。"},
            {"kind": "paragraph", "source_line": 3, "heading": "同一标题", "text": "这是一个很长的句子。" * 80},
        ]},
        {"layout": "code", "title": "代码", "source_line": 10, "notes": None, "blocks": [
            {"kind": "code", "source_line": 11, "heading": "源码", "language": "python", "text": code_text},
        ]},
    ])
    first = pptx_paginate.build_deck_plan(document, manifest)
    second = pptx_paginate.build_deck_plan(document, manifest)
    require(first == second, "pagination determinism")
    text_slides = [slide for slide in first.slides if slide.layout == "title-content"]
    require(text_slides[0].fragments[0].text == "短块完整保留。", "D-01 complete block split")
    require(all(slide.title == "正文" for slide in text_slides), "D-04 repeated title")
    require(all("续" not in slide.title for slide in first.slides), "D-05 visible continuation marker")
    headings = [fragment.heading for slide in text_slides for fragment in slide.fragments]
    require(all(heading == "同一标题" for heading in headings), "D-04 block heading changed")
    code_fragments = [fragment for slide in first.slides for fragment in slide.fragments if fragment.kind == "code"]
    require("\n".join(fragment.text or "" for fragment in code_fragments) == code_text, "D-03 code round trip")
    require(all(fragment.text is not None for fragment in code_fragments), "D-03 code fragment")
    require(any(d.code == "CODE_LINE_OVERFLOW" for d in first.diagnostics), "CODE_LINE_OVERFLOW missing")
    return {
        "sentence_parts": len(sentence_parts), "weak_parts": len(weak_parts),
        "unicode_parts": len(unicode_parts), "physical_slides": len(first.slides),
        "code_fragments": len(code_fragments),
    }


def pagination_structured_gate(workdir: Path) -> dict[str, object]:
    del workdir
    manifest = load_manifest(SKILL_DIR)
    rows = [[f"模块{index}", "说明" * (index % 4 + 3), "成果完整"] for index in range(1, 24)]
    timeline_rows = [[f"第{index}月", f"节点{index}", "阶段说明" * 14] for index in range(1, 16)]
    entries = [f"目录项目 {index} " + ("长标题" * (index % 3)) for index in range(1, 15)]
    document = _minimal_document([
        {"layout": "table", "title": "表格页", "source_line": 1, "notes": None, "blocks": [{
            "kind": "table", "source_line": 2, "heading": "原表名", "table_title": "原表名",
            "headers": ["模块", "说明", "成果"], "rows": rows,
        }]},
        {"layout": "table", "title": "无名表", "source_line": 30, "notes": None, "blocks": [{
            "kind": "table", "source_line": 31, "heading": None, "table_title": None,
            "headers": ["模块", "说明", "成果"], "rows": rows,
        }]},
        {"layout": "timeline", "title": "时间线", "source_line": 60, "notes": None, "blocks": [{
            "kind": "timeline", "source_line": 61, "heading": None,
            "headers": ["时间", "标题", "说明"], "rows": timeline_rows,
        }]},
        {"layout": "contents", "title": None, "source_line": 90, "notes": None, "blocks": []},
    ])
    document["contents_entries"] = entries
    plan = pptx_paginate.build_deck_plan(document, manifest)
    table_slides = [slide for slide in plan.slides if slide.logical_index == 0]
    require(len(table_slides) > 1, "D-07 table did not paginate")
    require(all(slide.fragments[0].rows[0] == ("模块", "说明", "成果") for slide in table_slides), "D-07 header")
    require(sum(len(slide.fragments[0].rows) - 1 for slide in table_slides) == len(rows), "D-08 row loss")
    names = [dict(slide.fragments[0].metadata)["table_name"] for slide in table_slides]
    require(names[0] == "原表名" and all(name == "原表名（续）" for name in names[1:]), "D-06 table name")
    unnamed = [slide for slide in plan.slides if slide.logical_index == 1]
    require(all(dict(slide.fragments[0].metadata)["table_name"] == "" for slide in unnamed), "D-06 empty table name")

    # Demonstrate that a larger size can remove a visible wrapped orphan.
    measure = pptx_paginate.TextMeasure()
    orphan_vector = None
    for length in range(8, 160):
        value = "测" * length
        small = pptx_paginate._wrapped_cell(value, 900_000, 12.0, measure)[1]
        large = pptx_paginate._wrapped_cell(value, 900_000, 18.0, measure)[1]
        if small and not large:
            orphan_vector = length
            break
    require(orphan_vector is not None, "D-08 larger-font orphan vector missing")

    timeline = [slide for slide in plan.slides if slide.logical_index == 2]
    counts = [len(slide.fragments[0].rows) for slide in timeline]
    require(len(timeline) >= 3 and min(counts) >= 3 and max(counts) - min(counts) <= 1, "D-09 global timeline balance")
    flattened = [row[1] for slide in timeline for row in slide.fragments[0].rows]
    require(flattened == [row[1] for row in timeline_rows], "D-09 timeline order")
    infeasible_document = _minimal_document([{
        "layout": "timeline", "title": "不可行", "source_line": 1, "notes": None, "blocks": [{
            "kind": "timeline", "source_line": 2, "heading": None,
            "headers": ["时间", "标题", "说明"],
            "rows": [[str(index), f"节点{index}", "极高说明" * 400] for index in range(5)],
        }],
    }])
    infeasible = pptx_paginate.build_deck_plan(infeasible_document, manifest)
    require(any(item.code == "TIMELINE_BALANCE_INFEASIBLE" for item in infeasible.diagnostics),
            "D-09 infeasible diagnostic")

    contents = [slide for slide in plan.slides if slide.logical_index == 3]
    content_counts = [len(slide.fragments[0].items) for slide in contents]
    require(all(slide.title == "目录" for slide in contents), "D-10 contents title")
    require(max(content_counts) - min(content_counts) <= 1, "D-10 contents count balance")
    require([item for slide in contents for item in slide.fragments[0].items] == entries, "D-10 contents order")
    try:
        pptx_paginate.ordered_contiguous_partition([1.0] * 300, 10.0)
    except ValueError as exc:
        require(str(exc) == "partition state budget exceeded", "bounded partition diagnostic")
    else:
        raise GateFailure("partition resource limit missing")
    return {
        "table_pages": len(table_slides), "table_font": dict(table_slides[0].selected_font_sizes)["table"],
        "orphan_vector": orphan_vector, "timeline_counts": counts, "contents_counts": content_counts,
    }


GATES["pagination-text-code"] = pagination_text_code_gate
GATES["pagination-structured"] = pagination_structured_gate


def run_contract_model() -> dict[str, object]:
    names = [name for name in GATES if not name.startswith("pagination-")]
    require(len(names) == len(set(names)) == 3, "gate registry must contain three unique contract gates")
    called: list[str] = []
    evidence: dict[str, object] = {}
    with tempfile.TemporaryDirectory(prefix="school-pptx-contract-model-") as temporary:
        root = Path(temporary)
        for name in names:
            gate = GATES[name]
            gate_dir = root / name
            gate_dir.mkdir()
            evidence[name] = gate(gate_dir)
            called.append(name)
            print(f"PASS {name}")
    require(called == names, "gate registry execution was skipped or reordered")
    return evidence


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="verify_pptx_renderer.py")
    parser.add_argument("gate", choices=["contract-model", "pagination", *GATES])
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.gate == "contract-model":
            evidence = run_contract_model()
        elif args.gate == "pagination":
            names = [name for name in GATES if name.startswith("pagination-")]
            evidence = {}
            with tempfile.TemporaryDirectory(prefix="school-pptx-pagination-") as temporary:
                root = Path(temporary)
                for name in names:
                    evidence[name] = GATES[name](root)
                    print(f"PASS {name}")
        else:
            with tempfile.TemporaryDirectory(prefix=f"school-pptx-{args.gate}-") as temporary:
                evidence = {args.gate: GATES[args.gate](Path(temporary))}
                print(f"PASS {args.gate}")
        print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))
        return 0
    except (GateFailure, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"FAIL {args.gate}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
