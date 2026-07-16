# End-of-Term Workflow and Artifact Reference

This reference holds detailed workflow, delivery, scoring, and verification rules for the `end-of-term-teaching-materials` skill. Keep `SKILL.md` as the concise semantic entry point and update this file when long operational behavior changes.

## Fixed Workflow

The teacher-facing workflow is:

```text
source materials -> repeated human/agent Markdown revision -> Typst/PDF + one score-list workbook
```

Do not skip the persistent Markdown review point and export PDF/XLSX directly from raw data. JSON, CSV, manifests, fixture runs, and diagnostic sidecars are not successful public delivery artifacts.

## Markdown Review Sections

Generated or updated `end-of-term-full.md` is the only human-maintained fact base. It must keep `YAML frontmatter + body` and these reviewable sections:

- `## 我带的学生`
- `## 过程考核任务`
- `## 成绩数据`
- `## 分析`
- `## 复核标记`

## Analysis Drafting

When `成绩分析表` or score-analysis-book content is enabled, do not rely only on generic AI prose. Ask the teacher for brief context such as:

- 教学重点和难点
- 学生整体表现
- 缺考或异常情况
- 需要强调的问题
- 后续改进措施

Combine those answers with score distribution, pass rate, below-60 cases, blank cells, and task-score patterns computed from the Markdown to draft `## 分析`.

## Review and Delivery Gates

- Uncertain values such as `87?` may be generated into `## 成绩数据` for teacher review.
- Every unresolved uncertain value must have a matching `## 复核标记` row.
- Ask one item at a time, edit the Markdown value after teacher confirmation or correction, and remove the matching marker.
- Hard delivery rule: `## 复核标记` must be exactly `无`.
- If `## 复核标记` is anything else, `validate` and `deliver` must fail.
- If unresolved items remain, keep working in Markdown. Do not generate final public files.

## Score and Template Rules

- Preserve blank score cells and declared task columns. Empty scores remain empty; declared tasks remain columns even when all cells are blank.
- Respect package flags.
- `成绩记分册` is one bundle covering the redesigned cover and score-book body.
- `交接班记录封面` requires both `handover_class_name` and `handover_teachers`; otherwise delivery must fail and the Markdown must be corrected.
- Support up to 8 process-assessment tasks. Markdown must expand columns through `任务8`; the fixed `成绩汇总表` PDF grid renders at most 8 task columns.
- `成绩记分册` shows every score row and uses the Markdown `考勤`、`作业`、`期末` test columns as its source data.
- `平时分` uses `考勤 * 0.3 + 作业 * 0.4 + 期末测试 * 0.3` when the Markdown `期末` test column is present, otherwise `考勤 * 0.5 + 作业 * 0.5`.
- `成绩汇总表` only shows students listed under `## 我带的学生`, uses `任务1..任务N`, and its `总评成绩` equals `期末分`, where `期末分` is the task-hours weighted average.
- Preserve fixed-template merged cells in the `成绩分析表`; `全班人数` and `缺考人数` labels each span the upper two statistic rows and remain centered above their values.

## Public Delivery Outputs

- `end-of-term-full.md`: persistent Markdown fact base and public source copy.
- `end-of-term-package.typ`: generated Typst package using `templates/typst/end-of-term-package.typ`.
- `end-of-term-package.pdf`: PDF package when `typst compile` succeeds.
- `score-list.xlsx`: the only public Excel file. It contains exactly `学号`、`姓名`、`平时成绩`、`期末成绩`, sorted by ascending student ID. Values come from the Markdown-derived score-book calculations.

These four stable names are one indivisible current bundle. The delivery root may additionally contain only these optional support directories:

- `sources/`: user-requested retained originals; normal `deliver` never moves, rewrites, versions, or deletes them.
- `assets/`: persistent referenced resources. This skill currently declares no managed assets, so normal `deliver` does not populate or mutate it.
- `history/<sequence>/`: one complete prior four-file bundle per version; numbering uses the existing numeric maximum plus one and history is never automatically deleted, compressed, or renumbered.
- `.work/<run-id>/{candidate,rollback,evidence}`: owned transient generation, recovery, and bounded evidence. The current run and owned empty `.work` are removed on success or handled failure; unrelated stale work is preserved and causes fail-closed refusal.

Successful public delivery roots must not contain `manifest.json`, `tables/`, JSON, CSV, `score-list.md`, `scorebook.xlsx`, status/model/log/report sidecars, staging, debug output, failed output, or verification output.

## Candidate, History, and Rollback Contract

`deliver --input <markdown.md> --out-dir <dir>` keeps its published flags and exit semantics. It acquires an exclusive same-root lock, builds all four files inside the run candidate, and runs every content and format gate before current mutation. `validate` remains read-only.

- First publish installs the exact four-file bundle and creates no history.
- An exact relative-name and byte-identical candidate is a no-op: current inode/mtime and history remain unchanged.
- A changed candidate snapshots and verifies the complete old bundle, writes that single bundle to the next `history/<sequence>/`, then replaces the four stable current names.
- Unknown root entries, partial current sets, symlinks, legacy hidden directories, malformed history, concurrent locks, traversal, and stale unrelated `.work` fail before current/history mutation. Normal delivery never migrates or deletes them.
- A handled exception, standard fault injection, `INT`, or `TERM` restores the prior four files, removes only paths owned by this run and its uncommitted history sequence, and exits non-zero. This is a sequence of single-path replaces, not a claim of cross-file atomicity; SIGKILL, power loss, kernel/filesystem failure, and automatic hard-crash recovery are outside the guarantee.

## Minimal Format Gates

| Candidate | Automated minimum before publication | Human boundary |
|-----------|--------------------------------------|----------------|
| `end-of-term-full.md` | regular, non-symlink, non-empty UTF-8; required metadata/sections, score consistency, and `## 复核标记` exactly `无` | Teacher confirms facts, scores, analysis, and submission readiness. |
| `end-of-term-package.typ` | regular, non-symlink, non-empty UTF-8 generated from the reviewed Markdown and fixed template | Reviewer checks template fidelity when requirements change. |
| `end-of-term-package.pdf` | successful candidate Typst compile, non-empty readable bytes beginning with `%PDF-` | Reviewer opens the PDF and checks pagination, fonts, grids, and print appearance. |
| `score-list.xlsx` | readable ZIP with required OOXML members, exactly four ordered columns, every data row four cells, ascending student ID | Reviewer opens the workbook and confirms practical spreadsheet appearance and data. |

PDF rendering uses the fixed Excel-style grid for the score book body, score summary, and analysis sheet: column proportions, row rhythm, thin borders, merged headers, merged statistic cells, and diagonal header cells are encoded in the skill-local renderer.

## Verification Detail

- `bash -n skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`
- `python3 -m py_compile skills/end-of-term-teaching-materials/scripts/render_package.py`
- `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh deliver --input <finalized-markdown> --out-dir <delivery-dir>`
- Successful delivery root contains exactly the public delivery outputs listed above.
- First/changed/identical and every handled fault are exercised through the public CLI; current/history hashes remain unchanged on failure and `.work` is cleaned only when owned.
- `score-list.xlsx` has exactly four columns in this order: `学号`、`姓名`、`平时成绩`、`期末成绩`.
- Score-list rows are sorted by ascending student ID.
- Uncertain Markdown values such as `87?` and non-empty `## 复核标记` block `deliver`.
