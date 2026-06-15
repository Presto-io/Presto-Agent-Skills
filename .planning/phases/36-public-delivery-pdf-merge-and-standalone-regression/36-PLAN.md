---
phase: 36
plan: 01
type: execute
wave: 1
depends_on:
  - phase: 35
files_modified:
  - skills/teaching-design-package/scripts/teaching-design-package.sh
  - skills/teaching-design-package/scripts/package-model.js
  - skills/teaching-design-package/SKILL.md
  - skills/teaching-design-package/references/format-and-orchestration.md
  - .planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-VERIFICATION.md
autonomous: true
requirements:
  - TDPKG-ART-01
  - TDPKG-ART-02
  - TDPKG-ART-03
  - TDPKG-PDF-01
  - TDPKG-PDF-02
  - TDPKG-PDF-03
  - TDPKG-PDF-04
requirements_addressed:
  - TDPKG-ART-01
  - TDPKG-ART-02
  - TDPKG-ART-03
  - TDPKG-PDF-01
  - TDPKG-PDF-02
  - TDPKG-PDF-03
  - TDPKG-PDF-04
must_haves:
  - "D-01: Successful public root is course-name-prefixed 1 + 1 + N; current N=2 gives exactly four files."
  - "D-02: Default fixture public files are 电气设备控制线路安装与调试教学资料.md, 电气设备控制线路安装与调试教学资料.pdf, 电气设备控制线路安装与调试授课进度计划表.pdf, and 电气设备控制线路安装与调试教学设计方案.pdf."
  - "D-03: Successful public root exposes no .typ, status, manifest, model, diagnostics, log, calendar JSON, hidden work artifacts, module Markdown, module Typst, or old English success filename surface."
  - "D-04: Public filenames derive from course_name through conservative sanitization; missing or invalid course_name fails non-zero with hidden diagnostics."
  - "D-05: Future N>2 module PDFs are published only through module registry metadata, not per-module ad hoc copy rules."
  - "D-06: Hidden .teaching-design-package evidence includes module Markdown, module Typst, model, status, diagnostics, debug logs, calendar path/hash, scheduling summary, module registry, module PDF status, merge status, merge tool, merge input order, input sizes, and failure evidence."
  - "D-07: status.json honestly records actual merge tool and result: pdfunite, qpdf, python_fitz, not_run, or a concrete failure category."
  - "D-08: final_ready true requires non-empty public Markdown, all registered module PDFs non-empty, real merged package PDF non-empty, hidden leakage check passed, and no review markers or validation errors."
  - "D-09: 课程名教学资料.pdf is created by merging registered module PDFs; directly compiled unified Typst/PDF cannot be reported as final merge success."
  - "D-10: Merge starts only after every registered module PDF exists, is non-empty, and has passed module status."
  - "D-11: Merge order comes only from module registry order: teaching-plan then teaching-design."
  - "D-12: Merge status records command/tool summary, input list, output path, exit code, and non-empty check."
  - "D-13: Module PDFs and merged PDF are generated in staging/hidden paths and verified before public publication."
  - "D-14: Failure cannot leave a complete-looking four-file public delivery set, including when old outputs already exist."
  - "D-15: Any module render, PDF compile, PDF check, filename derivation, merge, leakage, or standalone regression failure exits non-zero."
  - "D-16: Hidden failure diagnostics cover invalid course name, missing/empty module PDF, module status failure, merge order mismatch, merge tool unavailable, merge tool failed, empty merged PDF, public leakage, and standalone failure."
  - "D-17: Standalone regression copies only skills/teaching-design-package and proves no sibling jiaoan skill runtime dependency."
  - "D-18: Legacy jiaoan-jihua and jiaoan-shicao remain external compatibility surfaces and are not modified or invoked by package runtime."
  - "D-19: Future registry modules are not optional in final_ready; any registered module missing or empty PDF makes the merged package fail."
  - "D-20: Standalone-copy verification copies only skills/teaching-design-package into a clean temp dir and runs the copied scripts/teaching-design-package.sh."
  - "D-21: Standalone-copy verification proves copied skill-local calendar use, exact four-file public root, hidden evidence, and no sibling skill runtime dependency."
  - "D-22: Standalone or failure fixtures simulate missing module PDF, empty module PDF, or merge failure and prove non-zero plus no apparent public success."
  - "D-23: format-and-orchestration.md is updated from old English public filenames to the course-name-prefixed contract while preserving OpenClaw and Hermes notes."
  - "D-24: SKILL.md normal delivery instructions use teacher-readable course-name files, with runtime adapter notes limited to hidden diagnostics guidance."
  - "D-25: Legacy jiaoan-jihua and jiaoan-shicao are not modified, invoked, or introduced as package runtime dependencies."
