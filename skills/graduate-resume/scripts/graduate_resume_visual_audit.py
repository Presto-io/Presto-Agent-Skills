"""Assess text density rather than treating successful compilation as fullness."""
from pathlib import Path
import re
import subprocess
import xml.etree.ElementTree as ET


def audit_pdf(path: Path) -> dict:
    result = subprocess.run(['pdftotext', '-bbox', str(path), '-'], capture_output=True, check=True)
    tree = ET.fromstring(result.stdout)
    reports = []
    for index, page in enumerate(tree.findall('.//{*}page'), 1):
        words = page.findall('.//{*}word')
        height = float(page.get('height'))
        chars = sum(len(re.sub(r'\s', '', ''.join(w.itertext()))) for w in words)
        top = min((float(w.get('yMin')) for w in words), default=height)
        bottom = max((float(w.get('yMax')) for w in words), default=0)
        rows = set()
        for word in words:
            y0, y1 = float(word.get('yMin')), float(word.get('yMax'))
            rows.update(range(int(y0 / 8.5), int(y1 / 8.5) + 1))
        span = max(0, bottom - top) / height
        occupied = len(rows) / (height / 8.5)
        reasons = []
        if chars < 300: reasons.append('too_little_verified_content')
        if span < .78: reasons.append('short_vertical_span')
        if occupied < .30: reasons.append('large_internal_whitespace')
        reports.append(dict(page=index, characters=chars, text_span=round(span, 3),
                            occupied_rows=round(occupied, 3), reasons=reasons, fill_satisfied=not reasons))
    return dict(pages=reports, fill_satisfied=bool(reports) and all(p['fill_satisfied'] for p in reports))
