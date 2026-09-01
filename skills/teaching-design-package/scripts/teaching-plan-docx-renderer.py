#!/usr/bin/env python3
import copy
import json
import os
import sys
import tempfile
import zipfile
from pathlib import Path
from xml.etree import ElementTree as etree


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
W = f"{{{W_NS}}}"


def fail(message):
    print(f"teaching-plan-docx-renderer.py: {message}", file=sys.stderr)
    raise SystemExit(1)


def set_cjk_font(run):
    properties = run.find(W + "rPr")
    if properties is None:
        properties = etree.Element(W + "rPr")
        run.insert(0, properties)
    fonts = properties.find(W + "rFonts")
    if fonts is None:
        fonts = etree.SubElement(properties, W + "rFonts")
    for name in ["ascii", "hAnsi", "eastAsia"]:
        set_attr(fonts, name, "宋体")
    language = properties.find(W + "lang")
    if language is None:
        language = etree.SubElement(properties, W + "lang")
    set_attr(language, "eastAsia", "zh-CN")


def set_text(element, value):
    nodes = element.findall(".//" + W + "t")
    if not nodes:
        if str(value) == "":
            return
        paragraph = element if element.tag == W + "p" else element.find(".//" + W + "p")
        if paragraph is None:
            fail("template element has no paragraph for text")
        run = etree.SubElement(paragraph, W + "r")
        text_node = etree.SubElement(run, W + "t")
        text_node.text = str(value)
        set_cjk_font(run)
        return
    nodes[0].text = str(value)
    for node in nodes[1:]:
        node.text = ""
    for run in element.findall(".//" + W + "r"):
        set_cjk_font(run)


def set_paragraph_runs(paragraph, pieces):
    runs = paragraph.findall("./" + W + "r")
    if not runs:
        fail("template paragraph has no runs")
    for run in runs:
        paragraph.remove(run)
    templates = [copy.deepcopy(run) for run in runs]
    for index, piece in enumerate(pieces):
        kind, value = piece
        if kind == "tab":
            run = copy.deepcopy(templates[min(index, len(templates) - 1)])
            for child in list(run):
                if child.tag != W + "rPr":
                    run.remove(child)
            etree.SubElement(run, W + "tab")
        else:
            run = copy.deepcopy(templates[min(index, len(templates) - 1)])
            text_nodes = run.findall("./" + W + "t")
            if text_nodes:
                text_nodes[0].text = str(value)
                for node in text_nodes[1:]:
                    node.text = ""
            else:
                for child in list(run):
                    if child.tag != W + "rPr":
                        run.remove(child)
                text_node = etree.SubElement(run, W + "t")
                text_node.text = str(value)
        set_cjk_font(run)
        paragraph.append(run)


def set_attr(element, name, value):
    element.set(W + name, str(value))


def metadata_paragraph(prototype, text, alignment):
    paragraph = copy.deepcopy(prototype)
    set_text(paragraph, text)
    for run in paragraph.findall("./" + W + "r"):
        for child in list(run):
            if child.tag == W + "tab":
                run.remove(child)
    properties = paragraph.find(W + "pPr")
    if properties is None:
        properties = etree.Element(W + "pPr")
        paragraph.insert(0, properties)
    for name in ["tabs", "ind", "jc", "spacing"]:
        for child in properties.findall(W + name):
            properties.remove(child)
    spacing = etree.SubElement(properties, W + "spacing")
    set_attr(spacing, "before", 0)
    set_attr(spacing, "after", 0)
    set_attr(spacing, "line", 210)
    set_attr(spacing, "lineRule", "exact")
    indent = etree.SubElement(properties, W + "ind")
    set_attr(indent, "left", 0)
    set_attr(indent, "right", 0)
    set_attr(indent, "firstLine", 0)
    justification = etree.SubElement(properties, W + "jc")
    set_attr(justification, "val", alignment)
    return paragraph


def metadata_cell(prototype, text, width, alignment):
    cell = etree.Element(W + "tc")
    properties = etree.SubElement(cell, W + "tcPr")
    cell_width = etree.SubElement(properties, W + "tcW")
    set_attr(cell_width, "w", width)
    set_attr(cell_width, "type", "dxa")
    margins = etree.SubElement(properties, W + "tcMar")
    for side in ["left", "right"]:
        margin = etree.SubElement(margins, W + side)
        set_attr(margin, "w", 140 if side == "left" else 100)
        set_attr(margin, "type", "dxa")
    vertical = etree.SubElement(properties, W + "vAlign")
    set_attr(vertical, "val", "center")
    cell.append(metadata_paragraph(prototype, text, alignment))
    return cell