---

# Phase 36 Plan: Public Delivery, PDF Merge, and Standalone Regression

<objective>
把 `teaching-design-package` 的最终交付面收口为课程名前缀 `1 + 1 + N`，当前 N=2：一个统一 Markdown、一个由注册模块 PDF 合并得到的整包 PDF、两个正式模块 PDF。成功公开目录只包含老师需要看到的四个课程名文件；所有 Typst、status、manifest、model、diagnostics、logs、calendar evidence、模块 Markdown/Typst 和 staging 产物都保留在隐藏 `.teaching-design-package/` 下。任何模块或合并失败都必须非零退出，并且不能留下看起来已经成功的公开四件套。
</objective>

<scope_boundary>
## Phase 36 Only

- 本阶段只实现 Phase 36 的公开交付、PDF merge、失败语义、hidden evidence 和 standalone-copy regression。
- 本阶段不得新增第三模块；当前 N=2，只发布 `授课进度计划表` 与 `教学设计方案` 两个注册模块 PDF。
- 本阶段不得改变 teacher-facing unified Markdown 结构，不得把新的派生字段加入教师维护 YAML。
- 本阶段不得重新迁移 `jiaoan-jihua` 或 `jiaoan-shicao` formal renderer；Phase 34/35 已完成。
- 本阶段不得修改旧 `skills/jiaoan-jihua/` 或 `skills/jiaoan-shicao/`，也不得把它们作为 runtime dependency。
- 本阶段不得公开 `.typ`、status、manifest、model、diagnostics、logs、calendar JSON、module Markdown、module Typst、staging files 或 old English success filenames。
- `课程名教学资料.pdf` 的成功语义必须来自 registered module PDFs 的真实 merge；不能用直接编译 unified Typst 伪装成整包 merge。
</scope_boundary>

<must_haves>
## Truths

- LT-01: 默认成功公开目录只包含 `电气设备控制线路安装与调试教学资料.md`、`电气设备控制线路安装与调试教学资料.pdf`、`电气设备控制线路安装与调试授课进度计划表.pdf`、`电气设备控制线路安装与调试教学设计方案.pdf`。
- LT-02: 成功公开目录不得包含 `teaching-design-package-full.md`、`teaching-design-package.typ`、`teaching-design-package.pdf`、`teaching-plan.pdf`、`teaching-design.pdf`、任何 `.typ`、`status.json`、`manifest.json`、`model.json`、`diagnostics.json`、`calendar.json`、`*.log`、模块 Markdown、模块 Typst 或 staging 文件。
- LT-03: 公开文件名必须从 `model.metadata.course_name` 派生，清理路径分隔符、控制字符、前后空白和明显不适合作为文件名的字符；缺失、清理后为空、包含路径穿越意图或无法形成安全文件名时必须 hard fail。
- LT-04: `package-model.js` 的 module registry 是模块顺序和模块 PDF public display name 的唯一来源；未来 N>2 时通过 registry 增加 `课程名<模块显示名>.pdf`。
- LT-05: 每个模块 PDF 必须先写入 staging/hidden path，通过存在性、非空、模块 status passed 检查后，才允许发布为课程名前缀 public module PDF。
- LT-06: `课程名教学资料.pdf` 必须先在 staging/hidden path 由 registry-ordered module PDFs 合并生成，通过非空检查后才发布到 public root。
- LT-07: merge input order 必须是 `teaching-plan` -> `teaching-design`，对应 `课程名授课进度计划表.pdf` -> `课程名教学设计方案.pdf`；不得使用 glob、mtime、文件名排序或另一套硬编码顺序。
- LT-08: merge 工具可 fallback，但 status 必须诚实记录实际值：`pdfunite`、`qpdf`、`python_fitz`、`not_run` 或具体失败类别。
- LT-09: hidden evidence 必须包含 module Markdown、module Typst、unified scheduling model、status、diagnostics、debug logs、calendar path/hash、scheduling summary、module registry、module PDF statuses、merge status、merge tool、merge input order、merge input sizes、merge output path、exit code 和 failure evidence。
- LT-10: `final_ready` 只有在公开 Markdown、所有 registered module PDFs、merged package PDF 均存在且非空，泄漏检查通过，review markers 和 validation errors 均为空时才可为 true。
- LT-11: 任一 module render、Typst compile、module PDF 非空检查、public filename derivation、merge tool selection、merge execution、merged PDF 非空检查、public leakage check 或 standalone regression 失败，命令必须非零退出。
- LT-12: 失败时允许保留 hidden diagnostics/failure evidence，但 public root 不能包含完整四件套，也不能包含 status、manifest、model、diagnostics、log、calendar JSON、Typst 或模块中间产物。
- LT-13: 如果 public root 已存在旧成功输出，本阶段必须先清理 expected public outputs 或使用 run-specific staging + atomic publish，确保失败不会混用旧文件形成伪成功。
- LT-14: negative verification 至少覆盖 missing module PDF、empty module PDF、merge failure、invalid course name、public leakage。
- LT-15: standalone-copy regression 必须只复制 `skills/teaching-design-package/` 到干净临时目录，并从 copied folder 运行 `scripts/teaching-design-package.sh`。
- LT-16: standalone-copy regression 必须证明 copied package 使用 skill-local `references/calendar.json`，公开目录只有课程名前缀四件套，隐藏目录包含 model/status/diagnostics/work/debug/failure evidence，status 不含 sibling skill runtime dependency。
- LT-17: normal runtime path 不得调用 `skills/jiaoan-jihua/scripts/jiaoan-jihua.sh`、`skills/jiaoan-shicao/scripts/jiaoan-shicao.sh`，不得读取 sibling calendars，旧 jiaoan skill folders 不得出现 git diff。
- LT-18: `SKILL.md` 和 `references/format-and-orchestration.md` 必须把默认交付说明更新为课程名前缀 `1 + 1 + N`，并保留 OpenClaw/Hermes Agent 的隐藏证据、脚本权限、sandbox/allowlist 和 fallback 提示。

