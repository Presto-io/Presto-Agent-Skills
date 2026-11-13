#!/usr/bin/env python3
"""Read-only structural checks; does not assess image pixels or visual template fidelity."""
import argparse
import json
import re
import sys
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
WP = '{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}'
CITATION = re.compile(r'\[\s*\d+(?:\s*[,，、—–-]\s*\d+)*\s*\]|【\s*\d+(?:\s*[,，、—–-]\s*\d+)*\s*】')


def audit(path, expected=None):
    with zipfile.ZipFile(path) as package:
        raw = package.read('word/document.xml')
        if b'<!DOCTYPE' in raw or b'<!ENTITY' in raw:
            raise ValueError('Unsupported XML declarations')
        root = ET.fromstring(raw)
    errors = []
    paragraphs = root.findall('.//' + W + 'p')
    for i, p in enumerate(paragraphs, 1):
        text = ''.join(t.text or '' for t in p.iter(W + 't'))
        if CITATION.search(text):
            errors.append(f'paragraph {i}: numeric citation marker')
    tables = root.findall('.//' + W + 'tbl')
    for ti, table in enumerate(tables, 1):
        # Descendant paragraphs include any nested table: each must be centered.
        for ci, cell in enumerate(table.findall('./' + W + 'tr/' + W + 'tc'), 1):
            align = cell.find('./' + W + 'tcPr/' + W + 'vAlign')
            if align is None or align.get(W + 'val') != 'center':
                errors.append(f'table {ti}, cell {ci}: vertical center not explicit')
            for p in cell.findall('.//' + W + 'p'):
                jc = p.find('./' + W + 'pPr/' + W + 'jc')
                if jc is None or jc.get(W + 'val') != 'center':
                    errors.append(f'table {ti}, cell {ci}: horizontal center not explicit')
                    break
    count = len(root.findall('.//' + WP + 'inline')) + len(root.findall('.//' + WP + 'anchor'))
    if expected is not None and count != expected:
        errors.append(f'expected {expected} drawing(s), found {count}')
    return {'passed': not errors, 'paragraphs': len(paragraphs), 'tables': len(tables),
            'drawings': count, 'errors': errors,
            'visual_checks_required': ['template fidelity', 'SC font glyphs', 'readable figure text',
                                       'no in-image titles or small notes', 'no training-room collage',
                                       'captions and page breaks']}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('docx', type=Path)
    parser.add_argument('--expected-figures', type=int)
    args = parser.parse_args()
    try:
        result = audit(args.docx, args.expected_figures)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(json.dumps({'passed': False, 'error': str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['passed'] else 1


if __name__ == '__main__':
    sys.exit(main())
