"""Keep real candidate artifacts out of the distributable skill folder."""

from pathlib import Path
import unittest

from PIL import Image


SKILL_ROOT = Path(__file__).resolve().parent.parent


class PublicationContractTests(unittest.TestCase):
    def test_only_production_typst_template_is_packaged(self) -> None:
        templates = sorted(str(path.relative_to(SKILL_ROOT)) for path in SKILL_ROOT.rglob("*.typ"))
        self.assertEqual(templates, ["templates/resume-themes.typ"])

    def test_photo_fixtures_are_non_identifying_pixels(self) -> None:
        photos = sorted(
            path for path in SKILL_ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png"}
        )
        self.assertEqual(
            [str(path.relative_to(SKILL_ROOT)) for path in photos],
            ["fixtures/layout/media/student-photo.jpg", "fixtures/render/media/source-photo.jpg"],
        )
        for path in photos:
            with self.subTest(path=path.relative_to(SKILL_ROOT)), Image.open(path) as image:
                self.assertEqual(image.size, (1, 1))
                self.assertEqual(len(image.getcolors()), 1)
                self.assertFalse(image.getexif())

    def test_generated_deliverables_are_not_packaged(self) -> None:
        forbidden = {".pdf", ".doc", ".docx", ".pptx", ".xlsx"}
        artifacts = [str(path.relative_to(SKILL_ROOT)) for path in SKILL_ROOT.rglob("*") if path.is_file() and path.suffix.lower() in forbidden]
        self.assertEqual(artifacts, [])
