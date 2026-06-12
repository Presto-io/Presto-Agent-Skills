from __future__ import annotations

import sys

from . import _engine

RenderError = _engine.RenderError


def main(argv: list[str] | None = None) -> int:
    return _engine.main(sys.argv[1:] if argv is None else argv)


if __name__ == "__main__":
    raise SystemExit(main())
