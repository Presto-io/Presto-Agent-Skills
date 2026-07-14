#!/usr/bin/env python3
"""Task-local regression gates for the Phase 43 renderer contract and model."""

from __future__ import annotations

import argparse
import ast
import base64
import contextlib
import copy
import fcntl
import hashlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zlib
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
PUBLIC_CLI = SCRIPTS_DIR / "school-pptx.sh"
FIXTURE_PATH = SKILL_DIR / "fixtures" / "school-pptx-full.md"
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


def _image(index: int, caption: str | None = None) -> dict[str, object]:
    return {
        "kind": "image", "source_line": index + 2, "heading": None,
        "authored_path": f"media/{index}.png", "caption": caption if caption is not None else f"图 {index}",
    }


def pagination_full_gate(workdir: Path) -> dict[str, object]:
    del workdir
    manifest = load_manifest(SKILL_DIR)
    gallery_vectors: dict[int, list[int]] = {}
    for count in (1, 2, 3, 4, 5, 6, 8, 9):
        images = [_image(index, "" if index == 0 else None) for index in range(count)]
        document = _minimal_document([{
            "layout": "gallery", "title": "图集", "source_line": 1, "notes": None, "blocks": images,
        }])
        plan = pptx_paginate.build_deck_plan(document, manifest)
        gallery = [slide for slide in plan.slides if slide.layout == "gallery"]
        sizes = [len(slide.fragments) for slide in gallery]
        gallery_vectors[count] = sizes
        require(all(size <= 4 for size in sizes), "PPTX-06 gallery capacity")
        require(sum(sizes) == count, "PPTX-06 gallery item loss")
        for slide in gallery:
            require(all(int(dict(fragment.metadata)["gallery_preset"]) == len(slide.fragments)
                        for fragment in slide.fragments), "PPTX-06 gallery preset")
            require(all(dict(fragment.metadata)["caption_placeholder"] == "true"
                        for fragment in slide.fragments), "PPTX-06 caption placeholder")

    fixture = SKILL_DIR / "fixtures" / "school-pptx-full.md"
    document = parse_document(fixture, manifest)
    require(not document["errors"], "full fixture parser errors")
    first = pptx_paginate.build_deck_plan(document, manifest)
    second = pptx_paginate.build_deck_plan(document, manifest)
    require(first == second, "full fixture plan is not deterministic")
    require(first.slides[-1].layout == "closing", "closing is not last")
    require(sum(slide.layout == "closing" for slide in first.slides) == 1, "closing count")
    require(dict(first.slides[-1].fragments[0].metadata)["pptx_layout"] ==
            "ppt/slideLayouts/slideLayout7.xml", "closing part path")

    for logical_index, indices in first.logical_to_physical:
        require(indices == tuple(range(indices[0], indices[-1] + 1)), "logical-to-physical mapping not contiguous")
        logical = document["logical_slides"][logical_index]
        expected_notes = logical["notes"]["markdown"] if logical.get("notes") else None
        derived = [first.slides[index] for index in indices]
        require(all(slide.notes_intent == expected_notes for slide in derived), "D-16 notes propagation")
        if expected_notes is None:
            require(all(slide.to_projection()["notes_intent"] is None for slide in derived), "D-16 false notes intent")

    layouts = {slide.layout for slide in first.slides}
    require({"title-content", "two-column", "image-text", "table", "timeline", "gallery", "code"} <= layouts,
            "full fixture overflow layout coverage")
    image_text = [slide for slide in first.slides if slide.layout == "image-text"]
    require(len(image_text) >= 3 and all(any(fragment.kind == "image" for fragment in slide.fragments)
                                         for slide in image_text), "image-text cartesian planning")
    contents = [slide for slide in first.slides if slide.layout == "contents"]
    require([item for slide in contents for item in slide.fragments[0].items] == document["contents_entries"],
            "full fixture contents order")
    return {
        "gallery_vectors": gallery_vectors,
        "logical_slides": len(document["logical_slides"]),
        "physical_slides": len(first.slides),
        "diagnostics": [item.code for item in first.diagnostics],
    }


GATES["pagination-text-code"] = pagination_text_code_gate
GATES["pagination-structured"] = pagination_structured_gate
GATES["pagination-full"] = pagination_full_gate


def ooxml_bootstrap_gate(workdir: Path) -> dict[str, object]:
    try:
        import pptx_emit
        from pptx_ooxml import set_run_highlight
        from pptx.util import Inches
    except ImportError as exc:
        raise GateFailure("PPTX_DEPENDENCY_MISSING") from exc

    manifest = load_manifest(SKILL_DIR)
    presentation, layouts, evidence = pptx_emit.bootstrap_template(TEMPLATE_PATH, manifest)
    require(evidence == {
        "seed_slides": 5,
        "removed_seed_slides": 5,
        "removed_seed_notes_relationships": 2,
    }, "seed removal evidence mismatch")
    require(len(presentation.slides) == 0, "seed slides remain after bootstrap")
    require(set(layouts) == set(manifest["layouts"]), "layout part map incomplete")
    require(str(layouts["closing"].part.partname).lstrip("/") == "ppt/slideLayouts/slideLayout7.xml",
            "closing layout did not resolve by part path")

    invalid = copy.deepcopy(manifest)
    invalid["layouts"]["closing"]["pptx_layout"] = "ppt/slideLayouts/missing.xml"
    try:
        pptx_emit.bootstrap_template(TEMPLATE_PATH, invalid)
    except pptx_emit.PptxEmitError as exc:
        require(exc.code == "PPTX_TEMPLATE_LAYOUT_INVALID", "layout failure code mismatch")
    else:
        raise GateFailure("missing layout part did not fail")

    slide = presentation.slides.add_slide(layouts["closing"])
    text_box = slide.shapes.add_textbox(Inches(1), Inches(1), Inches(4), Inches(1))
    run = text_box.text_frame.paragraphs[0].add_run()
    run.text = "保留粗体与文本"
    run.font.bold = True
    scheme = manifest["inline_styles"]["highlight"]["scheme_color"]
    set_run_highlight(run, scheme)
    set_run_highlight(run, scheme)
    staged = workdir / "bootstrap.pptx"
    presentation.save(staged)
    reopened = pptx_emit.require_dependencies()["pptx"].Presentation(staged)
    require(len(reopened.slides) == 1, "bootstrap package did not reopen")
    require(reopened.slides[0].shapes[-1].text == "保留粗体与文本", "highlight changed run text")
    require(reopened.slides[0].shapes[-1].text_frame.paragraphs[0].runs[0].font.bold is True,
            "highlight changed bold")
    entries = safe_package_entries(staged)
    slide_xml = entries["ppt/slides/slide1.xml"]
    require(slide_xml.count(b"<a:highlight>") == 1 and f'val="{scheme}"'.encode() in slide_xml,
            "highlight is not idempotent theme OOXML")

    def missing_import(name: str) -> object:
        raise ModuleNotFoundError(name)

    try:
        pptx_emit.require_dependencies(missing_import)
    except pptx_emit.PptxEmitError as exc:
        require(exc.code == "PPTX_DEPENDENCY_MISSING" and "Traceback" not in str(exc),
                "dependency failure is not bounded")
    else:
        raise GateFailure("missing dependency did not fail")
    return {**evidence, "layouts": len(layouts), "highlight_scheme": scheme, "reopened_slides": 1}


