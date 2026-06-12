---
phase: 18
status: completed
generated_at: 2026-06-13
---

# Phase 18 Pattern Map

## Purpose

This map records the current code shapes Phase 18 should preserve while decomposing large script entry points. It is a planning aid only; it does not authorize behavior changes.

## Public Wrapper Pattern

### Existing Analog

- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`

### Pattern

- Keep a small shell file as the public command surface.
- Parse common flags in Bash when that is already the user-facing behavior.
- Delegate implementation to a skill-local helper while preserving the command name, default paths, status output, and error prefix.

### Use In Phase 18

- Apply this pattern to `skills/school-presentation/scripts/school-presentation.sh` by turning it into a thin wrapper over a skill-local Python package.
- Keep the existing end-of-term wrapper pattern stable and deepen only the Python helper decomposition behind it.
- Do not apply a Python delegation pattern to `gongwen.sh`; its Bash-only behavior is part of the skill contract.

## Python Package Extraction Pattern

### Existing Analog

- `skills/end-of-term-teaching-materials/scripts/render_package.py`

### Current Shape

- One Python file contains CLI dispatch, data validation, Markdown generation and parsing, Typst layout generation, workbook writing, PDF compile, and verification.
- Functions already form extractable clusters, making it suitable for a package split with a thin CLI shim.

### Use In Phase 18

- For `render_package.py`, create `scripts/end_of_term/` modules and keep `render_package.py` as the stable executable shim.
- For `school-presentation.sh`, move the embedded Python heredoc into `scripts/school_presentation/` modules and call it through the wrapper.

## Bash-Only Renderer Pattern

### Existing Analog

- `skills/gongwen/scripts/gongwen.sh`

### Current Shape

- Bash functions cover common helpers, Markdown/frontmatter parsing, Typst emission, image/table rendering, signature placement, command handlers, and dispatch.
- The reference explicitly says rendering must not depend on an external template binary, Pandoc, Python, Node, or another Markdown converter.

### Use In Phase 18

- Extract sourced Bash files under `skills/gongwen/scripts/gongwen_lib/`.
- Keep `gongwen.sh` as the only public executable command.
- Use `source` with `SCRIPT_DIR`-relative paths.

## Contract Verification Pattern

### Existing Analog

- `skills/school-presentation/references/verification-contract.md`
- `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md`
- `skills/gongwen/references/format-and-rendering.md`

### Use In Phase 18

- Treat these references as source-of-truth files for manifest keys, artifact names, Markdown intermediates, and public command behavior.
- Verify behavior through public shell commands first.
- Private module tests may supplement but cannot replace public command checks.

## Anti-Patterns

- Do not split files by arbitrary line-count chunks.
- Do not rename public commands or common flags.
- Do not add runtime-specific syntax for Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, or Hermes Agent to canonical skill bodies or script interfaces.
- Do not create a broad global script framework unless exact duplicated behavior and a stable contract are proven during implementation.
