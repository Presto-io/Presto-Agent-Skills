"""Bounded style selection and Typst whitespace measurements."""
import json
import re
import subprocess


def body_characters(sections):
    def visible(value):
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return ''.join(visible(item) for item in value)
        if isinstance(value, dict):
            return ''.join(visible(item) for key, item in value.items()
                           if key not in {'id', 'status'})
        return ''
    return len(re.sub(r'\s', '', ''.join(visible(section['value']) for section in sections)))


def recommend_size(policy, current, *, overflow=False):
    bounds = policy['font_pt']
    factor = .9 if overflow else 1.12
    return round(max(bounds['min'], min(bounds['max'], current * factor)), 2)


def audit_typst(typst, source, options, policy=None):
    policy = policy or {}
    selector = 'metadata'
    result = subprocess.run([typst, 'query', str(source), selector, *options],
                            capture_output=True, text=True)
    if result.returncode:
        raise ValueError('STYLE_MEASUREMENT_FAILED: ' + result.stderr[:1000])
    reports = []
    for node in json.loads(result.stdout):
        value = node.get('value')
        if not isinstance(value, dict):
            continue
        available = value.get('available_mm')
        used = value.get('used_mm')
        if available is None or used is None:
            if 'natural_height_mm' in value and 'available_mm' in value:
                available, used = value['available_mm'], value['natural_height_mm']
            else:
                continue
        gap = value.get('gap_mm', 0) if value.get('groups', 2) > 1 else 0
        unused = max(0, available - used) / max(1, available)
        reasons = []
        if gap > policy.get('max_section_gap_mm', 18) + .01:
            reasons.append('excessive_section_gap')
        if unused > policy.get('max_unused_height_ratio', .22):
            reasons.append('underfilled_body_region')
        if used > available + .1:
            reasons.append('body_region_overflow')
        reports.append(dict(available_mm=available, used_mm=used,
                            gap_mm=gap, unused_ratio=round(unused, 3), reasons=reasons))
    if not reports:
        raise ValueError('STYLE_MEASUREMENT_MISSING: no measured body regions')
    return dict(method='typst.measure/query', regions=reports,
                fill_satisfied=all(not row['reasons'] for row in reports))
