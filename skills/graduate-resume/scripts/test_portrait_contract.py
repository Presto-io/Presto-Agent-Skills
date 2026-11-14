"""Synthetic portrait processing and whitespace audit regressions."""
from pathlib import Path
import os
import subprocess
import tempfile
import unittest

from PIL import Image, ImageDraw
from graduate_resume_portrait import compose_background, prepare_portrait
from graduate_resume_styles import STYLE_ROOT
from graduate_resume_visual_audit import audit_pdf


class PortraitContractTests(unittest.TestCase):
    def test_edge_connected_cutout_keeps_subject_and_all_compositions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / 'synthetic.png'
            image = Image.new('RGB', (200, 260), 'white')
            draw = ImageDraw.Draw(image)
            draw.ellipse((60, 20, 140, 110), fill='#9D7156')
            draw.rectangle((35, 110, 165, 259), fill='#213A50')
            image.save(source)
            cutout, screen, paper = prepare_portrait(source)
            self.assertEqual(cutout.getpixel((0, 0))[3], 0)
            self.assertEqual(cutout.getpixel((100, 65))[3], 255)
            self.assertEqual(screen.size, cutout.size)
            self.assertEqual(paper.mode, 'RGBA')
            for background in (STYLE_ROOT / 'reference/backgrounds').glob('*-plain.png'):
                style = background.name.removesuffix('-plain.png')
                output = root / (style + '.png')
                compose_background(style, source, background, output)
                with Image.open(output) as composed:
                    self.assertEqual(composed.size, (1680, 2376))
                    self.assertNotEqual(composed.tobytes(), Image.open(background).convert('RGB').tobytes())

    def test_unsupported_background_fails_instead_of_rectangular_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / 'synthetic.png'
            Image.new('RGB', (200, 260), '#1759B0').save(source)
            with self.assertRaisesRegex(ValueError, 'PORTRAIT_CUTOUT_REQUIRED'):
                prepare_portrait(source)

    def test_audit_distinguishes_sparse_and_full_text_pages(self):
        typst = os.environ.get('TYPST_BIN')
        if not typst:
            self.skipTest('Set TYPST_BIN')
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for name, text in [('sparse', 'A short resume.'),
                               ('full', '\n\n'.join('Verified training record and practical task details.' for _ in range(31)))]:
                source = root / (name + '.typ')
                source.write_text('#set page(paper: "a4", margin: 15mm)\n#set text(size: 12pt)\n' + text)
                output = source.with_suffix('.pdf')
                subprocess.run([typst, 'compile', str(source), str(output)], check=True)
                report = audit_pdf(output)
                self.assertEqual(report['fill_satisfied'], name == 'full', report)
