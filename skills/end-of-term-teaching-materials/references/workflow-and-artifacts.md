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

- 先按 [score-reconciliation.md](score-reconciliation.md) 完成主 agent 和独立子 agent 双核算；原件清晰、两次完全一致的算术错误直接修正，修正清单仅在交付回复告知。只有仍不确定的值（如 `87?`）留待教师复核。
- Every unresolved uncertain value must have a matching `## 复核标记` row.
- 一次性汇总当前已知的缺失字段、不确定成绩及分析背景问题，按编号列出学生、任务或字段、当前值及疑点，供教师集中回复；不得将已知问题拆成逐条往返。收到回复后逐项编辑 Markdown 并清除对应标记；仅对新出现或仍未解决的问题集中追问。
- Hard delivery rule: `## 复核标记` must be exactly `无`.
- If `## 复核标记` is anything else, `validate` and `deliver` must fail.
- If unresolved items remain, keep working in Markdown. Do not generate final public files.

## Score and Template Rules

- 记分册考勤、作业、期末测试三类缺失时，按 [score-reconciliation.md](score-reconciliation.md) 自行反推补齐，保留已知分项及已确定最终总成绩。其他空分仍为空白；任务整列为空也须保留声明的列。
- Respect package flags.
- `成绩记分册` is one bundle covering the redesigned cover and score-book body.
- `交接班记录封面` requires both `handover_class_name` and `handover_teachers`; otherwise delivery must fail and the Markdown must be corrected.
- Support up to 8 process-assessment tasks. Markdown must expand columns through `任务8`; the fixed `成绩汇总表` PDF grid renders at most 8 task columns.
- `成绩记分册` shows every score row and uses the finalized Markdown `考勤`、`作业`、`期末` test columns as its source data. 反推值在整理阶段写入主表，实际计分方案优先；若某补列仅作展示或无独立考试，在任务 renderer 副本固定已确定公式，不能因补上测试列而自动改变分支。
- 默认 renderer 的 `平时分` 在 Markdown `期末` 有值时使用 `考勤 * 0.3 + 作业 * 0.4 + 期末测试 * 0.3`，否则使用 `考勤 * 0.5 + 作业 * 0.5`。这是默认实现，不覆盖用户确认的方案；前三类反推后须按实际公式核验，不能让空白隐式按0计算。
- `成绩汇总表` only shows students listed under `## 我带的学生`, uses `任务1..任务N`, and its `总评成绩` equals `期末分`, where `期末分` is the task-hours weighted average.
- Preserve fixed-template merged cells in the `成绩分析表`; `全班人数` and `缺考人数` labels each span the upper two statistic rows and remain centered above their values.

## 处理说明的边界

原始算术纠错清单、两次独立核算证据、反推依据保存在任务工作目录，最终交付回复必须告知纠正了哪些错误、哪些成绩列按最终总成绩反推。最终四件套不写这些说明；分析仅写教学与成绩分析，不加入数据修正经过。不增加报告文件。

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

## Source Notes and Course Analysis

按 `score-reconciliation.md` 自动完成可行反推补列并保留工作证据；无可行解时集中询问。四项分析仅讨论课程、考核、学习与改进，不加入数据处理经过。

Display numeric score cells and average scores with at most one decimal (no trailing `.0`). Calculate from the original precision and preserve raw Markdown values; display rounding must not alter weighted totals or verified target scores.

成绩记分册封面保持标题及字段顺序，各信息栏等宽弹性伸长；正文的专业/班级名称一行一个、框内左对齐。成绩记分册中的分数最终按四舍五入（half up）显示整数；汇总表及平均分最多一位小数。此为显示规则，原始值与计算精度不变。专业、班级标签放在名称框外；名称框内每行仅一个完整专业或班级，框内各行左对齐，不将两个名称混排或把单个名称折行。
