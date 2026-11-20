import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import posixpath
import shutil
import subprocess
import sys
import tempfile
from zipfile import ZipFile

from lxml import etree
from PIL import Image, ImageDraw, ImageOps
from pptx import Presentation


ROOT = Path(__file__).resolve().parents[1]
NAMESPACES = {"a": "http://schemas.openxmlformats.org/drawingml/2006/main"}


def write_json(path, value):
    payload = json.dumps(value, ensure_ascii=False, indent=2)
    if path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)


def walk(shapes):
    for shape in shapes:
        yield shape
        if shape.shape_type == 6:
            yield from walk(shape.shapes)


def inspect(path):
    deck = Presentation(str(path))
    slides = []
    for index, slide in enumerate(deck.slides, 1):
        shapes = []
        for shape in walk(slide.shapes):
            record = {"id": shape.shape_id, "name": shape.name,
                      "box_inches": [round(getattr(shape, field) / 914400, 4)
                                     for field in ("left", "top", "width", "height")]}
            if shape.has_text_frame:
                record["text"] = shape.text
                record["runs"] = [{"text": run.text, "font": run.font.name,
                                   "size_pt": run.font.size.pt if run.font.size else None}
                                  for paragraph in shape.text_frame.paragraphs for run in paragraph.runs]
            if shape.has_chart:
                record["chart"] = True
            if shape.has_table:
                record["table"] = [[cell.text for cell in row.cells] for row in shape.table.rows]
            shapes.append(record)
        slides.append({"page": index, "layout": slide.slide_layout.name, "shapes": shapes,
                       "notes": slide.notes_slide.notes_text_frame.text if slide.has_notes_slide else ""})
    return {"file": str(Path(path).resolve()), "pages": len(slides),
            "size_inches": [deck.slide_width / 914400, deck.slide_height / 914400], "slides": slides}


def check(path, school_template=False):
    errors, warnings = [], []
    inventory = inspect(path)
    with ZipFile(path) as archive:
        names = set(archive.namelist())
        broken = archive.testzip()
        if broken:
            errors.append(f"Corrupt ZIP member: {broken}")
        for name in names:
            if name.endswith(".xml") or name.endswith(".rels"):
                document = etree.fromstring(archive.read(name))
                if name.endswith(".rels"):
                    base = "" if name == "_rels/.rels" else posixpath.dirname(posixpath.dirname(name))
                    for relation in document:
                        if relation.get("TargetMode") == "External":
                            continue
                        target = relation.get("Target", "").split("#")[0]
                        resolved = posixpath.normpath(posixpath.join(base, target)) if not target.startswith("/") else target[1:]
                        if resolved not in names:
                            errors.append(f"Missing relationship: {name} -> {target}")
        if school_template:
            with ZipFile(ROOT / "assets/school-template.pptx") as template:
                protected = [name for name in template.namelist()
                             if not name.endswith("/") and name.startswith(("ppt/slideMasters/", "ppt/slideLayouts/", "ppt/theme/", "ppt/media/"))]
                for name in protected:
                    if name not in names:
                        errors.append(f"School asset missing: {name}")
                        continue
                    before, after = template.read(name), archive.read(name)
                    if name.endswith((".xml", ".rels")):
                        roots = [etree.fromstring(before), etree.fromstring(after)]
                        if name.endswith(".rels"):
                            for root in roots:
                                root[:] = sorted(root, key=lambda element: element.get("Id", ""))
                        before, after = [etree.tostring(root, method="c14n") for root in roots]
                    if hashlib.sha256(before).digest() != hashlib.sha256(after).digest():
                        errors.append(f"School asset changed: {name}")
    deck = Presentation(str(path))
    for page, slide in enumerate(deck.slides, 1):
        identifiers = [shape.shape_id for shape in walk(slide.shapes)]
        if len(identifiers) != len(set(identifiers)):
            errors.append(f"Page {page}: duplicate shape IDs")
        for shape in walk(slide.shapes):
            if shape.shape_type == 13:
                try:
                    with Image.open(io.BytesIO(shape.image.blob)) as image:
                        image.verify()
                except (OSError, ValueError):
                    warnings.append(f"Page {page}: image needs viewer validation: {shape.name}")
            if shape.has_text_frame:
                if any(marker in shape.text for marker in ("输入标题", "单击此处", "{{待补充", "Lorem ipsum")):
                    errors.append(f"Page {page}: leftover placeholder in {shape.name}")
            if not shape.name.startswith("school:"):
                continue
            if shape.name in {"school:visual-footer", "school:visual-logo", "school:visual-accent"}:
                continue
            left, top, width, height = [getattr(shape, field) / 914400 for field in ("left", "top", "width", "height")]
            if min(left, top) < -0.01 or left + width > inventory["size_inches"][0] + 0.01 or top + height > inventory["size_inches"][1] + 0.01:
                errors.append(f"Page {page}: outside canvas: {shape.name}")
            if slide.slide_layout.name == "标题和内容" and top + height > 6.12:
                errors.append(f"Page {page}: content enters footer safety area: {shape.name}")
            if slide.slide_layout.name == "标题和内容" and shape.name != "school:title" and top < 2.05:
                errors.append(f"Page {page}: content enters header safety area: {shape.name}")
            if shape.has_text_frame and shape.text:
                frame = shape.text_frame
                usable_width = max(0.01, width - (frame.margin_left + frame.margin_right) / 914400) * 72
                usable_height = max(0.01, height - (frame.margin_top + frame.margin_bottom) / 914400) * 72
                required = 0
                for paragraph in frame.paragraphs:
                    size = max([run.font.size.pt for run in paragraph.runs if run.font.size] or [24])
                    units = sum(1 if ord(character) > 255 else 0.55 for character in paragraph.text)
                    required += max(1, math.ceil(units * size / usable_width)) * size * 1.15
                    required += paragraph.space_after.pt if paragraph.space_after else 0
                if required > usable_height * 1.08:
                    warnings.append(f"Page {page}: possible text overflow: {shape.name}")
    return {"status": "FAIL" if errors else "PASS", "pages": inventory["pages"],
            "errors": errors, "warnings": warnings,
            "limits": "Geometry and text estimates do not replace rendered visual or PowerPoint/WPS review."}


