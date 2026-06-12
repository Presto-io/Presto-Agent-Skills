#!/usr/bin/env python3
"""Stable CLI shim for the end-of-term teaching-materials renderer."""

from __future__ import annotations

import sys

from end_of_term.cli import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