GATES["ooxml-bootstrap"] = ooxml_bootstrap_gate


def code_literal_roundtrip_gate(workdir: Path) -> dict[str, object]:
    try:
        from pptx import Presentation
        from pptx.enum.shapes import MSO_SHAPE_TYPE
        from pptx.util import Inches
        import pptx_objects
    except ImportError as exc:
        raise GateFailure("PPTX_DEPENDENCY_MISSING") from exc

    vector = "if a == b == c\nreturn **value**\nx = ***raw***\n  keep  spaces  "
    source = (SCRIPTS_DIR / "pptx_objects.py").read_text(encoding="utf-8")
    tree = ast.parse(source, filename="pptx_objects.py")
    helper = next(
        node for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "add_literal_text"
    )
    forbidden = {"normalize_rich_text", "inline_spans", "add_rich_text", "set_run_highlight"}
    referenced = {node.id for node in ast.walk(helper) if isinstance(node, ast.Name)}
    require(not forbidden & referenced, "C-02 literal helper reaches delimiter parser or highlight helper")

    presentation = Presentation()
    slide = presentation.slides.add_slide(presentation.slide_layouts[6])
    pptx_objects.add_literal_text(
        slide,
        {"x": Inches(1), "y": Inches(1), "width": Inches(8), "height": Inches(4)},
        vector,
        font_size=18,
        name="school-pptx:code",
    )
    output = workdir / "code-literal-roundtrip.pptx"
    presentation.save(output)
    reopened = Presentation(output)
    code_shapes = [shape for shape in reopened.slides[0].shapes if shape.name == "school-pptx:code"]
    require(len(code_shapes) == 1, "literal vector is not in exactly one school-pptx:code shape")
    code_shape = code_shapes[0]
    require(code_shape.shape_type == MSO_SHAPE_TYPE.TEXT_BOX, "literal code is not a native textbox")
    require(code_shape.text == vector, "literal code changed after PPTX reopen")
    runs = [run for paragraph in code_shape.text_frame.paragraphs for run in paragraph.runs]
    require(len(runs) == 1 and runs[0].text == vector, "literal code is not stored in one run")
    require(all(run.font.name == "Consolas" for run in runs), "literal code run is not monospace")
    return {"characters": len(vector), "runs": len(runs), "font": runs[0].font.name}


GATES["code-literal-roundtrip"] = code_literal_roundtrip_gate