def preview(path, out_dir, font_dirs):
    try:
        import pymupdf as pdf_runtime
    except ImportError:
        pdf_runtime = None
    poppler = shutil.which("pdftoppm")
    if pdf_runtime is None and not poppler:
        raise RuntimeError("PDF rasterizer missing: provide PyMuPDF or pdftoppm (Poppler)")
    executable = shutil.which("soffice") or shutil.which("libreoffice")
    if not executable:
        raise RuntimeError("LibreOffice missing; render with available PowerPoint/WPS and inspect images")
    output = Path(out_dir).resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Use an empty preview directory: {output}")
    output.mkdir(parents=True, exist_ok=True)
    local_fonts = [Path(item).expanduser().resolve() for item in font_dirs]
    if sys.platform == "darwin":
        local_fonts += [Path.home() / "Library/Fonts", Path("/Library/Fonts"), Path("/System/Library/Fonts")]
    environment = os.environ.copy()
    with tempfile.TemporaryDirectory(prefix="school-pptx-preview-") as temporary:
        temporary = Path(temporary)
        if local_fonts:
            configuration = etree.Element("fontconfig")
            for directory in local_fonts:
                if directory.is_dir():
                    etree.SubElement(configuration, "dir").text = str(directory)
            etree.SubElement(configuration, "cachedir").text = str(temporary / "font-cache")
            fontconfig = temporary / "fonts.conf"
            fontconfig.write_bytes(etree.tostring(configuration, xml_declaration=True))
            environment["FONTCONFIG_FILE"] = str(fontconfig)
        command = [executable, "-env:UserInstallation=" + (temporary / "profile").as_uri(),
                   "--headless", "--convert-to", "pdf", "--outdir", str(output), str(Path(path).resolve())]
        result = subprocess.run(command, capture_output=True, text=True, env=environment, timeout=180)
        pdf = output / (Path(path).stem + ".pdf")
        if result.returncode or not pdf.exists():
            raise RuntimeError(f"PDF export failed: {result.stdout}\n{result.stderr}")
    if pdf_runtime is not None:
        with pdf_runtime.open(pdf) as document:
            for index, page in enumerate(document):
                pixmap = page.get_pixmap(matrix=pdf_runtime.Matrix(1.5, 1.5), alpha=False)
                pixmap.save(output / f"slide-{index + 1:02}.png")
    else:
        result = subprocess.run([poppler, "-r", "108", "-png", str(pdf), str(output / "slide")],
                                capture_output=True, text=True, timeout=180)
        if result.returncode:
            raise RuntimeError(f"PDF rasterization failed: {result.stderr}")
    pages = sorted(output.glob("slide-*.png"), key=lambda path: int(path.stem.split("-")[-1]))
    if not pages:
        raise RuntimeError("PDF rasterization produced no pages")
    thumbnail_width, thumbnail_height = 480, 290
    sheet = Image.new("RGB", (thumbnail_width * 3, thumbnail_height * math.ceil(len(pages) / 3)), "#DCE3E8")
    for index, page_path in enumerate(pages):
        with Image.open(page_path) as rendered:
            thumb = ImageOps.contain(rendered, (464, 261))
            column, row = index % 3, index // 3
            sheet.paste(thumb, (column * thumbnail_width + 8, row * thumbnail_height + 8))
        ImageDraw.Draw(sheet).text((column * thumbnail_width + 10, row * thumbnail_height + 270), str(index + 1), fill="#17364A")
    sheet.save(output / "contact-sheet.png")
    return {"pdf": str(pdf), "contact_sheet": str(output / "contact-sheet.png"),
            "renderer": "LibreOffice", "viewer_uat": "not performed"}


def main():
    parser = argparse.ArgumentParser(description="School PPTX native authoring utilities")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("doctor")
    for command in ("inspect", "check", "preview"):
        subparser = commands.add_parser(command)
        subparser.add_argument("input", type=Path)
        if command == "preview":
            subparser.add_argument("--out-dir", required=True, type=Path)
            subparser.add_argument("--font-dir", action="append", default=[])
        else:
            subparser.add_argument("--out", type=Path)
        if command == "check":
            subparser.add_argument("--school-template", action="store_true")
    arguments = parser.parse_args()
    if arguments.command == "doctor":
        import importlib.util
        write_json(None, {"python": sys.executable, "native": "ready", "preview": {
            "soffice": shutil.which("soffice"), "pymupdf": bool(importlib.util.find_spec("pymupdf")),
            "pdftoppm": shutil.which("pdftoppm")}})
    elif arguments.command == "inspect":
        write_json(arguments.out, inspect(arguments.input))
    elif arguments.command == "check":
        report = check(arguments.input, arguments.school_template)
        write_json(arguments.out, report)
        print(f"{report['status']}: {report['pages']} pages, {len(report['errors'])} errors, {len(report['warnings'])} warnings")
        return 1 if report["errors"] else 0
    else:
        write_json(None, preview(arguments.input, arguments.out_dir, arguments.font_dir))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError, RuntimeError, ImportError, subprocess.TimeoutExpired) as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