## Context Decision Coverage Map

- D-01 至 D-05: 课程名前缀 `1 + 1 + N`、安全文件名、未来 registry 扩展。Covered by Tasks 1, 2, 6, and 7.
- D-06 至 D-09: hidden evidence、status honesty、final_ready、merged PDF 语义。Covered by Tasks 3, 4, 5, and 7.
- D-10 至 D-15: module PDF staging、registry-order merge、tool fallback、atomic publish、旧输出清理。Covered by Tasks 2, 3, 4, and 5.
- D-16 至 D-19: failure non-zero、failure diagnostics、future module missing PDF behavior。Covered by Tasks 3, 4, 5, and 7.
- D-20 至 D-22: standalone-copy regression 和负向 standalone/failure fixture。Covered by Task 6 and verification.
- D-23 至 D-25: reference/SKILL docs and old jiaoan non-dependency. Covered by Tasks 6, 7, and verification.
</must_haves>

<tasks>
## Task 1: Derive safe course-name public filenames and define the registry-backed delivery set

<read_first>
- `AGENTS.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `.planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-CONTEXT.md`
- `skills/teaching-design-package/scripts/package-model.js`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
</read_first>

<action>
Add a package-owned public delivery metadata path that derives filenames from `model.metadata.course_name`. The default template course name `电气设备控制线路安装与调试` must produce:

- public Markdown: `电气设备控制线路安装与调试教学资料.md`
- public merged package PDF: `电气设备控制线路安装与调试教学资料.pdf`
- public module PDF for registry id `teaching-plan`: `电气设备控制线路安装与调试授课进度计划表.pdf`
- public module PDF for registry id `teaching-design`: `电气设备控制线路安装与调试教学设计方案.pdf`

Implement conservative filename sanitization in package-owned code. It must reject missing `course_name`, all-whitespace names, names that become empty after sanitization, path separators `/` and `\`, NUL/control characters, path traversal-like `..`, and shell/OS-hostile filename characters chosen by the executor. The failure code must be stable, for example `invalid_course_name_for_filename`, and must write hidden diagnostics through the existing failure path.

Extend `MODULE_REGISTRY` or derived module metadata so every registered module exposes its display suffix for public PDFs. Current suffixes are exactly `授课进度计划表` and `教学设计方案`; future modules must be handled by registry iteration rather than new ad hoc copy blocks.
</action>

<acceptance_criteria>
- Running `scripts/teaching-design-package.sh model --input skills/teaching-design-package/templates/teaching-design-package-full.md` exposes or can derive the four expected public filenames above.
- `render-package --pdf` with the default template publishes the public Markdown as `电气设备控制线路安装与调试教学资料.md`, not `teaching-design-package-full.md`.
- `render-package --pdf` with the default template publishes module PDFs as `电气设备控制线路安装与调试授课进度计划表.pdf` and `电气设备控制线路安装与调试教学设计方案.pdf`, not `teaching-plan.pdf` or `teaching-design.pdf`.
- Fixtures with missing `course_name`, `course_name: ""`, `course_name: "../bad"`, `course_name: "bad/name"`, `course_name: "bad\\name"`, and a control character fail non-zero before public success publication.
- Each invalid-course-name failure writes hidden diagnostics containing `invalid_course_name_for_filename`, `source_markdown`, and the rejected or sanitized course-name evidence.
- Public PDF module targets are generated by iterating registry metadata; adding a fake temporary registry item in a local verification copy causes the planned public suffix path to include `课程名<display_name>.pdf` without adding a new hard-coded copy branch.
</acceptance_criteria>

## Task 2: Move all public publication behind staging and block public leakage

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/scripts/package-model.js`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-VERIFICATION.md`
- `.planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-CONTEXT.md`
</read_first>

<action>
Refactor `render-package` / `render-package --pdf` publication so successful public files are copied from a run-specific staging/hidden path only after validation passes. Use either a hidden staging directory such as `.teaching-design-package/staging/<run-id>/` or a deterministic hidden staging path that is cleaned before each run.

Before each run, prevent stale output from becoming apparent success. The executor may either remove only the expected four public filenames and old English success filenames at the start, or publish atomically from staging only after every final readiness check passes. The chosen strategy must guarantee that a failure cannot leave all four course-name public files present from a mix of old and new runs.

Harden `assert_no_public_leakage` so the public root rejects:

- any `.typ`;
- `status.json`, `manifest.json`, `model.json`, `diagnostics.json`, `calendar.json`;
- `*.log`;
- module Markdown and module Typst;
- files under names matching `teaching-design-package-full.md`, `teaching-design-package.typ`, `teaching-design-package.pdf`, `teaching-plan.pdf`, or `teaching-design.pdf` in a successful root;
- any hidden implementation artifacts accidentally copied to maxdepth 1 public root.
</action>

<acceptance_criteria>
- On successful default `render-package --pdf`, `find <out> -maxdepth 1 -type f | sort` prints exactly the four course-name public files and no other root-level files.
- On successful default `render-package --pdf`, `find <out> -maxdepth 1 -type f | rg '\\.typ$|status[.]json|manifest[.]json|model[.]json|diagnostics[.]json|calendar[.]json|[.]log$|teaching-design-package-full[.]md|teaching-design-package[.]typ|teaching-design-package[.]pdf|teaching-plan[.]pdf|teaching-design[.]pdf'` returns no matches.
- Hidden `.teaching-design-package/work/teaching-plan.md`, `.teaching-design-package/work/teaching-design.md`, `.teaching-design-package/work/teaching-plan.typ`, and `.teaching-design-package/work/teaching-design.typ` still exist after success.
- A forced leakage fixture that places `status.json`, `calendar.json`, `.typ`, or `teaching-plan.pdf` at public root causes the command or verification helper to fail with `public_root_leakage`.
- If the public root starts with stale old English output files, a successful run removes or ignores them so they are absent from the final public root.
- If the public root starts with stale four course-name files and the new run fails, verification proves the root does not contain a complete four-file success set for the failed run.
</acceptance_criteria>

## Task 3: Compile registered module PDFs to staging and merge only after all are real and non-empty

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/scripts/package-model.js`
- `skills/teaching-design-package/scripts/teaching-plan-renderer.js`
- `skills/teaching-design-package/scripts/teaching-design-renderer.js`
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-VERIFICATION.md`
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-VERIFICATION.md`
- `.planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-CONTEXT.md`
</read_first>