def editable_objects_gate(workdir: Path) -> dict[str, object]:
    try:
        import pptx_emit
        from pptx_model import BlockFragment, PhysicalDeckPlan, PhysicalSlide
        from pptx_objects import PptxObjectError, normalize_rich_text
    except ImportError as exc:
        raise GateFailure("PPTX_DEPENDENCY_MISSING") from exc

    require(normalize_rich_text("甲**粗体**==高亮==乙") == (
        ("plain", "甲"), ("bold", "粗体"), ("highlight", "高亮"), ("plain", "乙")
    ), "D-15 adjacent span normalization")
    try:
        normalize_rich_text("**重叠 ==样式** 失败==")
    except PptxObjectError as exc:
        require(str(exc) == "PPTX_INLINE_SPAN_OVERLAP", "overlap diagnostic changed")
    else:
        raise GateFailure("nested inline span did not fail")

    rich = BlockFragment(
        kind="paragraph", logical_index=0, block_index=0, fragment_index=0, source_line=1,
        text="甲**粗体**==高亮==乙",
    )
    table = BlockFragment(
        kind="table", logical_index=1, block_index=0, fragment_index=0, source_line=2,
        rows=(("列一", "列二"), ("数据", "内容")),
        metadata=(("table_name", ""), ("table_name_placeholder", "true"), ("repeat_header", "true")),
    )
    timeline = BlockFragment(
        kind="timeline", logical_index=2, block_index=0, fragment_index=0, source_line=3,
        rows=(("2026", "启动", "准备"), ("2027", "交付", "完成")),
    )
    gallery = BlockFragment(
        kind="image", logical_index=3, block_index=0, fragment_index=0, source_line=4,
        metadata=(("authored_path", "media/plc-line.png"), ("caption", ""),
                  ("caption_placeholder", "true"), ("gallery_preset", "1"), ("gallery_item_index", "0")),
    )
    code = BlockFragment(
        kind="code", logical_index=4, block_index=0, fragment_index=0, source_line=5,
        text="print('原始换行')\nreturn True",
    )
    slides = (
        PhysicalSlide(0, 0, "title-content", "富文本", 0, 1, (rich,), "逐字说明", affected_pages=(0,)),
        PhysicalSlide(1, 1, "table", "原生表格", 0, 2, (table,), None,
                      selected_font_sizes=(("table", 14.0),), affected_pages=(1,)),
        PhysicalSlide(2, 2, "timeline", "原生时间线", 0, 3, (timeline,), None, affected_pages=(2,)),
        PhysicalSlide(3, 3, "gallery", "原生图集", 0, 4, (gallery,), "图集备注", affected_pages=(3,)),
        PhysicalSlide(4, 4, "code", "代码", 0, 5, (code,), None, affected_pages=(4,)),
        PhysicalSlide(5, 5, "closing", "", 0, 6, (
            BlockFragment(kind="closing", logical_index=5, block_index=0, fragment_index=0, source_line=6),
        ), None, affected_pages=(5,)),
    )
    plan = PhysicalDeckPlan(slides)
    output = workdir / "editable-objects.pptx"
    manifest = load_manifest(SKILL_DIR)
    pptx_emit.emit_deck(plan, manifest, TEMPLATE_PATH, output, media_root=SKILL_DIR / "fixtures")
    reopened = pptx_emit.require_dependencies()["pptx"].Presentation(output)
    require(len(reopened.slides) == len(slides), "editable deck slide count")
    require([slide.has_notes_slide for slide in reopened.slides] == [True, False, False, True, False, False],
            "D-16 notes relationships do not match plan")
    require(reopened.slides[0].notes_slide.notes_text_frame.text == "逐字说明", "notes text mismatch")
    require(reopened.slides[3].notes_slide.notes_text_frame.text == "图集备注", "derived notes text mismatch")

    entries = safe_package_entries(output)
    all_slides = b"\n".join(payload for name, payload in entries.items() if name.startswith("ppt/slides/slide"))
    require(all_slides.count(b"<a:tbl>") == 1, "D-11 native table count")
    require(all_slides.count(b"<p:grpSp>") >= 3, "D-12/D-13 editable group count")
    require(b"<a:highlight>" in all_slides and b"b=\"1\"" in all_slides, "D-15 run OOXML missing")
    require(b"**" not in all_slides and b"==" not in all_slides, "D-15 delimiters visible")
    require(b"school-pptx:table-name" in all_slides and b"school-pptx:gallery-caption:0" in all_slides,
            "D-14 empty editable placeholder missing")
    require(all_slides.count(b"<a:t></a:t>") >= 1, "D-14 empty placeholder has no empty text node")
    require(b"school-pptx:timeline-axis" in all_slides, "timeline axis missing")
    require(b"school-pptx:timeline-axis" not in entries["ppt/slides/slide3.xml"].split(b"<p:grpSp>", 1)[-1],
            "timeline axis entered node group")
    require(b"print('original" not in all_slides, "unexpected code rewrite")
    require("print('原始换行')\nreturn True" in reopened.slides[4].shapes[-1].text, "code text changed")

    pictures = [shape for shape in reopened.slides[3].shapes if getattr(shape, "shape_type", None) == 6]
    require(pictures and len(pictures[0].shapes) == 2, "gallery card did not reopen as native group")
    gallery_picture = next(shape for shape in pictures[0].shapes if getattr(shape, "shape_type", None) == 13)
    require(all(getattr(gallery_picture, crop) == 0 for crop in ("crop_left", "crop_top", "crop_right", "crop_bottom")),
            "contain picture crop changed")
    require(output.stat().st_size > 0, "editable deck is empty")
    return {
        "slides": len(slides), "native_tables": 1, "groups": all_slides.count(b"<p:grpSp>"),
        "notes_relationships": 2, "picture_crop": [0, 0, 0, 0],
    }


GATES["editable-objects"] = editable_objects_gate


