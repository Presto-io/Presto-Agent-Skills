#!/usr/bin/env python3
"""Render an optional single-page visual sample from validated final Markdown."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

from graduate_resume_final_markdown import load_final_resume
from graduate_resume_cli import CliError

SKILL_ROOT = Path(__file__).resolve().parent.parent
STYLE_ROOT = SKILL_ROOT / 'templates' / 'visual-styles'


def command(args: list[str]) -> bytes:
    result = subprocess.run(args, capture_output=True)
    if result.returncode:
        raise ValueError('STYLE_RENDER_FAILED: ' + result.stderr.decode(errors='replace')[:1500])
    return result.stdout


def validate_pdf(path, data, page_counts=(1,)):
    import re
    import xml.etree.ElementTree as ET
    root = ET.fromstring(command(['pdftotext', '-bbox', str(path), '-']))
    pages = root.findall('.//{*}page')
    if len(pages) not in page_counts or any(abs(float(p.get('width')) - 595.28) > 1 or abs(float(p.get('height')) - 841.89) > 1 for p in pages):
        raise ValueError('STYLE_PAGE_INVALID')
    words = root.findall('.//{*}word')
    margin = 12 * 72 / 25.4
    if any(float(word.get('xMin')) < margin or float(word.get('yMin')) < margin or float(word.get('xMax')) > 595.28-margin or float(word.get('yMax')) > 841.89-margin for word in words):
        raise ValueError('STYLE_BOUNDARY_INVALID')
    import unicodedata
    def normalize(value):
        return ''.join(c for c in value if not c.isspace() and unicodedata.category(c)[0] not in 'PZ')
    def strings(value):
        if isinstance(value, str):
            yield value
        elif isinstance(value, (list, tuple)):
            for item in value:
                yield from strings(item)
        elif isinstance(value, dict):
            for key, item in value.items():
                if key not in {'id', 'status'}:
                    yield from strings(item)
    actual = normalize(command(['pdftotext', '-raw', str(path), '-']).decode())
    expected = [*strings(data['profile'])]
    for section in data['sections']:
        expected.extend(strings(section['value']))
    missing = [value for value in expected if normalize(value) not in actual]
    if missing:
        raise ValueError('STYLE_CONTENT_MISSING: ' + ', '.join(missing))
    for key in ('phone', 'email'):
        value = data['profile'].get('contact', {}).get(key)
        if value and actual.count(normalize(value)) != 1:
            raise ValueError('STYLE_CONTACT_DUPLICATED')
    fonts_report = command(['pdffonts', str(path)]).decode().splitlines()[2:]
    if not fonts_report or any(not re.search(r'\byes\s+yes\s+yes\s+\d+\s+\d+\s*$', row) for row in fonts_report):
        raise ValueError('STYLE_FONT_INVALID')


def render(input_path: Path, style: str, output: Path, *, typst: str = 'typst',
           font_paths: tuple[Path, ...] = (), photo: Path | None = None,
           number_lift_pt: float = 0, allow_sparse_preview: bool = False) -> dict:
    catalog = {row['id']: row for row in json.loads((STYLE_ROOT / 'catalog.json').read_text())}
    if style not in catalog:
        raise ValueError('STYLE_UNKNOWN')
    if style in {'conservative', 'modern', 'expressive'}:
        raise ValueError('STYLE_CANONICAL_WORKFLOW: use graduate-resume.sh render --generic or --target')
    if not 0 <= number_lift_pt <= 1:
        raise ValueError('STYLE_NUMBER_LIFT_INVALID: expected 0..1 pt')
    document = load_final_resume(input_path)
    if document.page_count != 1:
        raise ValueError('STYLE_SINGLE_PAGE_REQUIRED')
    if (document.photo_mode == 'photo') != (photo is not None):
        raise ValueError('STYLE_PHOTO_REQUIRED: photo-mode input requires an explicit local --photo')
    data = {'profile': document.facts[0].as_dict(), 'sections': [
        {'kind': fact.section, 'value': fact.as_dict()} for fact in document.facts[1:]
    ], 'photo': '/photo.png' if photo is not None else None}
    data['profile'].setdefault('contact', {})
    from graduate_resume_style_policy import body_characters
    visible_body_count = body_characters(data['sections'])
    for section in data['sections']:
        if section['kind'] == 'certificates':
            value = section['value']
            details = [value[key] for key in ('issuer', 'issued_on', 'expires_on', 'note') if value.get(key)]
            value['note'] = '；'.join(details)
    output = output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    if output.exists():
        raise ValueError('STYLE_OUTPUT_EXISTS: choose a new output path')
    if not command([typst, '--version']).decode().startswith('typst 0.15.1 '):
        raise ValueError('TYPST_RUNTIME_INVALID: Typst 0.15.1 required')
    with tempfile.TemporaryDirectory(prefix='resume-style-') as temp:
        work = Path(temp)
        shutil.copytree(STYLE_ROOT, work / 'templates' / 'visual-styles')
        shutil.copytree(SKILL_ROOT / 'assets' / 'icons', work / 'assets' / 'icons')
        if photo is not None:
            from PIL import Image, ImageOps
            with Image.open(photo) as image:
                ImageOps.exif_transpose(image).convert('RGBA').save(work / 'photo.png')
            plain = STYLE_ROOT / 'reference' / 'backgrounds' / (style + '-plain.png')
            if plain.exists():
                from graduate_resume_portrait import compose_background
                compose_background(style, photo, plain, work / 'reference-photo.png')
                data['reference_background'] = '/reference-photo.png'
        (work / 'data.json').write_text(json.dumps(data, ensure_ascii=False))
        (work / 'main.typ').write_text(
            '#import "templates/visual-styles/layout.typ": resume\n'
            '#resume(json("data.json"), ' + json.dumps(style) + ')\n')
        fonts = ['--font-path', str(SKILL_ROOT / 'fonts'), '--ignore-system-fonts']
        for path in font_paths:
            fonts += ['--font-path', str(path.resolve())]
        options = ['--root', str(work), '--input', f'number-lift-pt={number_lift_pt}', *fonts]
        from graduate_resume_style_policy import audit_typst, body_characters, recommend_size
        from graduate_resume_visual_audit import audit_pdf
        policy = catalog[style]['content_policy']
        font = policy['font_pt']['default']
        attempts = []
        audit = None
        for attempt in range(2):
            attempt_options = [*options, '--input', f'body-font-pt={font}']
            try:
                command([typst, 'compile', str(work / 'main.typ'), str(work / 'result.pdf'), *attempt_options])
                validate_pdf(work / 'result.pdf', data)
                geometry = audit_typst(typst, work / 'main.typ', attempt_options, policy)
                audit = audit_pdf(work / 'result.pdf')
                passed = geometry['fill_satisfied'] and audit['fill_satisfied']
                attempts.append(dict(attempt=attempt + 1, font_pt=font,
                                     typst=geometry, pdf=audit, accepted=passed))
                overflow = any('body_region_overflow' in r['reasons'] for r in geometry['regions'])
            except ValueError as error:
                if not any(code in str(error) for code in ('LAYOUT_OVERFLOW', 'STYLE_PAGE_INVALID', 'STYLE_BOUNDARY_INVALID')):
                    raise
                overflow = True
                passed = False
                attempts.append(dict(attempt=attempt + 1, font_pt=font, accepted=False,
                                     error=str(error).split(':')[0]))
            if passed or (allow_sparse_preview and audit is not None):
                break
            if attempt == 0:
                font = recommend_size(policy, font, overflow=overflow)
        if audit is None or (not attempts[-1]['accepted'] and not allow_sparse_preview):
            raise ValueError('STYLE_CONTENT_TOO_SPARSE: STYLE_EXCLUDED_AFTER_ONE_ADJUSTMENT: '
                             + json.dumps(dict(style=style, attempts=attempts)))
        audit = dict(audit, typst=attempts[-1]['typst'], attempts=attempts,
                     body_characters=visible_body_count,
                     recommended_body_characters=policy['body_characters'],
                     font_adjustments=len(attempts) - 1,
                     fill_satisfied=attempts[-1]['accepted'])
        with output.open('xb') as target:
            target.write((work / 'result.pdf').read_bytes())
        return audit


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list', action='store_true')
    parser.add_argument('--input', type=Path)
    parser.add_argument('--style')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--typst', default=os.environ.get('TYPST_BIN', 'typst'))
    parser.add_argument('--font-path', type=Path, action='append', default=[])
    parser.add_argument('--photo', type=Path)
    parser.add_argument('--number-lift-pt', type=float, default=0)
    parser.add_argument('--allow-sparse-preview', action='store_true', help='Preview only; does not qualify as a full-page delivery')
    args = parser.parse_args()
    if args.list:
        print((STYLE_ROOT / 'catalog.json').read_text())
        return
    if not all((args.input, args.style, args.output)):
        parser.error('--input, --style and --output are required')
    try:
        audit = render(args.input, args.style, args.output, typst=args.typst,
               font_paths=tuple(args.font_path), photo=args.photo,
               number_lift_pt=args.number_lift_pt, allow_sparse_preview=args.allow_sparse_preview)
    except (ValueError, OSError, CliError) as error:
        parser.exit(1, str(error) + '\n')
    print('STYLE_VERIFIED')
    print(json.dumps(audit, ensure_ascii=False))


if __name__ == '__main__':
    main()
