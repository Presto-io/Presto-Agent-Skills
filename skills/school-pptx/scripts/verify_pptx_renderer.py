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


def run_contract_model() -> dict[str, object]:
    require(len(GATES) == len(set(GATES)) == 3, "gate registry must contain three unique gates")
    called: list[str] = []
    evidence: dict[str, object] = {}
    with tempfile.TemporaryDirectory(prefix="school-pptx-contract-model-") as temporary:
        root = Path(temporary)
        for name, gate in GATES.items():
            gate_dir = root / name
            gate_dir.mkdir()
            evidence[name] = gate(gate_dir)
            called.append(name)
            print(f"PASS {name}")
    require(called == list(GATES), "gate registry execution was skipped or reordered")
    return evidence


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="verify_pptx_renderer.py")
    parser.add_argument("gate", choices=["contract-model", *GATES])
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        if args.gate == "contract-model":
            evidence = run_contract_model()
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
