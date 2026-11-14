"""Keep real candidate artifacts out of the distributable skill folder."""

from pathlib import Path
import unittest

from PIL import Image


SKILL_ROOT = Path(__file__).resolve().parent.parent


class PublicationContractTests(unittest.TestCase):
    def test_typst_templates_stay_in_allowed_directories(self) -> None:
        templates = sorted(str(path.relative_to(SKILL_ROOT)) for path in SKILL_ROOT.rglob("*.typ"))
        self.assertIn("templates/resume-themes.typ", templates)
        self.assertTrue(all(path == "templates/resume-themes.typ" or path.startswith("templates/visual-styles/") for path in templates))
        self.assertFalse((SKILL_ROOT / "templates/themes").exists())

    def test_photo_fixtures_are_non_identifying_pixels(self) -> None:
        photos = sorted(
            path for path in SKILL_ROOT.rglob("*")
            if path.is_file() and path.suffix.lower() in {".jpg", ".jpeg", ".png"}
        )
        self.assertEqual(
            [str(path.relative_to(SKILL_ROOT)) for path in photos],
            sorted(["fixtures/layout/media/student-photo.jpg", "fixtures/render/media/source-photo.jpg"] + [
                "templates/visual-styles/reference/backgrounds/" + name + "-plain.png"
                for name in ("blue-poster", "serif-blue", "purple-doodle", "purple-sidebar",
                             "rust-editorial", "blue-business", "blue-floral", "beige-notebook")]),
        )
        for path in photos:
            if path.parent == SKILL_ROOT / "templates/visual-styles/reference/backgrounds":
                with Image.open(path) as artwork:
                    self.assertEqual(artwork.size, (1680, 2376))
                    self.assertFalse(artwork.getexif())
                continue
            with self.subTest(path=path.relative_to(SKILL_ROOT)), Image.open(path) as image:
                self.assertEqual(image.size, (1, 1))
                self.assertEqual(len(image.getcolors()), 1)
                self.assertFalse(image.getexif())

    def test_generated_deliverables_are_not_packaged(self) -> None:
        forbidden = {".pdf", ".doc", ".docx", ".pptx", ".xlsx"}
        artifacts = [str(path.relative_to(SKILL_ROOT)) for path in SKILL_ROOT.rglob("*") if path.is_file() and path.suffix.lower() in forbidden]
        self.assertEqual(artifacts, [])
