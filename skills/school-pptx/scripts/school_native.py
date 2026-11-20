from copy import deepcopy
from pathlib import Path

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE, MSO_CONNECTOR
from pptx.enum.text import MSO_ANCHOR, MSO_AUTO_SIZE, PP_ALIGN
from pptx.oxml.xmlchemy import OxmlElement
from pptx.opc.constants import RELATIONSHIP_TYPE as RT
from pptx.util import Inches, Pt


ROOT = Path(__file__).resolve().parents[1]
BLUE = "0089C9"
GREEN = "519D46"
INK = "17364A"
MUTED = "526371"
PALE = "EEF5F8"
FONT = "Microsoft YaHei"


def color(value):
    return RGBColor.from_string(value.lstrip("#"))


def set_font(run, size, fill, bold=False, family=FONT):
    run.font.name = family
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = color(fill)
    properties = run._r.get_or_add_rPr()
    for tag in ("a:ea", "a:cs"):
        element = properties.find(tag, properties.nsmap)
        if element is None:
            element = OxmlElement(tag)
            properties.append(element)
        element.set("typeface", family)
    properties.set("lang", "zh-CN")


def text(slide, value, x, y, width, height, size=24, fill=INK,
         bold=False, align="left", name="text", family=FONT):
    shape = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(width), Inches(height))
    shape.name = "school:" + name
    frame = shape.text_frame
    frame.clear()
    frame.word_wrap = True
    frame.auto_size = MSO_AUTO_SIZE.NONE
    frame.margin_left = frame.margin_right = Inches(0.02)
    frame.margin_top = frame.margin_bottom = Inches(0.02)
    frame.vertical_anchor = MSO_ANCHOR.MIDDLE
    for index, line in enumerate(str(value).split("\n")):
        paragraph = frame.paragraphs[0] if index == 0 else frame.add_paragraph()
        paragraph.alignment = {"left": PP_ALIGN.LEFT, "center": PP_ALIGN.CENTER,
                               "right": PP_ALIGN.RIGHT}[align]
        paragraph.line_spacing = 1.15
        paragraph.space_after = Pt(4)
        run = paragraph.add_run()
        run.text = line
        set_font(run, size, fill, bold, family)
    return shape


def rect(slide, x, y, width, height, fill=PALE, name="panel", rounded=False):
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(width), Inches(height))
    shape.name = "school:" + name
    shape.fill.solid()
    shape.fill.fore_color.rgb = color(fill)
    shape.line.fill.background()
    return shape


def line(slide, x1, y1, x2, y2, fill=BLUE, width=2):
    shape = slide.shapes.add_connector(MSO_CONNECTOR.STRAIGHT,
                                      Inches(x1), Inches(y1), Inches(x2), Inches(y2))
    shape.name = "school:connector"
    shape.line.color.rgb = color(fill)
    shape.line.width = Pt(width)
    return shape


def picture(slide, path, x, y, width, height, fit="contain"):
    path = Path(path).resolve()
    with Image.open(path) as image:
        image_width, image_height = image.size
    if fit == "cover":
        shape = slide.shapes.add_picture(str(path), Inches(x), Inches(y),
                                         width=Inches(width), height=Inches(height))
        image_ratio = image_width / image_height
        box_ratio = width / height
        if image_ratio > box_ratio:
            crop = (1 - box_ratio / image_ratio) / 2
            shape.crop_left = shape.crop_right = crop
        else:
            crop = (1 - image_ratio / box_ratio) / 2
            shape.crop_top = shape.crop_bottom = crop
    elif fit == "contain":
        scale = min(width / image_width, height / image_height)
        actual_width, actual_height = image_width * scale, image_height * scale
        shape = slide.shapes.add_picture(str(path), Inches(x + (width - actual_width) / 2),
                                         Inches(y + (height - actual_height) / 2),
                                         width=Inches(actual_width), height=Inches(actual_height))
    else:
        raise ValueError("fit must be contain or cover")
    shape.name = "school:picture"
    return shape


