"""Exercise reusable style samples with synthetic facts and exclusive output creation."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

import graduate_resume_cli as cli
from graduate_resume_final_markdown import emit_final_markdown
from graduate_resume_targeting import LayoutFeedback, PageBudgetRequest, resolve_version_projection
from graduate_resume_styles import SKILL_ROOT, STYLE_ROOT, render


class VisualStyleTests(unittest.TestCase):
    def test_synthetic_styles_and_non_overwrite(self):
        typst = os.environ.get('TYPST_BIN')
        if not typst:
            self.skipTest('Set TYPST_BIN to Typst 0.15.0')
        fonts = tuple(Path(p) for p in os.environ.get('STYLE_TEST_FONT_PATHS', '').split(os.pathsep) if p)
        source = SKILL_ROOT / 'fixtures/visual-styles.md'
        document = cli.load_resume(str(source))
        cli.validate_document(document)
        projection = resolve_version_projection(document.data, None, PageBudgetRequest('auto'),
            lambda theme, selected, request: LayoutFeedback(theme, True, 1, ()))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            final = root / 'final.md'
            final.write_bytes(emit_final_markdown(document.data, projection,
                canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
                theme_key='conservative', page_count=1, photo_mode='no-photo'))
            catalog = json.loads((STYLE_ROOT / 'catalog.json').read_text())
            self.assertEqual(len(catalog), 44)
            self.assertEqual(len({row['id'] for row in catalog}), 44)
            for row in catalog:
                if row['engine'] == 'canonical':
                    continue
                with self.subTest(style=row['id']):
                    output = root / (row['id'] + '.pdf')
                    render(final, row['id'], output, typst=typst, font_paths=fonts)
                    original = output.read_bytes()
                    with self.assertRaisesRegex(ValueError, 'STYLE_OUTPUT_EXISTS'):
                        render(final, row['id'], output, typst=typst, font_paths=fonts)
                    self.assertEqual(output.read_bytes(), original)
            for style in ('bauhaus', 'network-topology'):
                render(final, style, root / (style + '-lift.pdf'), typst=typst,
                    font_paths=fonts, number_lift_pt=.55)
            photo_final = root / 'photo-final.md'
            photo_final.write_bytes(emit_final_markdown(document.data, projection,
                canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
                theme_key='conservative', page_count=1, photo_mode='photo'))
            for row in catalog:
                if row['engine'] == 'canonical':
                    continue
                with self.subTest(photo_style=row['id']):
                    render(photo_final, row['id'], root / (row['id'] + '-photo.pdf'),
                        typst=typst, font_paths=fonts,
                        photo=SKILL_ROOT / 'fixtures/render/media/source-photo.jpg')
            final.write_bytes(final.read_bytes().replace(b'graduate-resume-delivery/v1', b'invalid/v1'))
            with self.assertRaises(cli.CliError):
                render(final, 'bauhaus', root / 'tampered.pdf', typst=typst)
            self.assertFalse((root / 'tampered.pdf').exists())


if __name__ == '__main__':
    unittest.main()
