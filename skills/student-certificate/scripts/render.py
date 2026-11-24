"""Render a Markdown student certificate as DOCX and PDF."""
import argparse
from datetime import datetime
import json
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory
from zoneinfo import ZoneInfo
from pathlib import Path

import yaml
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH as Align
from docx.oxml.ns import qn
from docx.shared import Mm, Pt, RGBColor


def add_text(paragraph, content, font="STFangsong", size=15):
    run = paragraph.add_run(content)
    run.font.name = font
    run.font.size = Pt(size)
    run.font.color.rgb = RGBColor(0, 0, 0)
    run._element.get_or_add_rPr().rFonts.set(qn("w:eastAsia"), font)
    return run


def make_certificate(data, output):
    document = Document()
    page = document.sections[0]
    page.page_width, page.page_height = Mm(210), Mm(297)
    page.top_margin, page.bottom_margin = Mm(25), Mm(27)
    page.left_margin, page.right_margin = Mm(34), Mm(29)

    properties = document.styles["Title"].element.find(qn("w:pPr"))
    border = properties.find(qn("w:pBdr"))
    if border is not None:
        properties.remove(border)
    title = document.add_paragraph(style="Title")
    title.alignment = Align.CENTER
    title.paragraph_format.space_after = Mm(15)
    add_text(title, "证 明", "Songti SC", 19).bold = True

    body = document.add_paragraph()
    body.alignment = Align.JUSTIFY
    body.paragraph_format.first_line_indent = Pt(30)
    body.paragraph_format.line_spacing = Pt(31)
    body.paragraph_format.space_after = Mm(44)
    add_text(body, data["before_name"])
    add_text(body, data["student_name"]).underline = True
    add_text(body, data["after_name"])

    for field in ("issuer", "issued_on"):
        line = document.add_paragraph()
        line.alignment = Align.CENTER
        line.paragraph_format.left_indent = Mm(104)
        line.paragraph_format.line_spacing = Pt(31)
        line.paragraph_format.space_after = Pt(0)
        line.paragraph_format.keep_with_next = field == "issuer"
        add_text(line, data[field])
    document.save(output)


def read_certificate(source):
    lines = source.read_text(encoding="utf-8-sig").splitlines()
    if source.suffix.lower() != ".md" or not lines or lines[0] != "---":
        raise ValueError("请提供以 YAML 区块开头的 Markdown 文件。")
    try:
        end = lines.index("---", 1)
    except ValueError:
        raise ValueError("YAML 区块缺少结束分隔线。") from None

    fields = yaml.load("\n".join(lines[1:end]), Loader=yaml.BaseLoader)
    required = ("系部", "班级", "姓名", "学号", "证明事项", "出具部门")
    if not isinstance(fields, dict) or fields.keys() - set((*required, "出具日期")):
        raise ValueError("请使用模板中的 YAML 字段。")

    missing = []
    for key in required:
        value = fields.get(key, "")
        if not isinstance(value, str):
            missing.append(key)
            continue
        value = value.strip()
        if not value or "\n" in value or value.startswith("〔") and value.endswith("〕"):
            missing.append(key)
        fields[key] = value
    if missing:
        raise ValueError("请补充以下必填信息：" + "、".join(missing))

    if not re.fullmatch(r"[A-Za-z0-9]+", fields["学号"]):
        raise ValueError("学号须由英文字母或数字组成，不含空格。")

    issued_on = fields.get("出具日期", "")
    if not isinstance(issued_on, str) or "\n" in issued_on:
        raise ValueError("请将出具日期填写为单行文本，或留空使用当天日期。")
    issued_on = issued_on.strip()
    if not issued_on or issued_on == "____年__月__日":
        today = datetime.now(ZoneInfo("Asia/Shanghai")).date()
        issued_on = f"{today.year}年{today.month}月{today.day}日"

    closing = "\n".join(lines[end + 1:]).strip()
    if not closing or "\n" in closing:
        raise ValueError("请在 YAML 区块下方单独填写最后一句。")

    return {
        "before_name": f"兹证明{fields['系部']}{fields['班级']}",
        "student_name": fields["姓名"],
        "after_name": f"同学（学号：{fields['学号']}）{fields['证明事项']}。{closing}",
        "issuer": fields["出具部门"],
        "issued_on": issued_on,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    args = parser.parse_args()
    try:
        data = read_certificate(args.source)
    except (ValueError, yaml.YAMLError) as error:
        parser.error(str(error))

    template = Path(__file__).resolve().parents[1] / "templates" / "certificate.typ"
    with TemporaryDirectory() as directory:
        work = Path(directory)
        shutil.copyfile(template, work / "certificate.typ")
        (work / "data.json").write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")
        docx = work / "certificate.docx"
        pdf = work / "certificate.pdf"
        make_certificate(data, docx)
        subprocess.run(
            ["typst", "compile", "--input", "source=data.json", "certificate.typ", pdf.name],
            cwd=work,
            check=True,
        )
        shutil.copyfile(docx, args.source.with_suffix(".docx"))
        shutil.copyfile(pdf, args.source.with_suffix(".pdf"))


if __name__ == "__main__":
    main()