def emit_structure_gate(workdir: Path) -> dict[str, object]:
    try:
        import pptx_emit
    except ImportError as exc:
        raise GateFailure("PPTX_DEPENDENCY_MISSING") from exc

    fixture = SKILL_DIR / "fixtures" / "school-pptx-full.md"
    manifest = load_manifest(SKILL_DIR)
    document = parse_document(fixture, manifest)
    require(not document["errors"], "canonical fixture parser errors")
    plan = pptx_paginate.build_deck_plan(document, manifest)
    require(plan.slides and plan.slides[-1].layout == "closing", "physical plan closing invalid")
    output = workdir / "full-fixture.pptx"
    evidence = pptx_emit.emit_deck(plan, manifest, TEMPLATE_PATH, output, media_root=fixture.parent)
    emitter_source = (SCRIPTS_DIR / "pptx_emit.py").read_text(encoding="utf-8")
    require("build_deck_plan" not in emitter_source and "pptx_paginate" not in emitter_source,
            "emitter attempted to repaginate frozen plan")
    require(evidence["physical_slides"] == len(plan.slides), "PPTX-01 emitted slide count evidence")
    require(evidence["transition_mode"] == "none", "PPTX-12 transition mode")
    validated = pptx_emit.validate_staged_package(output, expected_slides=len(plan.slides))
    require(validated["slides"] == len(plan.slides), "staged validator slide count")

    package_entries = safe_package_entries(output)
    slide_xml = {
        index: package_entries[f"ppt/slides/slide{index + 1}.xml"] for index in range(len(plan.slides))
    }
    all_slide_xml = b"\n".join(slide_xml.values())
    require(b"\xe5\x88\x9d\xe8\xaf\x86\xe9\x9a\x94\xe7\xa6\xbb\xe5\xbc\x80\xe5\x85\xb3" not in all_slide_xml,
            "template seed text leaked")
    require(b"<p:transition" not in all_slide_xml, "PPTX-12 unexpected transition XML")

    rel_namespace = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
    layout_relationship = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/slideLayout"
    notes_relationship = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/notesSlide"
    image_relationship = "http://schemas.openxmlformats.org/officeDocument/2006/relationships/image"
    notes_indices: list[int] = []
    image_relationships = 0
    for index, physical in enumerate(plan.slides, start=1):
        rel_name = f"ppt/slides/_rels/slide{index}.xml.rels"
        relationships = ET.fromstring(package_entries[rel_name]).findall("r:Relationship", rel_namespace)
        layout_targets = [item.get("Target", "") for item in relationships if item.get("Type") == layout_relationship]
        require(len(layout_targets) == 1, f"slide {index} layout relationship count")
        expected_layout = manifest["layouts"][physical.layout]["pptx_layout"].split("/")[-1]
        require(layout_targets[0].endswith(expected_layout), f"slide {index} layout part mismatch")
        if any(item.get("Type") == notes_relationship for item in relationships):
            notes_indices.append(index - 1)
        image_relationships += sum(item.get("Type") == image_relationship for item in relationships)
    expected_notes = [slide.physical_index for slide in plan.slides if slide.notes_intent is not None]
    require(notes_indices == expected_notes, "PPTX-04 notes relationship mismatch")

    table_slides = [slide for slide in plan.slides if slide.layout == "table"]
    for physical in table_slides:
        xml = slide_xml[physical.physical_index]
        require(xml.count(b"<a:tbl>") == 1, "PPTX-04 native table per page")
        require(b"school-pptx:table-name" in xml, "empty/non-empty table-name shape missing")
        require(all(cell.encode("utf-8") in xml for cell in physical.fragments[0].rows[0]),
                "table repeated header missing")
    timeline_slides = [slide for slide in plan.slides if slide.layout == "timeline"]
    for physical in timeline_slides:
        xml = slide_xml[physical.physical_index]
        require(xml.count(b"<p:grpSp>") == len(physical.fragments[0].rows), "timeline group count")
        require(b"school-pptx:timeline-axis" in xml, "timeline axis missing")
    gallery_slides = [slide for slide in plan.slides if slide.layout == "gallery"]
    for physical in gallery_slides:
        require(len(physical.fragments) <= 4, "gallery capacity")
        xml = slide_xml[physical.physical_index]
        require(xml.count(b"<p:grpSp>") == len(physical.fragments), "gallery group count")
        require(xml.count(b"gallery-caption") == len(physical.fragments), "gallery caption count")
    code_slides = [slide for slide in plan.slides if slide.layout == "code"]
    for physical in code_slides:
        expected = "\n".join(fragment.text or "" for fragment in physical.fragments)
        reopened_text = "\n".join(
            shape.text for shape in pptx_emit.require_dependencies()["pptx"].Presentation(output)
            .slides[physical.physical_index].shapes if getattr(shape, "has_text_frame", False)
        )
        require(expected in reopened_text, "editable code round trip")

    reopened = pptx_emit.require_dependencies()["pptx"].Presentation(output)
    require(len(reopened.slides) == len(plan.slides), "PPTX-01 reopen slide count")
    require(sum(slide.layout == "closing" for slide in plan.slides) == 1, "closing plan count")
    last_relationships = ET.fromstring(
        package_entries[f"ppt/slides/_rels/slide{len(plan.slides)}.xml.rels"]
    ).findall("r:Relationship", rel_namespace)
    require(any(item.get("Target", "").endswith("slideLayout7.xml") for item in last_relationships),
            "closing did not use manifest part")
    for slide in reopened.slides:
        for shape in slide.shapes:
            if getattr(shape, "shape_type", None) == 13:
                require(not (shape.width == reopened.slide_width and shape.height == reopened.slide_height),
                        "whole-slide screenshot shortcut detected")
    require(image_relationships > 0, "native picture relationships missing")
    require(all(b"<a:srcRect" not in xml or b"<a:srcRect/>" in xml or b'l="0"' in xml
                for xml in slide_xml.values()),
            "picture crop is not zero")

    external = workdir / "external-relationship.pptx"
    with ZipFile(output) as source, ZipFile(external, "w", ZIP_DEFLATED) as target:
        for info in source.infolist():
            payload = source.read(info)
            if info.filename == "ppt/_rels/presentation.xml.rels":
                root = ET.fromstring(payload)
                relationship = root.findall("r:Relationship", rel_namespace)[0]
                relationship.set("Target", "https://invalid.example/template")
                relationship.set("TargetMode", "External")
                payload = ET.tostring(root, encoding="utf-8", xml_declaration=True)
            target.writestr(info.filename, payload)
    try:
        pptx_emit.validate_staged_package(external)
    except pptx_emit.PptxEmitError as exc:
        require(exc.code == "PPTX_PACKAGE_INVALID" and "Traceback" not in str(exc),
                "external relationship failure is not bounded")
    else:
        raise GateFailure("external relationship did not fail staged validation")
    return {
        "logical_slides": len(document["logical_slides"]),
        "physical_slides": len(plan.slides),
        "native_table_slides": len(table_slides),
        "timeline_slides": len(timeline_slides),
        "gallery_slides": len(gallery_slides),
        "notes_slides": len(notes_indices),
        "image_relationships": image_relationships,
        "transition_mode": "none",
        "package": validated,
    }


GATES["emit-structure"] = emit_structure_gate