<action>
Make `render-package --pdf` compile every registered module PDF into staging/hidden paths first. For current registry order:

1. compile `.teaching-design-package/work/teaching-plan.typ` to a staging PDF for module id `teaching-plan`;
2. compile `.teaching-design-package/work/teaching-design.typ` to a staging PDF for module id `teaching-design`;
3. verify both staging PDFs exist and are non-empty;
4. verify module statuses are `passed`;
5. merge the staging PDFs in registry order into a staging merged package PDF;
6. verify the staging merged package PDF exists and is non-empty;
7. publish the two module PDFs and merged PDF to the course-name public targets.

Remove the old final success path that directly compiles `teaching-design-package.typ` into `teaching-design-package.pdf` as the public full package PDF. If a unified Typst/PDF remains useful for debugging, keep it under hidden `.teaching-design-package/` and label it as debug evidence; it must not appear in public root or drive `final_ready`.
</action>

<acceptance_criteria>
- Status records module PDF staging paths for `teaching-plan` and `teaching-design`, and both have `exists: true`, `nonempty: true`, byte sizes, hidden source Typst paths, and public target paths after success.
- `课程名教学资料.pdf` is generated only after both staging module PDFs pass existence and non-empty checks.
- `课程名教学资料.pdf` is non-empty and its status evidence points to the module PDF merge, not direct unified Typst compilation.
- The merge input array is ordered exactly by registry order: first module id `teaching-plan`, second module id `teaching-design`.
- A verification command can compare `status.json` merge input order with `model.modules.registry[].id` order and pass.
- Removing or failing the staged `teaching-plan` PDF before merge makes the command fail non-zero and skip merged package publication.
- Replacing the staged `teaching-design` PDF with an empty file before merge makes the command fail non-zero and skip merged package publication.
</acceptance_criteria>