class SchoolDeck:
    def __init__(self, template=None):
        self.presentation = Presentation(str(template or ROOT / "assets/school-template.pptx"))
        self.seeds = list(self.presentation.slides)
        if len(self.seeds) != 5:
            raise ValueError("SchoolDeck expects the five-page bundled template; edit custom templates directly")
        self.generated = []
        self.families = {}

    def _clone(self, index, family):
        source = self.seeds[index]
        slide = self.presentation.slides.add_slide(source.slide_layout)
        for shape in list(slide.shapes):
            shape.element.getparent().remove(shape.element)
        relationships = {}
        for relation in source.part.rels.values():
            if relation.reltype in (RT.SLIDE_LAYOUT, RT.NOTES_SLIDE):
                continue
            target = relation.target_ref if relation.is_external else relation.target_part
            relationships[relation.rId] = slide.part.relate_to(
                target, relation.reltype, is_external=relation.is_external)
        for shape in source.shapes:
            element = deepcopy(shape.element)
            for descendant in element.iter():
                for key, value in list(descendant.attrib.items()):
                    if key.startswith("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"):
                        if value in relationships:
                            descendant.set(key, relationships[value])
            slide.shapes._spTree.insert_element_before(element, "p:extLst")
        source_background = source.element.find("p:cSld/p:bg", source.element.nsmap)
        if source_background is not None:
            slide.element.find("p:cSld", slide.element.nsmap).insert(0, deepcopy(source_background))
        for attribute in ("showMasterSp", "showMasterPhAnim"):
            if attribute in source.element.attrib:
                slide.element.set(attribute, source.element.get(attribute))
        self.generated.append(slide)
        self.families[slide.slide_id] = family
        return slide

    def cover(self, title, subtitle="", notes=""):
        slide = self._clone(0, "cover")
        self._clear(slide)
        text(slide, title, 1.15, 2.05, 11, 1.65, 60, "FFFFFF", True, "center", "cover-title")
        if subtitle:
            text(slide, subtitle, 1.4, 3.95, 10.5, 1.1, 20, "FFFFFF", align="center", name="cover-subtitle")
        self.notes(slide, notes)
        return slide

    def contents(self, items, notes=""):
        if not 1 <= len(items) <= 7:
            raise ValueError("Use 1–7 short agenda entries or compose a custom contents page")
        slide = self._clone(1, "contents")
        self._clear(slide)
        step = min(0.70, 4.24 / len(items))
        top = 1.72 + (4.24 - len(items) * step) / 2
        for index, item in enumerate(items):
            position = top + index * step
            rect(slide, 4.38, position + (step - 0.52) / 2, 0.58, 0.52, BLUE, "agenda-marker")
            text(slide, f"{index + 1:02}", 4.38, position + (step - 0.52) / 2, 0.58, 0.52,
                 19, "FFFFFF", True, "center", "agenda-number")
            text(slide, item, 5.15, position, 7.58, step,
                 32, "000000", name="agenda-item")
        self.notes(slide, notes)
        return slide

    def section(self, number, title, notes=""):
        slide = self._clone(2, "section")
        self._clear(slide)
        shape = text(slide, title, 0.91, 1.87, 11.5, 3.12,
                     66, "000000", name="section-title")
        shape.text_frame.vertical_anchor = MSO_ANCHOR.BOTTOM
        self.notes(slide, notes)
        return slide

    def content(self, title, kicker="", notes=""):
        slide = self._clone(3, "content")
        self._clear(slide)
        shape = text(slide, title, 0.92, 0.4, 11.49, 1.45,
                     48, "000000", name="title")
        for paragraph in shape.text_frame.paragraphs:
            paragraph.alignment = PP_ALIGN.JUSTIFY
        if kicker:
            text(slide, kicker, 0.92, 2.05, 11.49, 0.35,
                 14, MUTED, name="kicker")
        self.notes(slide, notes)
        return slide

    def closing(self, message="", notes=""):
        slide = self._clone(4, "closing")
        if message:
            raise ValueError("The merged school closing page is fixed; put additional remarks in notes")
        self.notes(slide, notes)
        return slide

    @staticmethod
    def _clear(slide):
        for shape in list(slide.shapes):
            shape.element.getparent().remove(shape.element)

    @staticmethod
    def notes(slide, value):
        if value:
            slide.notes_slide.notes_text_frame.text = value

    def save(self, path):
        path = Path(path).resolve()
        if path.exists():
            raise FileExistsError(f"Choose a new output filename: {path}")
        if not self.generated:
            raise ValueError("No slides authored")
        slide_ids = self.presentation.slides._sldIdLst
        seed_ids = {slide.slide_id for slide in self.seeds}
        for element in list(slide_ids):
            if int(element.id) in seed_ids:
                self.presentation.part.drop_rel(element.rId)
                slide_ids.remove(element)
        path.parent.mkdir(parents=True, exist_ok=True)
        self.presentation.save(str(path))
        return path
