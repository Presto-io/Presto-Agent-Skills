"""Regression checks for the bounded retry and qualified-only publication contract."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from types import SimpleNamespace

import graduate_resume_cli as cli
from graduate_resume_final_markdown import emit_final_markdown
from graduate_resume_style_policy import body_characters, recommend_size
from graduate_resume_styles import SKILL_ROOT, STYLE_ROOT, render
from graduate_resume_targeting import LayoutFeedback, PageBudgetRequest, resolve_version_projection


class StyleSelectionTests(unittest.TestCase):
    def test_collection_excludes_failed_styles_and_canonical_without_aborting(self):
        from pypdf import PdfReader, PdfWriter
        from graduate_resume_style_collection import collect

        rows = [dict(id='conservative', engine='canonical', recommended=True),
                dict(id='good', engine='visual', recommended=True),
                dict(id='bad', engine='visual', recommended=True)]
        def produce(source, style, target, **options):
            if style == 'bad':
                raise ValueError('STYLE_EXCLUDED_AFTER_ONE_ADJUSTMENT')
            writer = PdfWriter()
            writer.add_blank_page(width=595.28, height=841.89)
            with target.open('xb') as stream:
                writer.write(stream)
            return dict(fill_satisfied=True)

        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / 'source.md'
            source.write_text('synthetic test')
            with patch('graduate_resume_style_collection.recommendations', return_value=dict(styles=rows)), patch(
                'graduate_resume_style_collection.load_final_resume', return_value=SimpleNamespace(theme_key='conservative')), patch(
                'graduate_resume_style_collection.canonical_audit', side_effect=ValueError('COLUMN_UNFILLED')), patch(
                'graduate_resume_style_collection.render', side_effect=produce):
                report = collect(source, root / 'result', canonical=[(source, root / 'plan.json')])
                self.assertEqual((report['accepted'], report['excluded']), (1, 2))
                self.assertEqual(len(PdfReader(root / 'result/qualified-styles.pdf').pages), 1)
                self.assertEqual([p.name for p in (root / 'result/individual').iterdir()], ['good.pdf'])
                self.assertIn('COLUMN_UNFILLED', report['styles'][0]['reason'])
                self.assertEqual(report['styles'][1]['sha256'], hashlib.sha256(
                    (root / 'result/individual/good.pdf').read_bytes()).hexdigest())
                rows[:] = rows[:1]
                empty = collect(source, root / 'empty', canonical=[(source, root / 'plan.json')])
                self.assertIsNone(empty['collection'])
                self.assertFalse((root / 'empty/qualified-styles.pdf').exists())

    def test_catalog_bounds_and_visible_character_count(self):
        catalog = json.loads((STYLE_ROOT / 'catalog.json').read_text())
        self.assertEqual(len(catalog), 44)
        for row in catalog:
            policy = row['content_policy']
            bounds = policy['font_pt']
            self.assertLessEqual(bounds['min'], bounds['default'])
            self.assertLessEqual(bounds['default'], bounds['max'])
            self.assertEqual(recommend_size(policy, bounds['max']), bounds['max'])
            self.assertEqual(recommend_size(policy, bounds['min'], overflow=True), bounds['min'])
        self.assertEqual(body_characters([dict(kind='skills', value=dict(
            id='ignored', status='verified', group='测试', items=['A B', '测量']))]), 6)

    def test_retry_budget_and_no_failed_publication(self):
        typst = os.environ.get('TYPST_BIN')
        if not typst:
            self.skipTest('Set TYPST_BIN')
        source = SKILL_ROOT / 'fixtures/visual-styles.md'
        document = cli.load_resume(str(source))
        projection = resolve_version_projection(document.data, None, PageBudgetRequest('auto'),
            lambda theme, selected, request: LayoutFeedback(theme, True, 1, ()))
        good = dict(fill_satisfied=True, regions=[])
        bad = dict(fill_satisfied=False, regions=[dict(reasons=['underfilled_body_region'])])
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            final = root / 'final.md'
            final.write_bytes(emit_final_markdown(document.data, projection,
                canonical_hash=hashlib.sha256(source.read_bytes()).hexdigest(),
                theme_key='conservative', page_count=1, photo_mode='no-photo'))
            for name, measurements, count, accepted in [
                ('first-pass', [good], 1, True),
                ('adjusted-pass', [bad, good], 2, True),
                ('excluded', [bad, bad], 2, False),
            ]:
                target = root / (name + '.pdf')
                with self.subTest(name=name), patch(
                    'graduate_resume_style_policy.audit_typst', side_effect=measurements) as query, patch(
                    'graduate_resume_visual_audit.audit_pdf', return_value=dict(fill_satisfied=True, pages=[])):
                    if accepted:
                        audit = render(final, 'mono-minimal', target, typst=typst)
                        self.assertEqual(audit['font_adjustments'], count - 1)
                        self.assertTrue(target.is_file())
                    else:
                        with self.assertRaisesRegex(ValueError, 'STYLE_EXCLUDED_AFTER_ONE_ADJUSTMENT'):
                            render(final, 'mono-minimal', target, typst=typst)
                        self.assertFalse(target.exists())
                    self.assertEqual(query.call_count, count)


if __name__ == '__main__':
    unittest.main()
