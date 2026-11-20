#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${SCHOOL_PPTX_PYTHON:-${VIRTUAL_ENV:+$VIRTUAL_ENV/bin/python}}"
RUNTIME="${XDG_CACHE_HOME:-$HOME/.cache}/presto/school-pptx/runtime/bin/python"
if [[ -z "$PYTHON" && -x "$RUNTIME" ]]; then
  PYTHON="$RUNTIME"
fi
PYTHON="${PYTHON:-python3}"
exec "$PYTHON" "$SCRIPT_DIR/school_pptx.py" "$@"
