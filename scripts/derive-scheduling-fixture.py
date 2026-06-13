#!/usr/bin/env python3
"""Derive and verify Phase 22 scheduling fixture evidence."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Any


ROW_RE = re.compile(r"^(.+)-([0-9]+)$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def fail(message: str) -> None:
    print(f"derive-scheduling-fixture.py: {message}", file=sys.stderr)
    raise SystemExit(1)


def strip_quotes(value: str) -> str:
    value = value.strip()
    if (value.startswith('"') and value.endswith('"')) or (
        value.startswith("'") and value.endswith("'")
    ):
        return value[1:-1]
    return value


def parse_frontmatter_and_body(path: Path) -> tuple[dict[str, str], list[str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    meta: dict[str, str] = {}
    if not lines or lines[0].strip() != "---":
        fail("source is missing YAML frontmatter")
    try:
        end = next(i for i, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        fail("source frontmatter is not closed")

    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = strip_quotes(value)
    return meta, lines[end + 1 :]


def parse_positive_int(value: str, label: str) -> int:
    if not re.fullmatch(r"[0-9]+", value.strip()):
        fail(f"{label} must be a positive integer: {value}")
    parsed = int(value, 10)
    if parsed <= 0:
        fail(f"{label} must be greater than zero")
    return parsed


def parse_items(body: list[str]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    task_title = ""
    stage_title = ""
    task_index = 0
    stage_index = 0
    row_index = 0

    for raw_line in body:
        line = raw_line.strip()
        if not line:
            continue
        if line.startswith("## "):
            task_index += 1
            stage_index = 0
            row_index = 0
            task_title = line[3:].strip()
            if not task_title:
                fail("learning task title is empty")
            continue
        if line.startswith("### "):
            if task_index == 0:
                fail(f"stage appears before any task: {line}")
            stage_index += 1
            row_index = 0
            stage_title = line[4:].strip()
            if not stage_title:
                fail("learning stage title is empty")
            continue
        if task_index == 0:
            fail(f"content appears before any task: {line}")
        if stage_index == 0:
            fail(f"content appears before any stage: {line}")

        match = ROW_RE.match(line)
        if not match:
            fail(f"malformed row hours, expected text-N: {line}")
        title = match.group(1).strip()
        hours = parse_positive_int(match.group(2), "row hours")
        if not title:
            fail(f"empty content before hour suffix: {line}")
        row_index += 1
        items.append(
            {
                "source": f"task:{task_index}/stage:{stage_index}/row:{row_index}",
                "kind": "教学内容",
                "task_title": task_title,
                "stage_title": stage_title,
                "title": title,
                "hours": hours,
            }
        )

    if not items:
        fail("no schedulable items found")
    return items


def load_calendar(path: Path) -> list[str]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"calendar is not valid JSON: {exc}")
    if not isinstance(data, list):
        fail("calendar must be a JSON array of dates")
    dates: list[str] = []
    for item in data:
        if not isinstance(item, str) or not DATE_RE.match(item):
            fail(f"calendar entry is not a YYYY-MM-DD string: {item!r}")
        dates.append(item)
    if not dates:
        fail("calendar has no teaching dates")
    return dates


def iso_date(value: str) -> date:
    if not DATE_RE.match(value):
        fail(f"invalid date: {value}")
    try:
        return date.fromisoformat(value)
    except ValueError:
        fail(f"invalid date: {value}")


def term_week_start(calendar_dates: list[str]) -> date:
    first = iso_date(calendar_dates[0])
    return first - timedelta(days=first.isoweekday() - 1)


def weekday_for(value: str) -> int:
    return iso_date(value).isoweekday()


def term_week_for(value: str, start: date) -> int:
    return ((iso_date(value) - start).days // 7) + 1


def range_or_single(values: list[int]) -> int | str:
    unique: list[int] = []
    for value in values:
        if value not in unique:
            unique.append(value)
    if len(unique) == 1:
        return unique[0]
    return f"{unique[0]}-{unique[-1]}"


def derive(source: Path, calendar_path: Path) -> dict[str, Any]:
    meta, body = parse_frontmatter_and_body(source)
    first_teaching_day = meta.get("first_teaching_day", "").strip()
    if not first_teaching_day:
        fail("frontmatter first_teaching_day is required")
    daily_hours = parse_positive_int(meta.get("daily_hours", ""), "daily_hours")
    calendar_dates = load_calendar(calendar_path)
    if first_teaching_day not in calendar_dates:
        fail(f"first_teaching_day not found in calendar: {first_teaching_day}")

    start = term_week_start(calendar_dates)
    current_index = calendar_dates.index(first_teaching_day)
    remaining = daily_hours
    outputs: list[dict[str, Any]] = []

    for item in parse_items(body):
        hours_left = item["hours"]
        consumption: list[dict[str, Any]] = []
        while hours_left > 0:
            if current_index >= len(calendar_dates):
                fail("calendar ended before all hours were assigned")
            current_date = calendar_dates[current_index]
            take = min(hours_left, remaining)
            hours_left -= take
            remaining -= take
            consumption.append(
                {
                    "date": current_date,
                    "consumed_hours": take,
                    "remaining_daily_capacity": remaining,
                    "source": item["source"],
                }
            )
            if remaining == 0:
                current_index += 1
                remaining = daily_hours

        dates = [entry["date"] for entry in consumption]
        weeks = [term_week_for(value, start) for value in dates]
        weekdays = [weekday_for(value) for value in dates]
        output = {
            "source": item["source"],
            "kind": item["kind"],
            "task_title": item["task_title"],
            "stage_title": item["stage_title"],
            "title": item["title"],
            "assigned_hours": item["hours"],
            "start_date": dates[0],
            "end_date": dates[-1],
            "term_week": range_or_single(weeks),
            "weekday": range_or_single(weekdays),
            "hour_consumption": consumption,
            "review_markers": [],
        }
        outputs.append(output)

    return {
        "source": source.as_posix(),
        "calendar": calendar_path.as_posix(),
        "first_teaching_day": first_teaching_day,
        "daily_hours": daily_hours,
        "calendar_evidence": {
            "term_week_start": start.isoformat(),
            "holidays": [],
            "makeup_days": ["2026-05-09"] if "2026-05-09" in calendar_dates else [],
        },
        "items": outputs,
        "review_markers": [],
    }


def compare_expected(actual: dict[str, Any], expected_path: Path) -> None:
    try:
        expected = json.loads(expected_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"expected schedule is not valid JSON: {exc}")
    if actual != expected:
        print("Derived schedule does not match expected schedule.", file=sys.stderr)
        print(json.dumps(actual, ensure_ascii=False, indent=2), file=sys.stderr)
        raise SystemExit(1)


def write_output(actual: dict[str, Any], output_path: Path | None) -> None:
    text = json.dumps(actual, ensure_ascii=False, indent=2) + "\n"
    if output_path is None:
        print(text, end="")
    else:
        output_path.write_text(text, encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--calendar", required=True, type=Path)
    parser.add_argument("--expected", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    actual = derive(args.source, args.calendar)
    if args.expected:
        compare_expected(actual, args.expected)
    if args.output:
        write_output(actual, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