## Task 4: Implement honest PDF merge tool selection and merge status evidence

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `.planning/phases/29-pdf-parity-and-standalone-regression/29-SUMMARY.md`
- `.planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-CONTEXT.md`
</read_first>

<action>
Add a package-owned merge helper inside `teaching-design-package.sh` or a skill-local script. The merge helper may choose tools by availability, with a concrete priority documented in code and reference docs. Acceptable tools are:

- `pdfunite`;
- `qpdf`;
- Python PyMuPDF fallback, recorded as `python_fitz`.

The helper must record actual tool, command/parameter summary, input list, output path, exit code, stdout/stderr log path or summary, byte sizes, and non-empty output check in hidden status/diagnostics. If no merge tool exists, record `merge_tool_unavailable` and fail non-zero. If a tool exits non-zero, record `merge_tool_failed` and fail non-zero. If the output is missing or empty, record `merged_pdf_empty` and fail non-zero.

For testability, add a narrow package-owned test hook or environment override that can simulate merge tool failure without depending on host package availability. The hook must not be advertised as normal user workflow and must not weaken production behavior.
</action>

<acceptance_criteria>
- Successful status contains `merge.status: "passed"` or equivalent, `merge_tool` equal to one of `pdfunite`, `qpdf`, or `python_fitz`, and `merge_inputs` with module ids, display names, staging paths, public paths, source Typst paths, byte sizes, and order values.
- Successful status contains merge output staging path, public output path, exit code `0`, and output byte size greater than `0`.
- If `pdfunite` is used, status says `merge_tool: "pdfunite"`; if `qpdf` is used, status says `merge_tool: "qpdf"`; if PyMuPDF fallback is used, status says `merge_tool: "python_fitz"`.
- A simulated no-tool or forced failure case exits non-zero and writes hidden diagnostics containing `merge_tool_unavailable` or `merge_tool_failed`.
- A simulated empty merged output exits non-zero and writes hidden diagnostics containing `merged_pdf_empty`.
- Public root does not contain `课程名教学资料.pdf` after merge failure.
- `status.json` never reports `final_ready: true` when `merge.status` is `not_run`, `failed`, `merge_tool_unavailable`, `merge_tool_failed`, or `merged_pdf_empty`.
</acceptance_criteria>

## Task 5: Make failure semantics atomic, non-zero, and auditable