def metadata_table(first_prototype, second_prototype, metadata):
    table = etree.Element(W + "tbl")
    properties = etree.SubElement(table, W + "tblPr")
    table_width = etree.SubElement(properties, W + "tblW")
    set_attr(table_width, "w", 8688)
    set_attr(table_width, "type", "dxa")
    justification = etree.SubElement(properties, W + "jc")
    set_attr(justification, "val", "center")
    layout = etree.SubElement(properties, W + "tblLayout")
    set_attr(layout, "type", "fixed")
    borders = etree.SubElement(properties, W + "tblBorders")
    for side in ["top", "left", "bottom", "right", "insideH", "insideV"]:
        border = etree.SubElement(borders, W + side)
        set_attr(border, "val", "nil")
    grid = etree.SubElement(table, W + "tblGrid")
    indent = etree.SubElement(properties, W + "tblInd")
    set_attr(indent, "w", 40)
    set_attr(indent, "type", "dxa")
    widths = [1400, 2964, 1400, 2924]
    for width in widths:
        column = etree.SubElement(grid, W + "gridCol")
        set_attr(column, "w", width)
    rows = [
        (first_prototype, ["专业名称：", metadata["major_name"], "课程名称：", metadata["course_name"]]),
        (second_prototype, ["授课教师：", metadata["teacher_name"], "授课班级：", metadata["class_name"]]),
    ]
    for prototype, values in rows:
        row = etree.SubElement(table, W + "tr")
        row_properties = etree.SubElement(row, W + "trPr")
        height = etree.SubElement(row_properties, W + "trHeight")
        set_attr(height, "val", 300)
        set_attr(height, "hRule", "atLeast")
        for index, (value, width) in enumerate(zip(values, widths)):
            row.append(metadata_cell(prototype, value, width, "left"))
    return table


def spacing_paragraph(prototype, before):
    paragraph = copy.deepcopy(prototype)
    for run in paragraph.findall("./" + W + "r"):
        paragraph.remove(run)
    properties = paragraph.find(W + "pPr")
    if properties is None:
        properties = etree.Element(W + "pPr")
        paragraph.insert(0, properties)
    for child in list(properties):
        if child.tag in (W + "tabs", W + "spacing", W + "ind", W + "jc"):
            properties.remove(child)
    spacing = etree.SubElement(properties, W + "spacing")
    set_attr(spacing, "before", before)
    set_attr(spacing, "after", 0)
    set_attr(spacing, "line", 1)
    set_attr(spacing, "lineRule", "exact")
    return paragraph


def compact_weekday(value):
    return str(value).replace("周日", "7").replace("周一", "1").replace("周二", "2").replace("周三", "3").replace("周四", "4").replace("周五", "5").replace("周六", "6").replace("-", " ")


def compact_week(value):
    return str(value).replace("-", " ")


def format_title_week(model):
    course = model["scheduling"]["course"]
    school_year = course["school_year"].replace("学年", " 学年")
    semester = course["semester"]
    term_week = str(course["term_week"]).replace("-", " - ")
    return f"{school_year}{semester}第{term_week}周"


def build_rows(model, template_rows):
    schedule = model["schedule"]["tasks"]
    if not schedule:
        fail("schedule has no tasks")
    task_row = template_rows[0]
    header_row = template_rows[1]
    single_row = template_rows[4]
    merged_first_row = template_rows[5]
    merged_next_row = template_rows[6]
    rows = []
    for task_index, task in enumerate(schedule, start=1):
        task_copy = copy.deepcopy(task_row)
        cells = task_copy.findall("./" + W + "tc")
        if len(cells) != 4:
            fail("task template row must have four cells")
        for cell, value in zip(cells, [f"学习任务{task_index} 名称：", task["title"], "学时", f'{task["total_hours"]}H']):
            set_text(cell, value)
        rows.append(task_copy)
        if task_index == 1:
            rows.append(copy.deepcopy(header_row))
        for stage_index, stage in enumerate(task["stages"], start=1):
            stage_rows = stage["rows"]
            for row_index, item in enumerate(stage_rows):
                if len(stage_rows) == 1:
                    row_copy = copy.deepcopy(single_row)
                elif row_index == 0:
                    row_copy = copy.deepcopy(merged_first_row)
                else:
                    row_copy = copy.deepcopy(merged_next_row)
                cells = row_copy.findall("./" + W + "tc")
                if len(cells) != 5:
                    fail("activity template row must have five cells")
                values = [
                    f"学习环节{stage_index} 名称：{stage['title']}" if row_index == 0 else "",
                    item["title"],
                    compact_week(item["term_week"]),
                    compact_weekday(item["weekday"]),
                    item["hours"],
                ]
                for cell, value in zip(cells, values):
                    set_text(cell, value)
                rows.append(row_copy)
    return rows


