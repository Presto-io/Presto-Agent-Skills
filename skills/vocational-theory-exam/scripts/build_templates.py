import argparse
import io
import re
from copy import deepcopy
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

WORD = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def paragraph(prototype, text):
    result = deepcopy(prototype)
    for child in list(result):
        if child.tag != WORD + "pPr":
            result.remove(child)
    run = ET.SubElement(result, WORD + "r")
    properties = prototype.find("./" + WORD + "r/" + WORD + "rPr")
    if properties is not None:
        run.append(deepcopy(properties))
    ET.SubElement(run, WORD + "t").text = text
    return result


def build(source, destination, answers):
    with ZipFile(source) as archive:
        data = archive.read("word/document.xml")
        for event, namespace in ET.iterparse(io.BytesIO(data), events=["start-ns"]):
            prefix, uri = namespace
            if prefix not in {"xml", "xmlns"}:
                ET.register_namespace(prefix, uri)
        document = ET.fromstring(data)
        body = document.find(WORD + "body")
        prototypes = body.findall(WORD + "p")
        section = deepcopy(body.find(WORD + "sectPr"))
        identity = deepcopy(prototypes[0])
        for node in identity.iter(WORD + "t"):
            if node.text == "西安市职业技能等级认定":
                node.text = "{{认定机构}}职业技能等级认定"
        for child in list(body):
            body.remove(child)
        body.append(identity)
        title = "{{职业名称}}{{等级}}理论试卷{{套号}}" + ("答案与评分说明" if answers else "")
        body.append(paragraph(prototypes[1], title))
        entries = ["考核时间：{{分钟}}分钟    满分：{{总分}}分", "{{考生须知或评阅规则}}", "{{题型标题与分值}}"]
        entries += ["{{题号}}．{{正确答案}}", "{{解析与逐点评分}}"] if answers else ["{{题号}}．{{题干}}", "A．{{选项A}}", "B．{{选项B}}", "C．{{选项C}}", "D．{{选项D}}", "{{答题区}}"]
        for text in entries:
            body.append(paragraph(prototypes[2] if text.startswith("{{题型") else prototypes[3], text))
        body.append(section)
        payload = ET.tostring(document, encoding="utf-8", xml_declaration=True)
        declarations = re.findall(rb'xmlns:([\w]+)="([^"]+)"', data.split(b">", 2)[1])
        for prefix, uri in declarations:
            attribute = b"xmlns:" + prefix + b'="' + uri + b'"'
            if b"xmlns:" + prefix + b"=" not in payload:
                payload = payload.replace(b"<w:document", b"<w:document " + attribute, 1)
        with ZipFile(destination, "w") as output:
            for member in archive.infolist():
                output.writestr(member, payload if member.filename == "word/document.xml" else archive.read(member.filename))


def main():
    parser = argparse.ArgumentParser(description="从母版页面框架构建理论模板，不覆盖已有目标")
    parser.add_argument("--source", required=True)
    parser.add_argument("--output-dir", required=True)
    arguments = parser.parse_args()
    root = Path(arguments.output_dir)
    names = ["theory-paper-template.docx", "theory-answer-template.docx"]
    if not root.is_dir() or root.is_symlink() or any((root / name).exists() for name in names):
        parser.error("输出必须是真实目录且目标文件不存在")
    for name, answers in zip(names, [False, True]):
        build(arguments.source, root / name, answers)


if __name__ == "__main__":
    main()