<read_first>
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/scripts/package-model.js`
- `.planning/phases/33-module-registry-unified-extraction-and-scheduling-model/33-VERIFICATION.md`
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-VERIFICATION.md`
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-VERIFICATION.md`
- `.planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-CONTEXT.md`
</read_first>

<action>
Extend hidden failure diagnostics and final readiness logic for Phase 36. All failure paths must exit non-zero and preserve hidden evidence under `.teaching-design-package/diagnostics.json`, `.teaching-design-package/status.json`, `.teaching-design-package/debug/`, and `.teaching-design-package/failure-diagnostics/`.

Add stable failure classes for:

- `invalid_course_name_for_filename`;
- `module_pdf_missing`;
- `module_pdf_empty`;
- `module_status_failed`;
- `merge_input_order_mismatch`;
- `merge_tool_unavailable`;
- `merge_tool_failed`;
- `merged_pdf_empty`;
- `public_root_leakage`;
- `standalone_copy_failed`.

Every relevant diagnostic must include module id when applicable, source Markdown path, calendar path/hash when model exists, model version, expected value, actual value, public target path, staging path, and a concise message. Failure paths must not publish or leave a full four-file public success set.
</action>

<acceptance_criteria>
- Negative fixture `invalid_course_name_for_filename` exits non-zero and writes hidden diagnostics with source Markdown and rejected course-name evidence.
- Negative fixture `module_pdf_missing` exits non-zero before merge, records the missing module id and staging path, and public root lacks full four-file success set.
- Negative fixture `module_pdf_empty` exits non-zero before merge, records the module id and zero byte size, and public root lacks full four-file success set.
- Negative fixture `merge_tool_failed` exits non-zero, records tool and exit code, and public root lacks `课程名教学资料.pdf`.
- Negative fixture `public_root_leakage` exits non-zero or fails verification with hidden diagnostic evidence.
- `status.json` on any failure has `final_ready: false` and never claims all public outputs passed.
- Hidden `failure-diagnostics/` contains snapshots of diagnostics/status for each failure class tested in Phase 36 verification.
</acceptance_criteria>

## Task 6: Prove standalone-copy regression with only the teaching-design-package skill folder

<read_first>
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/scripts/teaching-design-package.sh`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `skills/teaching-design-package/references/calendar.json`
- `skills/teaching-design-package/templates/teaching-design-package-full.md`
- `.planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-CONTEXT.md`
</read_first>

<action>
Add Phase 36 standalone verification that copies only `skills/teaching-design-package/` into a clean temporary directory, then runs the copied `scripts/teaching-design-package.sh` from the copied folder. The standalone check must not rely on repo sibling `skills/jiaoan-jihua/`, `skills/jiaoan-shicao/`, repo-level `test/`, or absolute workspace paths.

The standalone success check must run:

- copied script `example` to create a package Markdown or copy the copied template directly;
- copied script `model` or `render-package --pdf`;
- copied script `render-package --pdf --input <copied-or-generated-md> --out-dir <standalone-out>`.

It must assert the copied package uses its own `references/calendar.json`, public root has exactly the four course-name public files, hidden evidence exists, and status/model/diagnostics contain no sibling skill runtime dependency.

Add at least one standalone negative path for missing/empty module PDF or forced merge failure, and prove non-zero plus no full public success set.
</action>

<acceptance_criteria>
- Standalone verification creates a temp directory containing `skills/teaching-design-package/` and no sibling `skills/jiaoan-jihua/` or `skills/jiaoan-shicao/`.
- Standalone `render-package --pdf` succeeds and public root contains exactly the four course-name public files for the default template.
- Standalone hidden `.teaching-design-package/model.json`, `status.json`, `diagnostics.json`, `work/`, `debug/`, and `failure-diagnostics/` exist or are accounted for after success/failure.
- Standalone model/status/diagnostics include the copied skill folder's `references/calendar.json` path and calendar hash.
- `rg 'skills/jiaoan-jihua|skills/jiaoan-shicao|jiaoan-jihua[.]sh|jiaoan-shicao[.]sh' <standalone evidence>` returns no runtime dependency matches.
- Standalone negative merge/module failure exits non-zero and public root does not contain the complete four-file public success set.
- `git diff --name-only -- skills/jiaoan-jihua skills/jiaoan-shicao` prints nothing after execution.
</acceptance_criteria>

## Task 7: Update docs and write Phase 36 verification evidence

<read_first>
- `skills/teaching-design-package/SKILL.md`
- `skills/teaching-design-package/references/format-and-orchestration.md`
- `.planning/REQUIREMENTS.md`
- `.planning/ROADMAP.md`
- `.planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-CONTEXT.md`
- `.planning/phases/34-teaching-plan-formal-renderer-migration/34-VERIFICATION.md`
- `.planning/phases/35-teaching-design-formal-renderer-and-cross-module-validation/35-VERIFICATION.md`
</read_first>

