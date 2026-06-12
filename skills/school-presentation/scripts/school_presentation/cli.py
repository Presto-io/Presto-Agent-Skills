from __future__ import annotations

import sys
from pathlib import Path

from . import _engine


def main(argv: list[str] | None = None) -> None:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        _engine.fail("missing skill directory")
    _engine.SKILL_DIR = Path(args[0]).resolve()
    _engine.TEMPLATE_MD = _engine.SKILL_DIR / "templates" / "school-presentation-full.md"
    _engine.IDENTITY_DIR = _engine.SKILL_DIR / "references" / "identity"
    _engine.IMAGE_DIR = _engine.IDENTITY_DIR / "images"
    _engine.main(args[1:])


if __name__ == "__main__":
    main()