def run_public_render(input_path: Path, output_root: Path, stem: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["SCHOOL_PPTX_PYTHON"] = sys.executable
    completed = subprocess.run(
        [str(PUBLIC_CLI), "render", "--input", str(input_path), "--out-dir", str(output_root), "--stem", stem],
        cwd=SKILL_DIR.parent.parent,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=60,
        check=False,
        env=environment,
    )
    require("Traceback" not in completed.stdout + completed.stderr, "public render leaked traceback")
    require(len(completed.stdout + completed.stderr) < 200_000, "public render output is unbounded")
    return completed


def command_owned_files(root: Path) -> set[str]:
    return {
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() or path.is_symlink()
    }


def semantic_package_inventory(path: Path) -> dict[str, object]:
    import pptx_emit

    entries = safe_package_entries(path)
    presentation = pptx_emit.require_dependencies()["pptx"].Presentation(path)
    slide_payloads = [entries[f"ppt/slides/slide{index}.xml"] for index in range(1, len(presentation.slides) + 1)]
    relationship_payloads = [
        entries[f"ppt/slides/_rels/slide{index}.xml.rels"] for index in range(1, len(presentation.slides) + 1)
    ]
    relationship_namespace = {"r": "http://schemas.openxmlformats.org/package/2006/relationships"}
    layouts: list[str] = []
    notes = 0
    images = 0
    for payload in relationship_payloads:
        relationships = ET.fromstring(payload).findall("r:Relationship", relationship_namespace)
        layouts.extend(
            item.get("Target", "").split("/")[-1]
            for item in relationships
            if item.get("Type", "").endswith("/slideLayout")
        )
        notes += sum(item.get("Type", "").endswith("/notesSlide") for item in relationships)
        images += sum(item.get("Type", "").endswith("/image") for item in relationships)
    visible_text = "\n".join(
        shape.text
        for slide in presentation.slides
        for shape in slide.shapes
        if getattr(shape, "has_text_frame", False)
    )
    return {
        "slides": len(presentation.slides),
        "layouts": layouts,
        "native_tables": sum(payload.count(b"<a:tbl>") for payload in slide_payloads),
        "groups": sum(payload.count(b"<p:grpSp>") for payload in slide_payloads),
        "pictures": images,
        "notes": notes,
        "visible_text_sha256": hashlib.sha256(visible_text.encode("utf-8")).hexdigest(),
    }


def cli_publication_gate(workdir: Path) -> dict[str, object]:
    output = workdir / "delivery"
    output.mkdir()
    sentinel = output / "caller-owned.txt"
    sentinel.write_bytes(b"caller-owned")
    before = hashlib.sha256(sentinel.read_bytes()).hexdigest()
    completed = run_public_render(FIXTURE_PATH, output, "course-deck")
    require(completed.returncode == 0, f"public render failed: {completed.stdout}{completed.stderr}")
    lines = completed.stdout.splitlines()
    require(lines and lines[0] == "渲染成功", "success heading order changed")
    require("逻辑页：13；物理页：24" in completed.stdout, "success pagination summary missing")
    require(completed.stdout.rstrip().endswith("校验结果：PASS"), "success validation footer missing")
    markdown = output / "course-deck.md"
    pptx = output / "course-deck.pptx"
    require(markdown.read_bytes() == FIXTURE_PATH.read_bytes(), "published Markdown bytes changed")
    require(pptx.stat().st_size > 0, "published PPTX is empty")
    require(hashlib.sha256(sentinel.read_bytes()).hexdigest() == before, "caller sentinel changed")
    require(command_owned_files(output) == {"caller-owned.txt", "course-deck.md", "course-deck.pptx"},
            "success public root contains non-pair artifacts")
    inventory = semantic_package_inventory(pptx)
    require(inventory["slides"] == 24 and inventory["native_tables"] > 0, "published PPTX did not reopen structurally")
    help_result = subprocess.run([str(PUBLIC_CLI), "--help"], text=True, capture_output=True, check=False)
    require(help_result.returncode == 0 and
            "render --input <reviewed.md> --out-dir <delivery-dir> [--stem <name>]" in help_result.stdout,
            "literal render usage missing")
    return {"files": sorted(command_owned_files(output)), "inventory": inventory}


def best_effort_gate(workdir: Path) -> dict[str, object]:
    missing_source = workdir / "missing-media.md"
    missing_source.write_bytes(FIXTURE_PATH.read_bytes())
    missing_output = workdir / "missing-output"
    missing_output.mkdir()
    completed = run_public_render(missing_source, missing_output, "missing")
    require(completed.returncode != 0, "missing-media render returned success")
    require("渲染完成但输入存在异常" in completed.stdout and "本次渲染不成功" in completed.stdout,
            "best-effort non-success copy missing")
    require("受影响逻辑页" in completed.stdout and "MEDIA_MISSING" in completed.stdout,
            "best-effort affected slides missing")
    require("渲染成功" not in completed.stdout, "best-effort printed success copy")
    require(command_owned_files(missing_output) == {"missing.md", "missing.pptx"},
            "best-effort root is not a clean pair")
    require(missing_source.read_bytes() == (missing_output / "missing.md").read_bytes(),
            "best-effort Markdown bytes changed")
    inventory = semantic_package_inventory(missing_output / "missing.pptx")
    entries = safe_package_entries(missing_output / "missing.pptx")
    slide_xml = b"\n".join(payload for name, payload in entries.items() if name.startswith("ppt/slides/slide"))
    for forbidden in ("警告页", "警告横幅", "水印", "渲染失败", "本次渲染不成功"):
        require(forbidden.encode("utf-8") not in slide_xml, f"best-effort PPTX contains visible warning pollution: {forbidden}")

    invalid_source = workdir / "invalid.md"
    invalid_source.write_text(
        '---\ntitle: "异常"\ntheme: "standard-school"\n---\n'
        '::: slide {layout="unknown-layout"}\n## 受影响页\n可恢复正文。\n:::\n',
        encoding="utf-8",
    )
    invalid_output = workdir / "invalid-output"
    invalid_output.mkdir()
    invalid = run_public_render(invalid_source, invalid_output, "invalid")
    require(invalid.returncode != 0 and "LAYOUT_UNKNOWN" in invalid.stdout and "受影响页" in invalid.stdout,
            "invalid Markdown did not publish bounded best-effort output")
    require(command_owned_files(invalid_output) == {"invalid.md", "invalid.pptx"},
            "invalid Markdown did not publish the fixed pair")
    semantic_package_inventory(invalid_output / "invalid.pptx")
    return {"missing_media_inventory": inventory, "invalid_exit": invalid.returncode}


def invoke_render_module(input_path: Path, output_root: Path, stem: str) -> tuple[int, str]:
    import pptx_render

    stdout = io.StringIO()
    arguments = argparse.Namespace(
        skill_dir=str(SKILL_DIR), input=str(input_path), out_dir=str(output_root), stem=stem,
    )
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stdout):
        result = pptx_render.render_command(arguments)
    output = stdout.getvalue()
    require("Traceback" not in output and len(output) < 200_000, "in-process render failure is unbounded")
    return result, output


def assert_no_renderer_debris(root: Path) -> None:
    forbidden = [
        path for path in root.rglob("*")
        if path.name.endswith(".bak") or ".tmp-" in path.name or path.suffix in {".json", ".log"}
        or "manifest" in path.name.lower() or "debug" in path.name.lower() or "evidence" in path.name.lower()
    ]
    require(not forbidden, f"renderer debris remains: {[path.name for path in forbidden]}")


