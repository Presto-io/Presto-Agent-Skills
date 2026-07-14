#!/usr/bin/env python3
"""Black-box security regressions for the public template-report command."""

from __future__ import annotations

import json
import struct
import subprocess
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

import template_report


SKILL_DIR = Path(__file__).resolve().parent.parent
PUBLIC_CLI = SKILL_DIR / "scripts" / "school-pptx.sh"
TEMPLATE_PATH = SKILL_DIR / "templates" / "standard-school.pptx"
REPOSITORY_ROOT = SKILL_DIR.parent.parent


class VerificationFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationFailure(message)


def run_public(template: Path, workdir: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            str(PUBLIC_CLI),
            "template-report",
            "--theme",
            "standard-school",
            "--template",
            str(template),
            "--out-md",
            str(workdir / "report.md"),
            "--out-json",
            str(workdir / "report.json"),
        ],
        cwd=REPOSITORY_ROOT,
        text=True,
        capture_output=True,
        timeout=60,
        check=False,
    )


def assert_public_failure(template: Path, workdir: Path, expected_code: str) -> dict[str, object]:
    completed = run_public(template, workdir)
    output = completed.stdout + completed.stderr
    require(completed.returncode != 0, f"{expected_code} unexpectedly passed")
    require(output.strip() == expected_code, f"expected {expected_code}, got bounded output mismatch")
    require(len(output.encode("utf-8")) < 8 * 1024, f"{expected_code} output exceeded 8 KiB")
    require("Traceback" not in output and str(workdir) not in output, f"{expected_code} leaked internals")
    require("SECRET_PAYLOAD" not in output, f"{expected_code} leaked entry payload")
    return {"exit": completed.returncode, "output_bytes": len(output.encode("utf-8"))}


def package(path: Path, entries: list[tuple[str, bytes]]) -> None:
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        for name, payload in entries:
            archive.writestr(name, payload)


def patch_uncompressed_sizes(path: Path, declared_size: int) -> None:
    payload = bytearray(path.read_bytes())
    cursor = 0
    patched_local = False
    patched_central = False
    while cursor < len(payload) - 30:
        signature = payload[cursor:cursor + 4]
        if signature == b"PK\x03\x04":
            struct.pack_into("<I", payload, cursor + 22, declared_size)
            patched_local = True
            name_length, extra_length = struct.unpack_from("<HH", payload, cursor + 26)
            compressed_size = struct.unpack_from("<I", payload, cursor + 18)[0]
            cursor += 30 + name_length + extra_length + compressed_size
        elif signature == b"PK\x01\x02":
            struct.pack_into("<I", payload, cursor + 24, declared_size)
            patched_central = True
            name_length, extra_length, comment_length = struct.unpack_from("<HHH", payload, cursor + 28)
            cursor += 46 + name_length + extra_length + comment_length
        else:
            cursor += 1
    require(patched_local and patched_central, "failed to patch ZIP size metadata")
    path.write_bytes(payload)


def fake_info(name: str, size: int) -> ZipInfo:
    info = ZipInfo(name)
    info.file_size = size
    return info


def expect_preflight_failure(infos: list[ZipInfo], expected_code: str) -> None:
    try:
        template_report.preflight_package(infos)
    except template_report.TemplatePackageError as exc:
        require(str(exc) == expected_code, f"expected {expected_code}, got {exc}")
        return
    raise VerificationFailure(f"preflight did not fail with {expected_code}")


def relationship_xml(count: int) -> ET.Element:
    namespace = template_report.REL_NS["r"]
    root = ET.Element(f"{{{namespace}}}Relationships")
    for index in range(count):
        ET.SubElement(
            root,
            f"{{{namespace}}}Relationship",
            {"Id": f"rId{index}", "Type": "urn:test", "Target": "../slides/slide1.xml"},
        )
    return root


def resource_boundaries() -> dict[str, object]:
    entries_at_limit = [fake_info(f"parts/{index}.bin", 0) for index in range(template_report.MAX_PACKAGE_ENTRIES)]
    require(len(template_report.preflight_package(entries_at_limit)) == template_report.MAX_PACKAGE_ENTRIES,
            "entry-count boundary failed")
    expect_preflight_failure(entries_at_limit + [fake_info("parts/overflow.bin", 0)],
                             "TEMPLATE_PACKAGE_ENTRY_COUNT")

    template_report.preflight_package([fake_info("part.bin", template_report.MAX_PACKAGE_ENTRY_BYTES)])
    expect_preflight_failure([fake_info("part.bin", template_report.MAX_PACKAGE_ENTRY_BYTES + 1)],
                             "TEMPLATE_PACKAGE_ENTRY_SIZE")

    total_at_limit = [fake_info(f"total/{index}.bin", template_report.MAX_PACKAGE_ENTRY_BYTES) for index in range(6)]
    template_report.preflight_package(total_at_limit)
    total_over = total_at_limit + [fake_info("total/extra.bin", 1)]
    expect_preflight_failure(total_over, "TEMPLATE_PACKAGE_TOTAL_SIZE")

    require(template_report.validate_relationships(
        "ppt/_rels/presentation.xml.rels", relationship_xml(template_report.MAX_PACKAGE_RELATIONSHIPS), 0
    ) == template_report.MAX_PACKAGE_RELATIONSHIPS, "relationship boundary failed")
    try:
        template_report.validate_relationships(
            "ppt/_rels/presentation.xml.rels", relationship_xml(template_report.MAX_PACKAGE_RELATIONSHIPS + 1), 0
        )
    except template_report.TemplatePackageError as exc:
        require(str(exc) == "TEMPLATE_PACKAGE_RELATIONSHIP_LIMIT", "relationship overflow code changed")
    else:
        raise VerificationFailure("relationship overflow did not fail")
    return {
        "entries": template_report.MAX_PACKAGE_ENTRIES,
        "entry_bytes": template_report.MAX_PACKAGE_ENTRY_BYTES,
        "total_bytes": template_report.MAX_PACKAGE_TOTAL_BYTES,
        "relationships": template_report.MAX_PACKAGE_RELATIONSHIPS,
    }