<action>
Update the canonical skill entry and package reference docs to describe Phase 36's course-name-prefixed `1 + 1 + N` public contract. Replace the default successful public output list in `SKILL.md` and `references/format-and-orchestration.md` with current N=2 filenames:

- `课程名教学资料.md`;
- `课程名教学资料.pdf`;
- `课程名授课进度计划表.pdf`;
- `课程名教学设计方案.pdf`.

Document that `.typ`, status, manifest, model, diagnostics, logs, calendar JSON, module Markdown, module Typst, staging files, and old English filenames are hidden/internal or no longer successful public outputs. Document merge semantics: all registered module PDFs must exist and be non-empty, merge order is registry order, actual merge tool is recorded, and any module/merge failure exits non-zero without apparent public success.

Keep the teacher workflow and runtime adapter notes portable. OpenClaw and Hermes Agent notes must mention copying the whole `teaching-design-package` skill folder, script permission/sandbox allowlist concerns, hidden diagnostics path, and merge tool fallback. Do not put Codex/Claude private syntax into the canonical workflow body.

Create `.planning/phases/36-public-delivery-pdf-merge-and-standalone-regression/36-VERIFICATION.md` with exact commands, observed results, public root listings, hidden evidence listings, status excerpts, merge tool evidence, standalone-copy result, negative fixture results, and legacy jiaoan non-modification proof.
</action>

<acceptance_criteria>
- `SKILL.md` no longer says the default successful public root contains `teaching-design-package-full.md`, `teaching-design-package.typ`, `teaching-design-package.pdf`, `teaching-plan.pdf`, or `teaching-design.pdf`.
- `references/format-and-orchestration.md` documents course-name-prefixed `1 + 1 + N`, current N=2, hidden `.typ`/status/model/diagnostics/log/calendar/module artifacts, and registry-order merge semantics.
- Runtime adapter notes still cover Codex, Claude Code, Gemini CLI, OpenCode, OpenClaw, and Hermes Agent.
- `36-VERIFICATION.md` records syntax checks: `bash -n`, `node --check` for all package JS helpers touched, and `typst --version` when PDF verification is run.
- `36-VERIFICATION.md` records a successful default run with exact public root listing of four course-name files and hidden evidence listing under `.teaching-design-package/`.
- `36-VERIFICATION.md` records status excerpts proving `final_ready: true`, registry-order merge inputs, actual merge tool, module PDF sizes, merged PDF size, calendar path/hash, and no sibling skill runtime dependency.
- `36-VERIFICATION.md` records negative results for missing module PDF, empty module PDF, merge failure, invalid course name, and public leakage.
- `36-VERIFICATION.md` records standalone-copy success and at least one standalone negative failure.
- `36-VERIFICATION.md` records `git diff --name-only -- skills/jiaoan-jihua skills/jiaoan-shicao` with no output.
</acceptance_criteria>
</tasks>

<verification>
## Required Verification Commands

The executor must record exact commands and observed output in `36-VERIFICATION.md`.

```bash
bash -n skills/teaching-design-package/scripts/teaching-design-package.sh
node --check skills/teaching-design-package/scripts/package-model.js
node --check skills/teaching-design-package/scripts/teaching-plan-renderer.js
node --check skills/teaching-design-package/scripts/teaching-design-renderer.js
typst --version
```

```bash
verify_root="$(mktemp -d)"
skills/teaching-design-package/scripts/teaching-design-package.sh example --output "$verify_root/package.md"
skills/teaching-design-package/scripts/teaching-design-package.sh render-package --pdf --input "$verify_root/package.md" --out-dir "$verify_root/out"
find "$verify_root/out" -maxdepth 1 -type f -print | sort
test -s "$verify_root/out/电气设备控制线路安装与调试教学资料.md"
test -s "$verify_root/out/电气设备控制线路安装与调试教学资料.pdf"
test -s "$verify_root/out/电气设备控制线路安装与调试授课进度计划表.pdf"
test -s "$verify_root/out/电气设备控制线路安装与调试教学设计方案.pdf"
! find "$verify_root/out" -maxdepth 1 -type f -print | rg '\\.typ$|status[.]json|manifest[.]json|model[.]json|diagnostics[.]json|calendar[.]json|[.]log$|teaching-design-package-full[.]md|teaching-design-package[.]typ|teaching-design-package[.]pdf|teaching-plan[.]pdf|teaching-design[.]pdf'
find "$verify_root/out/.teaching-design-package" -maxdepth 3 -type f -print | sort
```