def publication_safety_gate(workdir: Path) -> dict[str, object]:
    import pptx_render

    old_pptx = b"old-pptx-sentinel"
    corruption_root = workdir / "corruption"
    corruption_root.mkdir()
    (corruption_root / "deck.pptx").write_bytes(old_pptx)
    def corrupt(stream: object) -> None:
        stream.seek(0)
        stream.truncate(0)
        stream.write(b"corrupt")
        stream.flush()

    pptx_render.RENDER_PRE_VALIDATE_HOOK = corrupt
    try:
        result, output = invoke_render_module(FIXTURE_PATH, corruption_root, "deck")
    finally:
        pptx_render.RENDER_PRE_VALIDATE_HOOK = None
    require(result != 0 and "PPTX_PACKAGE_INVALID" in output, "staged corruption did not fail bounded")
    require((corruption_root / "deck.pptx").read_bytes() == old_pptx, "staged corruption replaced old PPTX")
    require(not (corruption_root / "deck.md").exists(), "staged corruption published Markdown")
    assert_no_renderer_debris(corruption_root)

    crash_root = workdir / "crash-window"
    crash_root.mkdir()
    (crash_root / "deck.md").write_bytes(b"old-markdown")
    (crash_root / "deck.pptx").write_bytes(old_pptx)
    pptx_render.RENDER_BETWEEN_REPLACE_HOOK = lambda root: (_ for _ in ()).throw(OSError("injected"))
    try:
        result, output = invoke_render_module(FIXTURE_PATH, crash_root, "deck")
    finally:
        pptx_render.RENDER_BETWEEN_REPLACE_HOOK = None
    require(result != 0 and "OUTPUT_PAIR_INTERRUPTED" in output, "between-replace fault did not fail bounded")
    require((crash_root / "deck.md").read_bytes() == FIXTURE_PATH.read_bytes(), "Markdown-first was not observable")
    require((crash_root / "deck.pptx").read_bytes() == old_pptx, "PPTX-last crash window replaced old PPTX")
    assert_no_renderer_debris(crash_root)

    exchange_root = workdir / "exchange"
    exchange_root.mkdir()
    attacker = workdir / "attacker"
    attacker.mkdir()
    sentinel = attacker / "sentinel"
    sentinel.write_bytes(b"caller")
    held = workdir / "held-exchange"

    def exchange(root: Path) -> None:
        root.rename(held)
        root.symlink_to(attacker, target_is_directory=True)

    pptx_render.RENDER_PRE_PUBLISH_HOOK = exchange
    try:
        result, output = invoke_render_module(FIXTURE_PATH, exchange_root, "deck")
    finally:
        pptx_render.RENDER_PRE_PUBLISH_HOOK = None
    require(result != 0 and "OUTPUT_ROOT_CHANGED" in output, "output-root exchange was not blocked")
    require(sentinel.read_bytes() == b"caller" and not (attacker / "deck.pptx").exists(),
            "output-root exchange modified attacker target")
    assert_no_renderer_debris(held)

    collision_root = workdir / "collisions"
    collision_root.mkdir()
    outside = workdir / "outside"
    outside.write_bytes(b"outside")
    (collision_root / "link.pptx").symlink_to(outside)
    result, output = invoke_render_module(FIXTURE_PATH, collision_root, "link")
    require(result != 0 and "OUTPUT_COLLISION" in output and outside.read_bytes() == b"outside",
            "final symlink collision was unsafe")
    (collision_root / "directory.pptx").mkdir()
    result, output = invoke_render_module(FIXTURE_PATH, collision_root, "directory")
    require(result != 0 and "OUTPUT_COLLISION" in output, "directory collision was accepted")
    result, output = invoke_render_module(FIXTURE_PATH, collision_root, "../escape")
    require(result != 0 and "OUTPUT_STEM_INVALID" in output and outside.read_bytes() == b"outside",
            "stem traversal was accepted")
    same = workdir / "same.md"
    same.write_bytes(FIXTURE_PATH.read_bytes())
    result, output = invoke_render_module(same, workdir, "same")
    require(result != 0 and "OUTPUT_INPUT_COLLISION" in output and same.read_bytes() == FIXTURE_PATH.read_bytes(),
            "input/output identity was accepted")
    assert_no_renderer_debris(collision_root)

    host_python = shutil.which("python3")
    require(host_python is not None, "host python missing for dependency gate")
    dependency_root = workdir / "dependency"
    dependency_root.mkdir()
    (dependency_root / "deck.pptx").write_bytes(old_pptx)
    environment = os.environ.copy()
    yaml_root = next(path.parent for path in Path.home().glob(".cache/uv/archive-v0/*/yaml/__init__.py"))
    environment["PYTHONPATH"] = str(yaml_root)
    environment["SCHOOL_PPTX_PYTHON"] = host_python
    dependency = subprocess.run(
        [str(PUBLIC_CLI), "render", "--input", str(FIXTURE_PATH), "--out-dir", str(dependency_root), "--stem", "deck"],
        text=True, capture_output=True, check=False, env=environment, timeout=30,
    )
    require(dependency.returncode != 0 and "PPTX_DEPENDENCY_MISSING" in dependency.stdout + dependency.stderr,
            "dependency absence did not fail bounded")
    require("Traceback" not in dependency.stdout + dependency.stderr and
            (dependency_root / "deck.pptx").read_bytes() == old_pptx,
            "dependency failure leaked traceback or replaced old PPTX")
    assert_no_renderer_debris(dependency_root)
    return {"staged_corruption": "blocked", "crash_window": "markdown-new-pptx-old", "exchange": "blocked"}