def public_negative_vectors(root: Path) -> dict[str, object]:
    vectors: dict[str, tuple[Path, str]] = {}

    entry_count = root / "entry-count.pptx"
    package(entry_count, [(f"parts/{index}.xml", b"<x/>") for index in range(template_report.MAX_PACKAGE_ENTRIES + 1)])
    vectors["entry_count"] = (entry_count, "TEMPLATE_PACKAGE_ENTRY_COUNT")

    declared_size = root / "declared-size.pptx"
    package(declared_size, [("ppt/presentation.xml", b"0" * (template_report.MAX_PACKAGE_ENTRY_BYTES + 1))])
    vectors["declared_size"] = (declared_size, "TEMPLATE_PACKAGE_ENTRY_SIZE")

    actual_size = root / "actual-size.pptx"
    package(actual_size, [("ppt/presentation.xml", b"A" * (template_report.MAX_PACKAGE_ENTRY_BYTES + 1))])
    patch_uncompressed_sizes(actual_size, template_report.MAX_PACKAGE_ENTRY_BYTES)
    vectors["actual_size"] = (actual_size, "TEMPLATE_PACKAGE_ENTRY_SIZE")

    duplicate = root / "duplicate.pptx"
    with ZipFile(duplicate, "w", ZIP_DEFLATED) as archive:
        archive.writestr("ppt/presentation.xml", b"<x/>")
        archive.writestr("ppt/presentation.xml", b"<SECRET_PAYLOAD/>")
    vectors["duplicate"] = (duplicate, "TEMPLATE_PACKAGE_DUPLICATE")

    traversal = root / "traversal.pptx"
    package(traversal, [("ppt/../SECRET_PAYLOAD.xml", b"<x/>")])
    vectors["traversal"] = (traversal, "TEMPLATE_PACKAGE_PATH_INVALID")

    forbidden_xml = root / "forbidden-xml.pptx"
    package(forbidden_xml, [("ppt/presentation.xml", b'<!DOCTYPE x [<!ENTITY e "SECRET_PAYLOAD">]><x>&e;</x>')])
    vectors["doctype_entity"] = (forbidden_xml, "TEMPLATE_PACKAGE_XML_FORBIDDEN")

    external_relationship = root / "external-relationship.pptx"
    package(external_relationship, [(
        "ppt/_rels/presentation.xml.rels",
        b'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        b'<Relationship Id="rId1" Type="urn:test" TargetMode="External" Target="https://example.invalid/SECRET_PAYLOAD"/>'
        b'</Relationships>',
    )])
    vectors["external_relationship"] = (external_relationship, "TEMPLATE_PACKAGE_RELATIONSHIP_INVALID")

    evidence: dict[str, object] = {}
    for name, (path, code) in vectors.items():
        vector_workdir = root / f"work-{name}"
        vector_workdir.mkdir()
        evidence[name] = {"code": code, **assert_public_failure(path, vector_workdir, code)}
    require(len(evidence) == 7, "public negative vector count changed")
    return evidence


def canonical_regression(root: Path) -> dict[str, object]:
    workdir = root / "canonical"
    workdir.mkdir()
    completed = run_public(TEMPLATE_PATH, workdir)
    output = completed.stdout + completed.stderr
    require(completed.returncode == 0 and "Traceback" not in output, "canonical template-report failed")
    report = json.loads((workdir / "report.json").read_text(encoding="utf-8"))
    require(len(report["layouts"]) == 11 and not report["failures"], "canonical 11-layout regression failed")
    return {"layouts": len(report["layouts"]), "status": "PASS"}


def run() -> dict[str, object]:
    with tempfile.TemporaryDirectory(prefix="school-pptx-template-security-") as temporary:
        root = Path(temporary)
        return {
            "boundaries": resource_boundaries(),
            "negative_vectors": public_negative_vectors(root),
            "canonical": canonical_regression(root),
        }


def main() -> int:
    try:
        print(json.dumps(run(), ensure_ascii=False, sort_keys=True))
        return 0
    except (VerificationFailure, OSError, ValueError, template_report.TemplatePackageError) as exc:
        print(f"FAIL template-reader-security: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
