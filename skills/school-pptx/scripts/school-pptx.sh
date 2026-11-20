#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${SCHOOL_PPTX_PYTHON:-${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python}}"
PYTHON="${PYTHON:-python3}"
exec "$PYTHON" "$SCRIPT_DIR/school_pptx.py" "$@"