def publication_descriptor_race_gate(workdir: Path) -> dict[str, object]:
    import pptx_render

    normal_root = workdir / "normal"
    normal_root.mkdir()
    descriptor_evidence: dict[str, object] = {}

    def inspect_descriptors(destination: object, duplicate: object) -> None:
        _, identity, owner_fd = destination.temporary["pptx"]
        owner_flags = fcntl.fcntl(owner_fd, fcntl.F_GETFL) & os.O_ACCMODE
        duplicate_flags = fcntl.fcntl(duplicate.fileno(), fcntl.F_GETFL) & os.O_ACCMODE
        owner_status = os.fstat(owner_fd)
        duplicate_status = os.fstat(duplicate.fileno())
        probe = os.fdopen(os.dup(duplicate.fileno()), "r+b")
        probe.write(b"descriptor-probe")
        probe.seek(0)
        require(probe.read() == b"descriptor-probe", "duplicate is not independently seekable/readable/writable")
        probe.close()
        require(os.fstat(owner_fd).st_ino == owner_status.st_ino, "closing duplicate closed owner")
        require(owner_flags == duplicate_flags == os.O_RDWR, "PPTX descriptors are not read-write")
        require((owner_status.st_dev, owner_status.st_ino) ==
                (duplicate_status.st_dev, duplicate_status.st_ino) == identity,
                "owner and duplicate inode differ")
        descriptor_evidence.update({"owner_fd": owner_fd, "duplicate_fd": duplicate.fileno(), "identity": identity})

    pptx_render.RENDER_PRE_SAVE_HOOK = inspect_descriptors
    try:
        result, output = invoke_render_module(FIXTURE_PATH, normal_root, "deck")
    finally:
        pptx_render.RENDER_PRE_SAVE_HOOK = None
    require(result == 0, f"descriptor-only canonical render failed: {output}")
    safe_package_entries(normal_root / "deck.pptx")
    import pptx_emit
    require(len(pptx_emit.require_dependencies()["pptx"].Presentation(normal_root / "deck.pptx").slides) > 0,
            "published descriptor deck did not reopen")
    for key in ("owner_fd", "duplicate_fd"):
        try:
            os.fstat(int(descriptor_evidence[key]))
        except OSError:
            pass
        else:
            raise GateFailure(f"{key} remained open after render")

    race_root = workdir / "race"
    race_root.mkdir()
    sentinel = workdir / "outside-sentinel.bin"
    sentinel_bytes = b"caller-owned-sentinel\x00bytes"
    sentinel.write_bytes(sentinel_bytes)
    sentinel_hash = hashlib.sha256(sentinel_bytes).hexdigest()
    race_fds: dict[str, int] = {}
    attacker_name: dict[str, str] = {}

    def exchange(destination: object, duplicate: object) -> None:
        name, _, owner_fd = destination.temporary["pptx"]
        race_fds.update({"owner_fd": owner_fd, "duplicate_fd": duplicate.fileno()})
        attacker_name["name"] = name
        os.unlink(name, dir_fd=destination.root_fd)
        os.symlink(str(sentinel), name, dir_fd=destination.root_fd)

    pptx_render.RENDER_PRE_SAVE_HOOK = exchange
    try:
        result, output = invoke_render_module(FIXTURE_PATH, race_root, "deck")
    finally:
        pptx_render.RENDER_PRE_SAVE_HOOK = None
    require(result != 0 and "OUTPUT_TEMP_CHANGED" in output, "staged symlink exchange was not blocked")
    require(sentinel.read_bytes() == sentinel_bytes and sentinel.stat().st_size == len(sentinel_bytes)
            and hashlib.sha256(sentinel.read_bytes()).hexdigest() == sentinel_hash,
            "external sentinel changed during descriptor race")
    retained = race_root / attacker_name["name"]
    require(retained.is_symlink() and retained.resolve() == sentinel.resolve(), "attacker symlink was not retained")
    for key, descriptor in race_fds.items():
        try:
            os.fstat(descriptor)
        except OSError:
            pass
        else:
            raise GateFailure(f"race {key} remained open")
    regular_debris = [path for path in race_root.iterdir() if path.is_file() and not path.is_symlink()]
    require(not regular_debris and not (race_root / "deck.pptx").exists() and not (race_root / "deck.md").exists(),
            "renderer-owned publication debris remains after race")
    return {
        "descriptor_access": "O_RDWR",
        "same_inode": True,
        "zip_and_reopen": "PASS",
        "race_code": "OUTPUT_TEMP_CHANGED",
        "sentinel_sha256": sentinel_hash,
        "attacker_symlink_retained": True,
        "fds_closed": True,
    }


def _media_markdown(media_name: str) -> str:
    return (
        '---\ntitle: "对象错误"\ntheme: "standard-school"\n---\n'
        '::: slide {layout="image-text"}\n## 媒体页\n对象错误验证正文。\n\n'
        f'![本地媒体]({media_name})\n:::\n'
    )


def _png_chunk(kind: bytes, payload: bytes) -> bytes:
    return len(payload).to_bytes(4, "big") + kind + payload + zlib.crc32(kind + payload).to_bytes(4, "big")


def object_error_bounded_gate(workdir: Path) -> dict[str, object]:
    import pptx_emit
    from pptx_objects import PptxObjectError

    unknown = pptx_emit.map_object_error(PptxObjectError("private path /tmp/secret"))
    require(unknown.code == "PPTX_OBJECT_INVALID" and "/tmp/secret" not in unknown.message,
            "unknown object error was not normalized")

    vectors: list[tuple[str, bytes, str]] = []
    vectors.append((
        "invalid.gif",
        base64.b64decode("R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="),
        "PPTX_MEDIA_FORMAT_INVALID",
    ))
    ihdr = (10_000).to_bytes(4, "big") + (5_000).to_bytes(4, "big") + bytes((8, 2, 0, 0, 0))
    oversized_png = b"\x89PNG\r\n\x1a\n" + _png_chunk(b"IHDR", ihdr) + _png_chunk(b"IEND", b"")
    vectors.append(("oversized.png", oversized_png, "PPTX_MEDIA_PIXEL_LIMIT"))

    evidence: dict[str, object] = {}
    for media_name, payload, expected_code in vectors:
        vector_root = workdir / expected_code.lower()
        vector_root.mkdir()
        media_path = vector_root / media_name
        media_path.write_bytes(payload)
        source = vector_root / "deck.md"
        source.write_text(_media_markdown(media_name), encoding="utf-8")
        output_root = vector_root / "delivery"
        output_root.mkdir()
        old_pptx = b"old-pptx-object-error-sentinel"
        (output_root / "deck.pptx").write_bytes(old_pptx)
        completed = run_public_render(source, output_root, "deck")
        output = completed.stdout + completed.stderr
        require(completed.returncode != 0 and expected_code in output, f"{expected_code} was not public")
        require(len(output.encode("utf-8")) < 8 * 1024, f"{expected_code} output exceeded 8 KiB")
        require("Traceback" not in output and str(workdir) not in output,
                f"{expected_code} leaked traceback or absolute workdir")
        require("cannot identify image file" not in output.lower() and "decompressionbomb" not in output.lower(),
                f"{expected_code} leaked Pillow details")
        require((output_root / "deck.pptx").read_bytes() == old_pptx,
                f"{expected_code} replaced the old PPTX")
        require(not (output_root / "deck.md").exists(), f"{expected_code} published Markdown")
        assert_no_renderer_debris(output_root)
        evidence[expected_code] = {"exit": completed.returncode, "output_bytes": len(output.encode("utf-8"))}
    return evidence


