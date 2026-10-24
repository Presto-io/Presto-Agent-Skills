"""Verify job emphasis preserves evidence and course/grade associations."""

from __future__ import annotations

import copy
from pathlib import Path
import subprocess
import tempfile
import unittest

import fitz

from graduate_resume_emphasis import emphasis_spans, ordered_courses, relevant_terms
from graduate_resume_layout import project_containers
from graduate_resume_typst import _content, emit_page_body
from graduate_resume_typst_runtime import resolve_typst_executable


class EmphasisContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.terms = relevant_terms({"headline": "电气自动化技术员"})

    def emphasized(self, value: str, academic: bool = False) -> list[str]:
        return [value[start:end] for start, end in emphasis_spans(value, self.terms, academic)]

    def test_role_overrides_generic_intention_and_ascii_terms_have_boundaries(self) -> None:
        terms = relevant_terms({"headline": "电气自动化技术员"}, "行政文员：熟练使用Office")
        self.assertIn("Office", terms)
        self.assertNotIn("PLC", terms)
        self.assertEqual(self.emphasized("使用PLCSimulator学习PLC。"), ["PLC"])

    def test_negative_ability_and_density_are_not_misleading(self) -> None:
        self.assertEqual(self.emphasized("未掌握PLC及梯形图；仅了解变频器。"), [])
        self.assertLessEqual(len(self.emphasized("PLC梯形图接线与调试，使用变频器排查故障。")), 3)

    def test_grades_are_related_high_and_explicitly_on_a_hundred_point_scale(self) -> None:
        self.assertIn("95分", self.emphasized("PLC（95分）", True))
        self.assertIn("95/100", self.emphasized("PLC（95/100）", True))
        self.assertNotIn("70分", self.emphasized("PLC（70分）", True))
        self.assertNotIn("95分", self.emphasized("高等数学95分；PLC70分", True))
        self.assertNotIn("4.0", self.emphasized("PLC绩点4.0", True))
        self.assertNotIn("150分", self.emphasized("PLC150分", True))
        self.assertIn("专业排名前4%", self.emphasized("专业排名前4%；二等奖学金", True))
        self.assertEqual(self.emphasized("专业排名前40%", True), [])

    def test_courses_move_with_grades_without_changing_source(self) -> None:
        data = {"candidate": {"name": "学生", "headline": "电气自动化技术员"}, "education": [{"id": "edu-001", "school": "学院", "courses": ["高等数学95分", "PLC70分", "电气制图92分"]}]}
        before = copy.deepcopy(data)
        containers = project_containers(data)
        values = [value for key, value in containers[1].fields if key.startswith("courses[")]
        self.assertEqual(values, ["电气制图92分", "PLC70分", "高等数学95分"])
        self.assertEqual(data, before)
        self.assertEqual(ordered_courses("高等数学95分；PLC70分", self.terms), "PLC70分；高等数学95分")
        self.assertEqual(ordered_courses("高等数学、PLC；其余课程", self.terms), "高等数学、PLC；其余课程")
        targeted = relevant_terms(data["candidate"], "PLC调试工程师；PLC编程")
        self.assertEqual(ordered_courses("电气制图92分；PLC70分", targeted, "PLC调试工程师；PLC编程"), "PLC70分；电气制图92分")

    def test_emphasis_escapes_typst_and_education_has_separate_lines(self) -> None:
        content = _content("PLC #panic[危险]", self.terms)
        self.assertIn("#strong[PLC]", content)
        self.assertIn(r"\#panic\[危险\]", content)
        containers = project_containers({"candidate": {"name": "学生", "headline": "电气自动化"}, "education": [{"id": "edu-001", "school": "学院", "courses": ["PLC95分"], "honors": ["专业排名前4%"]}]})
        body = emit_page_body(containers, "modern")
        self.assertLess(body.index("成绩与荣誉"), body.index("相关课程"))
        self.assertIn("#linebreak()", body)
        self.assertIn("#strong[95分]", body)

    def test_pdf_has_real_bold_grades_and_no_literal_markup(self) -> None:
        skill_root = Path(__file__).resolve().parent.parent
        containers = project_containers({"candidate": {"name": "学生", "headline": "电气自动化"}, "education": [{"id": "edu-001", "school": "学院", "courses": ["电气制图95分", "PLC70分"], "honors": ["专业排名前4%"]}]})
        with resolve_typst_executable() as executable, tempfile.TemporaryDirectory() as temporary:
            probe = Path(temporary) / "emphasis.typ"
            probe.write_text((skill_root / "templates/resume-themes.typ").read_text(encoding="utf-8") + "\n" + emit_page_body(containers, "modern", function="resume-page"), encoding="utf-8")
            result = subprocess.run([str(executable.snapshot_path), "compile", str(probe), "--font-path", str(skill_root / "fonts"), "--ignore-system-fonts"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            with fitz.open(probe.with_suffix(".pdf")) as document:
                text = document[0].get_text()
                self.assertNotIn("[", text)
                self.assertNotIn("*", text)
                self.assertLess(text.index("成绩与荣誉"), text.index("相关课程"))
                spans = [span for block in document[0].get_text("dict")["blocks"] for line in block.get("lines", []) for span in line["spans"]]
                bold_text = "".join(span["text"] for span in spans if "Bold" in span["font"])
                regular_text = "".join(span["text"] for span in spans if "Bold" not in span["font"])
                self.assertIn("95分", "".join(bold_text.split()))
                self.assertIn("70分", "".join(regular_text.split()))


if __name__ == "__main__":
    unittest.main()
