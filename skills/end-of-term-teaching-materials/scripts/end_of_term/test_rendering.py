"""Display regression tests; fixtures contain no real students or course data."""
import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from end_of_term import _engine as engine


class ScoreDisplayTests(unittest.TestCase):
    def test_decimal_precision_blank_and_review_values(self):
        cases = {'': '', '0': '0', '100.0': '100', '82.25': '82.3',
                 '91.6666666667': '91.7', '87.249?': '87.2?', '0.04': '0'}
        for source, expected in cases.items():
            self.assertEqual(engine.display_score(source), expected)

    def test_scorebook_rounds_half_up_and_splits_names(self):
        self.assertEqual(engine.scorebook_display_score('82.5'), '83')
        self.assertEqual(engine.scorebook_display_score('82.49'), '82')
        self.assertEqual(engine.scorebook_display_score(''), '')
        self.assertEqual(engine.name_items('专业甲、专业乙'), ['专业甲', '专业乙'])
        self.assertEqual(engine.name_items(['班级甲班', '班级乙'], classes=True), ['班级甲班', '班级乙班'])

    def test_display_does_not_rewrite_inputs_or_calculation(self):
        row = {'考勤': '96', '作业': '82.25', '期末': '61', '任务1': '79.555555'}
        original = copy.deepcopy(row)
        before = engine.derived_score_values(row, [{'hours': 20}])
        self.assertEqual(engine.scorebook_source_values(row), ['96', '82', '61'])
        self.assertEqual(engine.task_score(row, 1), '79.555555')
        self.assertEqual(row, original)
        self.assertEqual(engine.derived_score_values(row, [{'hours': 20}]), before)

    def test_full_task_name_is_not_truncated_and_reserves_stay_blank(self):
        name = '综合控制线路安装接线调试及安全操作检验' * 3
        cell = '\n'.join(engine.task_name_cells(0, 0, 45, 145, {'task_name':name,'hours':20}))
        self.assertIn(name, cell)
        self.assertEqual(engine.task_name_cells(0,0,45,145,{'task_name':name,'hours':0}), [])
        self.assertEqual(engine.task_name_cells(0,0,45,145,{'task_name':'预留任务1','hours':20}), [])

    def test_cover_fields_expand_together_without_font_fitting(self):
        course = '综合自动化系统运行维护与调试课程'
        geometry = engine.cover_field_geometry([course, '示例教师'])
        self.assertGreater(geometry['value_w'], 228)
        self.assertAlmostEqual(geometry['label_x'] * 2 + geometry['label_w'] + geometry['value_w'], 595.3)
        course_lines = []
        teacher_lines = []
        engine.cover_line_field(course_lines, 522, '科目', course, **geometry)
        engine.cover_line_field(teacher_lines, 556, '教师', '示例教师', **geometry)
        self.assertEqual(course_lines[-1].split(',')[:2], teacher_lines[-1].split(',')[:2])
        self.assertNotIn('#pfit', '\n'.join(course_lines + teacher_lines))

    def test_cover_wrapping_reserves_vertical_space(self):
        course = '综合自动化系统运行维护' * 5
        geometry = engine.cover_field_geometry([course])
        self.assertLessEqual(geometry['value_w'], 423.3)
        lines = []
        extra = engine.cover_line_field(lines, 522, '科目', course, **geometry)
        self.assertGreater(extra, 0)
        self.assertIn(course, '\n'.join(lines))


if __name__ == '__main__':
    unittest.main()