def render(model_path, template_path, output_path):
    model = json.loads(Path(model_path).read_text(encoding="utf-8"))
    template_path = Path(template_path)
    output_path = Path(output_path)
    if not template_path.is_file():
        fail(f"template not found: {template_path}")
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="tdpkg-docx-") as temp_name:
        temp_dir = Path(temp_name)
        with zipfile.ZipFile(template_path) as archive:
            archive.extractall(temp_dir)
        document_path = temp_dir / "word" / "document.xml"
        for _event, namespace in etree.iterparse(document_path, events=("start-ns",)):
            prefix, uri = namespace
            etree.register_namespace(prefix, uri)
        tree = etree.parse(document_path)
        body = tree.getroot().find(W + "body")
        paragraphs = body.findall("./" + W + "p")
        tables = body.findall("./" + W + "tbl")
        if len(paragraphs) < 5 or len(tables) != 1:
            fail("template body structure mismatch")

        metadata = model["metadata"]
        set_text(paragraphs[0], format_title_week(model))
        set_text(paragraphs[1], "工学一体化课程/基本技能课程授课进度计划表")
        title_properties = paragraphs[1].find(W + "pPr")
        if title_properties is None:
            title_properties = etree.Element(W + "pPr")
            paragraphs[1].insert(0, title_properties)
        title_spacing = title_properties.find(W + "spacing") if title_properties is not None else None
        if title_spacing is None:
            title_spacing = etree.SubElement(title_properties, W + "spacing")
        set_attr(title_spacing, "after", 370)
        info_table = metadata_table(paragraphs[2], paragraphs[3], metadata)
        info_index = list(body).index(paragraphs[2])
        body.remove(paragraphs[2])
        body.remove(paragraphs[3])
        body.insert(info_index, info_table)
        body.insert(info_index + 1, spacing_paragraph(paragraphs[3], 370))
        set_paragraph_runs(paragraphs[-1], [
            ("text", "系主任："),
            ("tab", ""),
            ("text", "教研室主任："),
            ("tab", ""),
            ("text", f'制表：{metadata["teacher_name"]}'),
        ])

        table = tables[0]
        template_rows = table.findall("./" + W + "tr")
        generated_rows = build_rows(model, template_rows)
        for row in template_rows:
            table.remove(row)
        for row in generated_rows:
            table.append(row)

        sect_pr = body.find(W + "sectPr")
        if sect_pr is None:
            fail("template section properties missing")
        page_size = sect_pr.find(W + "pgSz")
        page_margin = sect_pr.find(W + "pgMar")
        expected_page = {W + "w": "11906", W + "h": "16838"}
        expected_margin = {W + "top": "1360", W + "bottom": "1360", W + "left": "1600", W + "right": "1600"}
        if page_size is None or any(page_size.get(key) != value for key, value in expected_page.items()):
            fail("template page size differs from the approved A4 format")
        if page_margin is None or any(page_margin.get(key) != value for key, value in expected_margin.items()):
            fail("template margins differ from the approved format")

        tree.write(document_path, encoding="UTF-8", xml_declaration=True)
        temp_output = output_path.with_suffix(output_path.suffix + ".tmp")
        with zipfile.ZipFile(temp_output, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(temp_dir.rglob("*")):
                if path.is_file():
                    name = path.relative_to(temp_dir).as_posix()
                    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                    info.compress_type = zipfile.ZIP_DEFLATED
                    info.external_attr = 0o600 << 16
                    archive.writestr(info, path.read_bytes())
        os.replace(temp_output, output_path)


if __name__ == "__main__":
    if len(sys.argv) != 4:
        fail("usage: teaching-plan-docx-renderer.py <model.json> <template.docx> <output.docx>")
    render(sys.argv[1], sys.argv[2], sys.argv[3])
