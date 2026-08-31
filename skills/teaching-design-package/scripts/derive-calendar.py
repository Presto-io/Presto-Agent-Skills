#!/usr/bin/env python3
"""Derive a reviewed teaching-day calendar from school-calendar exceptions."""

import argparse
import datetime as dt
import json
from pathlib import Path


def parse_date(value: str) -> dt.date:
    try:
        return dt.date.fromisoformat(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(f"invalid ISO date: {value}") from error


def parse_range(value: str) -> tuple[dt.date, dt.date]:
    try:
        start_text, end_text = value.split(":", 1)
    except ValueError as error:
        raise argparse.ArgumentTypeError("range must use START:END") from error
    start_date = parse_date(start_text)
    end_date = parse_date(end_text)
    if end_date < start_date:
        raise argparse.ArgumentTypeError("range end must not precede its start")
    return start_date, end_date


def dates_in_range(start_date: dt.date, end_date: dt.date) -> list[dt.date]:
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += dt.timedelta(days=1)
    return dates


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate reviewed teaching dates from a school calendar's normal weekdays and exceptions."
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--term-start", required=True, type=parse_date)
    parser.add_argument("--term-end", required=True, type=parse_date)
    parser.add_argument("--first-teaching-day", type=parse_date)
    parser.add_argument("--exclude-range", action="append", default=[], type=parse_range)
    parser.add_argument("--include-date", action="append", default=[], type=parse_date)
    parser.add_argument("--expected-count", type=int)
    arguments = parser.parse_args()

    if arguments.term_end < arguments.term_start:
        parser.error("--term-end must not precede --term-start")
    teaching_start = arguments.first_teaching_day or arguments.term_start
    if teaching_start < arguments.term_start or teaching_start > arguments.term_end:
        parser.error("--first-teaching-day must be inside the term range")

    excluded_dates = {
        date
        for start_date, end_date in arguments.exclude_range
        for date in dates_in_range(start_date, end_date)
    }
    teaching_dates = {
        date
        for date in dates_in_range(teaching_start, arguments.term_end)
        if date.weekday() < 5 and date not in excluded_dates
    }
    teaching_dates.update(arguments.include_date)
    teaching_dates = sorted(date for date in teaching_dates if teaching_start <= date <= arguments.term_end)

    if arguments.expected_count is not None and len(teaching_dates) != arguments.expected_count:
        parser.error(f"expected {arguments.expected_count} teaching dates, derived {len(teaching_dates)}")

    arguments.output.parent.mkdir(parents=True, exist_ok=True)
    arguments.output.write_text(
        json.dumps([date.isoformat() for date in teaching_dates], ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
