import argparse
import json
from pathlib import Path
from zipfile import BadZipFile, ZipFile
from xml.etree import ElementTree


NAMESPACE = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def read_document(path):
    file_path = Path(path)
    if file_path.is_symlink() or not file_path.is_file():
        raise ValueError("输入必须为真实普通文件")
    with ZipFile(file_path) as archive:
        return ElementTree.fromstring(archive.read("word/document.xml"))


def text_sequence(document):
    return [node.text or "" for node in document.iter(NAMESPACE + "t")]


def integer_attribute(node, name, default=0):
    return int(node.get(NAMESPACE + name, str(default)))


def audit(document, source=None):
    errors = []
    warnings = []
    tables = list(document.iter(NAMESPACE + "tbl"))
    sections = list(document.iter(NAMESPACE + "sectPr"))
    if len(sections) != 1:
        errors.append("仅支持单节几何审计；多节文档需要逐节核对")
    usable_width = None
    if len(sections) == 1:
        page_size = sections[0].find(NAMESPACE + "pgSz")
        margins = sections[0].find(NAMESPACE + "pgMar")
        if page_size is not None and margins is not None:
            usable_width = integer_attribute(page_size, "w") - sum(
                integer_attribute(margins, side) for side in ("left", "right", "gutter")
            )
    if usable_width is None:
        errors.append("无法确定版心宽度")
    for table_index, table in enumerate(tables, 1):
        grid = table.find(NAMESPACE + "tblGrid")
        properties = table.find(NAMESPACE + "tblPr")
        if grid is None or properties is None:
            errors.append(f"表{table_index}缺少显式几何")
            continue
        widths = [integer_attribute(column, "w") for column in grid]
        declared = properties.find(NAMESPACE + "tblW")
        indent = properties.find(NAMESPACE + "tblInd")
        offset = integer_attribute(indent, "w") if indent is not None else 0
        if declared is None or declared.get(NAMESPACE + "type") != "dxa":
            errors.append(f"表{table_index}缺少 dxa 总宽")
        elif integer_attribute(declared, "w") != sum(widths):
            errors.append(f"表{table_index}总宽与网格不一致")
        if usable_width is not None and sum(widths) + max(offset, 0) > usable_width:
            errors.append(f"表{table_index}超出版心")
        for row_index, row in enumerate(table.findall(NAMESPACE + "tr"), 1):
            logical_column = 0
            for cell in row.findall(NAMESPACE + "tc"):
                cell_properties = cell.find(NAMESPACE + "tcPr")
                if cell_properties is None:
                    errors.append(f"表{table_index}行{row_index}缺少单元格属性")
                    continue
                span_node = cell_properties.find(NAMESPACE + "gridSpan")
                span = integer_attribute(span_node, "val", 1) if span_node is not None else 1
                width_node = cell_properties.find(NAMESPACE + "tcW")
                expected = sum(widths[logical_column:logical_column + span])
                if width_node is None or width_node.get(NAMESPACE + "type") != "dxa" or integer_attribute(width_node, "w") != expected:
                    errors.append(f"表{table_index}行{row_index}列{logical_column + 1}宽度不一致")
                paragraphs = cell.findall(NAMESPACE + "p")
                if len(paragraphs) > 1 and any(not list(paragraph.iter(NAMESPACE + "t")) for paragraph in paragraphs):
                    warnings.append(f"表{table_index}行{row_index}有待复核空段；不能自动删含锚点的段落")
                logical_column += span
            if logical_column != len(widths):
                errors.append(f"表{table_index}行{row_index}列跨度与网格不一致")
    identical = None
    if source is not None:
        identical = text_sequence(document) == text_sequence(source)
        if not identical:
            errors.append("文字节点序列与原卷不一致；需进一步定位字符和边界差异")
    return {"tables": len(tables), "usable_width_twips": usable_width,
            "text_nodes_identical": identical, "errors": errors, "warnings": warnings,
            "scope": "只读单节 OOXML 几何与文字节点检查，不替代技术审题或视觉验收"}


def main():
    parser = argparse.ArgumentParser(description="只读核对实操 DOCX 的文字与表格几何")
    parser.add_argument("--input", required=True)
    parser.add_argument("--source")
    arguments = parser.parse_args()
    try:
        report = audit(read_document(arguments.input), read_document(arguments.source) if arguments.source else None)
    except (ValueError, OSError, ElementTree.ParseError, KeyError, BadZipFile) as error:
        parser.exit(2, f"审计失败：{error}\n")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