def determinism_gate(workdir: Path) -> dict[str, object]:
    manifest = load_manifest(SKILL_DIR)
    first_document = parse_document(FIXTURE_PATH, manifest)
    second_document = parse_document(FIXTURE_PATH, manifest)
    first_plan = pptx_paginate.build_deck_plan(first_document, manifest)
    second_plan = pptx_paginate.build_deck_plan(second_document, manifest)
    first_projection = first_plan.to_projection()
    second_projection = second_plan.to_projection()
    require(first_projection == second_projection, "physical-plan projection changed")
    inventories: list[dict[str, object]] = []
    for index in range(2):
        output = workdir / f"run-{index}"
        output.mkdir()
        completed = run_public_render(FIXTURE_PATH, output, "deck")
        require(completed.returncode == 0, f"determinism render {index} failed")
        inventories.append(semantic_package_inventory(output / "deck.pptx"))
    require(inventories[0] == inventories[1], "semantic package inventory changed")
    projection_bytes = json.dumps(first_projection, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return {
        "physical_plan_sha256": hashlib.sha256(projection_bytes).hexdigest(),
        "physical_slides": len(first_plan.slides),
        "semantic_inventory": inventories[0],
    }


def phase_41_42_regression_gate(workdir: Path) -> dict[str, object]:
    template = run_template_report(workdir)
    completed = subprocess.run(
        [sys.executable, str(SCRIPTS_DIR / "verify_markdown_contract.py"), "fixture-example"],
        cwd=SKILL_DIR.parent.parent, text=True, capture_output=True, timeout=120, check=False,
    )
    require(completed.returncode == 0, f"Phase 42 fixture-example failed: {completed.stdout}{completed.stderr}")
    require("Traceback" not in completed.stdout + completed.stderr, "Phase 42 regression leaked traceback")
    runtime_files = sorted(path for path in SCRIPTS_DIR.glob("*.py") if path.name.startswith("pptx_"))
    require(runtime_files and all(path.parent == SCRIPTS_DIR for path in runtime_files), "runtime file escaped skill scripts")
    forbidden_calls: list[str] = []
    for path in runtime_files:
        source = path.read_text(encoding="utf-8")
        if "skills/" in source and "school-pptx" not in source:
            forbidden_calls.append(path.name)
    require(not forbidden_calls, f"sibling skill runtime calls found: {forbidden_calls}")
    shell_source = PUBLIC_CLI.read_text(encoding="utf-8")
    require("pptx_render.py" in shell_source and "verify --workdir" not in shell_source,
            "Phase 44 public verify leaked into Phase 43")
    require(not (SKILL_DIR / "SKILL.md").exists(), "Phase 44 canonical skill entry was created early")
    return {"template_layouts": len(template["layouts"]), "fixture_example": "PASS", "runtime_files": [p.name for p in runtime_files]}


GATES["cli-publication"] = cli_publication_gate
GATES["best-effort"] = best_effort_gate
GATES["publication-safety"] = publication_safety_gate
GATES["publication-descriptor-race"] = publication_descriptor_race_gate
GATES["object-error-bounded"] = object_error_bounded_gate
GATES["determinism"] = determinism_gate
GATES["phase_41_42_regression"] = phase_41_42_regression_gate


PHASE_43_GATE_ORDER = (
    "contract-model",
    "pagination",
    "ooxml-bootstrap",
    "editable-objects",
    "emit-structure",
    "cli-publication",
    "best-effort",
    "publication-safety",
    "determinism",
    "phase_41_42_regression",
)


def run_named_gate(name: str, workdir: Path) -> dict[str, object]:
    if name == "contract-model":
        return run_contract_model()
    if name == "pagination":
        names = [candidate for candidate in GATES if candidate.startswith("pagination-")]
        evidence: dict[str, object] = {}
        for candidate in names:
            evidence[candidate] = GATES[candidate](workdir)
            print(f"PASS {candidate}")
        return evidence
    evidence = GATES[name](workdir)
    print(f"PASS {name}")
    return {name: evidence}


def run_phase_43() -> dict[str, object]:
    require(len(PHASE_43_GATE_ORDER) == len(set(PHASE_43_GATE_ORDER)), "phase-43 registry contains duplicates")
    required = {
        "contract-model", "pagination", "ooxml-bootstrap", "editable-objects", "emit-structure",
        "cli-publication", "best-effort", "publication-safety", "determinism", "phase_41_42_regression",
    }
    require(set(PHASE_43_GATE_ORDER) == required, "phase-43 registry coverage changed")
    evidence: dict[str, object] = {}
    called: list[str] = []
    with tempfile.TemporaryDirectory(prefix="school-pptx-phase-43-") as temporary:
        root = Path(temporary)
        for name in PHASE_43_GATE_ORDER:
            gate_dir = root / name
            gate_dir.mkdir()
            evidence[name] = run_named_gate(name, gate_dir)
            called.append(name)
    require(tuple(called) == PHASE_43_GATE_ORDER, "phase-43 registry skipped or reordered a gate")
    evidence["decision_coverage"] = {
        "D-01..D-05": "pagination",
        "D-06..D-10": "pagination",
        "D-11..D-16": "editable-objects,emit-structure",
        "D-17..D-18": "best-effort",
        "D-19": "publication-safety",
        "D-20..D-21": "cli-publication,publication-safety",
    }
    evidence["requirement_coverage"] = {
        "PPTX-01..PPTX-12": "contract-model,pagination,ooxml-bootstrap,editable-objects,emit-structure",
        "PPTX-13": "cli-publication,publication-safety",
        "VER-03": "cli-publication,best-effort",
        "SKILL-03": "phase_41_42_regression",
    }
    return evidence


def run_contract_model() -> dict[str, object]:
    names = ["manifest_renderer_contract_gate", "model_determinism_gate", "measurement_gate"]
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
    parser.add_argument("gate", choices=["contract-model", "pagination", "phase-43", *GATES])
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.gate == "phase-43":
            evidence = run_phase_43()
        else:
            with tempfile.TemporaryDirectory(prefix=f"school-pptx-{args.gate}-") as temporary:
                evidence = run_named_gate(args.gate, Path(temporary))
        print(json.dumps(evidence, ensure_ascii=False, sort_keys=True))
        return 0
    except (GateFailure, OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"FAIL {args.gate}: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