```bash
node - "$verify_root/out/.teaching-design-package/status.json" <<'NODE'
const fs = require('fs');
const status = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
if (status.final_ready !== true) throw new Error('final_ready is not true');
const merge = status.merge || status.pdf_merge;
if (!merge) throw new Error('missing merge status');
const ids = (merge.inputs || merge.merge_inputs || []).map((item) => item.module_id || item.id);
if (ids.join(',') !== 'teaching-plan,teaching-design') throw new Error(`bad merge order: ${ids.join(',')}`);
if (!['pdfunite', 'qpdf', 'python_fitz'].includes(merge.merge_tool || merge.tool)) throw new Error('unexpected merge tool');
NODE
```

Required negative verification:

- invalid course name: missing/empty/path separator/path traversal/control character fails non-zero and writes `invalid_course_name_for_filename`.
- missing module PDF: forced missing staged module PDF fails non-zero and public root lacks full four-file set.
- empty module PDF: forced zero-byte staged module PDF fails non-zero and public root lacks full four-file set.
- merge failure: forced merge failure exits non-zero and does not publish `课程名教学资料.pdf`.
- public leakage: root-level `.typ`, `status.json`, `calendar.json`, or old English public filename is rejected.

Required standalone verification:

```bash
standalone_root="$(mktemp -d)"
mkdir -p "$standalone_root/skills"
cp -R skills/teaching-design-package "$standalone_root/skills/"
"$standalone_root/skills/teaching-design-package/scripts/teaching-design-package.sh" example --output "$standalone_root/package.md"
"$standalone_root/skills/teaching-design-package/scripts/teaching-design-package.sh" render-package --pdf --input "$standalone_root/package.md" --out-dir "$standalone_root/out"
find "$standalone_root/out" -maxdepth 1 -type f -print | sort
! rg 'skills/jiaoan-jihua|skills/jiaoan-shicao|jiaoan-jihua[.]sh|jiaoan-shicao[.]sh' "$standalone_root/out/.teaching-design-package" "$standalone_root/package.md"
```

Required legacy boundary checks:

```bash
git diff --name-only -- skills/jiaoan-jihua skills/jiaoan-shicao
! rg 'skills/jiaoan-jihua|skills/jiaoan-shicao|jiaoan-jihua[.]sh|jiaoan-shicao[.]sh|skills/jiaoan-jihua/references/calendar[.]json|skills/jiaoan-shicao/references/calendar[.]json' skills/teaching-design-package/scripts
```
</verification>

<success_criteria>
- [ ] `TDPKG-ART-01` complete: default public directory contains only course-name-prefixed final teacher-facing artifacts and no internal files.
- [ ] `TDPKG-ART-02` complete: current fixture produces exactly the four expected default public files.
- [ ] `TDPKG-ART-03` complete: hidden `.teaching-design-package/` contains module Markdown, module Typst, model, status, diagnostics, logs, calendar path/hash, scheduling summary, module registry, module PDF status, merge status, and failure evidence.
- [ ] `TDPKG-PDF-01` complete: all module PDFs exist and are non-empty before merged PDF is attempted.
- [ ] `TDPKG-PDF-02` complete: merge order is registry order, currently `teaching-plan` then `teaching-design`.
- [ ] `TDPKG-PDF-03` complete: actual merge tool and result are honestly recorded as `pdfunite`, `qpdf`, `python_fitz`, `not_run`, or failure.
- [ ] `TDPKG-PDF-04` complete: any module PDF or merge failure exits non-zero and cannot leave apparent public success.
- [ ] Standalone-copy regression passes using only `skills/teaching-design-package/`.
- [ ] Negative fixtures cover missing/empty module PDF, merge failure, invalid course name, and public leakage.
- [ ] Old `jiaoan-jihua` and `jiaoan-shicao` remain unmodified and absent from package runtime dependency checks.
</success_criteria>

---
*Phase: 36-public-delivery-pdf-merge-and-standalone-regression*
*Plan created: 2026-06-15*
