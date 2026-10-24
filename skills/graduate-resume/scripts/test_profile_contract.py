import unittest

from graduate_resume_profile import personal_fields, paragraph_text


class ProfileContractTests(unittest.TestCase):
    def test_explicit_personal_fields_do_not_require_inferred_gender(self) -> None:
        self.assertEqual(
            personal_fields("出生日期：2006年3月21日；籍贯：陕西；民族：汉族；政治面貌：群众"),
            (("出生日期", "2006年3月21日"), ("籍贯", "陕西"), ("民族", "汉族"), ("政治面貌", "群众")),
        )

    def test_paragraph_endings_are_consistent_and_idempotent(self) -> None:
        for source in ("完成设备调试", "完成设备调试。", "完成设备调试；", "完成设备调试,", "完成设备调试."):
            self.assertEqual(paragraph_text(source), "完成设备调试。")
            self.assertEqual(paragraph_text(paragraph_text(source)), "完成设备调试。")
        self.assertEqual(paragraph_text(""), "")
        self.assertEqual(paragraph_text("是否完成？"), "是否完成？")

    def test_standard_information_becomes_unpunctuated_fields(self) -> None:
        self.assertEqual(
            personal_fields("男，2004年11月26日出生，汉族，籍贯陕西省渭南市。"),
            (("性别", "男"), ("出生日期", "2004年11月26日"), ("民族", "汉族"), ("籍贯", "陕西省渭南市")),
        )

    def test_narrative_or_partial_information_is_not_guessed(self) -> None:
        for summary in ("熟悉电气安装，愿意从事设备维护。", "男，汉族，陕西西安。", ""):
            self.assertEqual(personal_fields(summary), ())
