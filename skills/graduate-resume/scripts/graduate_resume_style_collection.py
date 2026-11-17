"""Recommend styles, render each at most twice, and merge qualified PDFs only."""
import argparse
import json
import os
from pathlib import Path
import shutil
import hashlib

from graduate_resume_final_markdown import load_final_resume
from graduate_resume_style_policy import body_characters
from graduate_resume_styles import STYLE_ROOT, render, validate_pdf
from graduate_resume_visual_audit import audit_pdf


def recommendations(source):
    document = load_final_resume(source)
    sections = [{'kind': fact.section, 'value': fact.as_dict()} for fact in document.facts[1:]]
    count = body_characters(sections)
    rows = json.loads((STYLE_ROOT / 'catalog.json').read_text())
    return dict(body_characters=count, styles=[dict(
        id=row['id'], engine=row['engine'], policy=row['content_policy'],
        recommended=row['content_policy']['body_characters']['min'] <= count
        <= row['content_policy']['body_characters']['max'] * document.page_count)
        for row in rows])


def canonical_audit(final, plan_path, source):
    """Admit an existing canonical delivery only with its frozen column plan."""
    document = load_final_resume(final)
    origin = load_final_resume(source)
    if document.canonical_hash != origin.canonical_hash or document.facts != origin.facts:
        raise ValueError('COLLECTION_CANONICAL_FACTS_MISMATCH')
    plan = json.loads(plan_path.read_text())['frozen_layout']
    if plan['theme']['key'] != document.theme_key or plan['page_count'] != document.page_count:
        raise ValueError('COLLECTION_CANONICAL_PLAN_MISMATCH')
    regions = []
    for page in plan['pages']:
        composition = page['composition']
        header = composition['natural_height_mm'] - max(composition['sidebar_height_mm'], composition['main_height_mm'])
        for column in ('sidebar', 'main'):
            natural = composition[column + '_height_mm']
            if not natural:
                continue
            gap = composition[column + '_gap_mm']
            if not composition['fill_satisfied'] or gap > 18:
                raise ValueError('COLLECTION_CANONICAL_COLUMN_UNFILLED')
            regions.append(dict(page=page['number'], column=column, natural_mm=natural,
                                header_mm=header, gap_mm=gap))
    pdf = final.with_suffix('.pdf')
    data = dict(profile=document.facts[0].as_dict(), sections=[dict(kind=f.section, value=f.as_dict()) for f in document.facts[1:]])
    validate_pdf(pdf, data, page_counts=(document.page_count,))
    audit = audit_pdf(pdf)
    if not audit['fill_satisfied'] or not regions:
        raise ValueError('COLLECTION_CANONICAL_DENSITY_FAILED')
    return document.theme_key, pdf, dict(audit, typst_frozen_regions=regions)


def collect(source, output, *, typst='typst', photo=None, font_paths=(), canonical=(), expected_count=None):
    from pypdf import PdfReader, PdfWriter
    if expected_count is not None and (isinstance(expected_count, bool) or not isinstance(expected_count, int) or expected_count < 1):
        raise ValueError("COLLECTION_EXPECTED_COUNT_INVALID")
    selection = recommendations(source)
    output.mkdir(parents=True, exist_ok=False)
    individual = output / 'individual'
    individual.mkdir()
    records = []
    writer = PdfWriter()
    canonical_results = {}
    for final, plan in canonical:
        key = load_final_resume(final).theme_key
        if key in canonical_results:
            raise ValueError('COLLECTION_DUPLICATE_CANONICAL_THEME')
        try:
            _, pdf, audit = canonical_audit(final, plan, source)
            canonical_results[key] = dict(pdf=pdf, audit=audit)
        except (ValueError, OSError, KeyError, TypeError) as error:
            canonical_results[key] = dict(reason='COLLECTION_CANONICAL_EXCLUDED: ' + str(error))
    for row in selection['styles']:
        record = dict(id=row['id'], accepted=False)
        if row['engine'] == 'canonical':
            if row['id'] in canonical_results:
                result = canonical_results[row['id']]
                if 'reason' in result:
                    record['reason'] = result['reason']
                else:
                    target = individual / (row['id'] + '.pdf')
                    shutil.copyfile(result['pdf'], target)
                    writer.append(PdfReader(target), outline_item=row['id'])
                    record.update(accepted=True, audit=result['audit'], file=str(target.resolve()))
            else:
                record['reason'] = 'canonical_requires_transactional_render_and_per_column_audit'
        elif not row['recommended']:
            record['reason'] = 'outside_recommended_body_range_after_content_preparation'
        else:
            target = individual / (row['id'] + '.pdf')
            try:
                audit = render(source, row['id'], target, typst=typst,
                               photo=photo, font_paths=font_paths)
                record.update(accepted=True, audit=audit, file=str(target.resolve()))
                writer.append(PdfReader(target), outline_item=row['id'])
            except ValueError as error:
                record['reason'] = str(error)
        records.append(record)
    accepted = [row for row in records if row['accepted']]
    if accepted:
        with (output / 'qualified-styles.pdf').open('xb') as stream:
            writer.write(stream)
    merged_pages = 0
    if accepted:
        merged = PdfReader(output / 'qualified-styles.pdf')
        merged_pages = len(merged.pages)
        expected_pages = sum(len(PdfReader(Path(row['file'])).pages) for row in accepted)
        if merged_pages != expected_pages:
            raise ValueError('COLLECTION_PAGE_COUNT_MISMATCH')
    for row in accepted:
        row['sha256'] = hashlib.sha256(Path(row['file']).read_bytes()).hexdigest()
    report = dict(source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  selection=selection, accepted=len(accepted), excluded=len(records) - len(accepted),
                  expected_count=expected_count, request_satisfied=(expected_count is None or len(accepted) == expected_count),
                  individual_pdf_count=len(accepted), collection_pages=merged_pages,
                  styles=records, collection='qualified-styles.pdf' if accepted else None)
    (output / 'selection-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--recommend', action='store_true')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--expected-count', type=int, help='Requested number of resume styles per person; mismatch exits nonzero')
    parser.add_argument('--photo', type=Path)
    parser.add_argument('--typst', default=os.environ.get('TYPST_BIN', 'typst'))
    parser.add_argument('--font-path', type=Path, action='append', default=[])
    parser.add_argument('--canonical', nargs=2, action='append', default=[], type=Path,
                        metavar=('FINAL_MD', 'PLAN_JSON'), help='Include a verified canonical PDF and frozen column plan; repeat for each theme')
    args = parser.parse_args()
    if args.recommend:
        print(json.dumps(recommendations(args.input), ensure_ascii=False, indent=2))
    elif args.output:
        report = collect(args.input, args.output, typst=args.typst,
                         photo=args.photo, font_paths=tuple(args.font_path), canonical=args.canonical, expected_count=args.expected_count)
        print(json.dumps({key: report[key] for key in ('accepted', 'excluded', 'expected_count',
                         'request_satisfied', 'individual_pdf_count', 'collection_pages')}, ensure_ascii=False))
        if not report['accepted'] or not report['request_satisfied']:
            raise SystemExit(2)
    else:
        parser.error('--recommend or --output is required')


if __name__ == '__main__':
    main()
