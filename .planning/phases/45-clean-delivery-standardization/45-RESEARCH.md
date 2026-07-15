# Phase 45: 全技能干净交付目录标准化改造 - Research

**Researched:** 2026-07-16
**Mode:** implementation / filesystem transaction / cross-skill regression
**Confidence:** High for repository-local behavior and required refactor boundaries; Medium for hard-crash durability because portable filesystems do not provide one atomic transaction over multiple stable root files

## Research Summary

Phase 45 不应把六个 renderer 重写成一套，也不应增加仓库根运行时 helper。正确做法是冻结一套共同的发布协议，再让每个 skill folder 以自己的现有语言和 renderer 适配协议：所有候选先生成到交付根内的 `.work/<run-id>/candidate/`，通过该技能最小验证后，在同根锁下完成受管集合比较、旧版成套归档、稳定文件名发布、失败回滚与本次工作目录清理。公共 shell 入口、现有命令名和参数继续可用；诊断型命令仍可向调用方显式 workdir 写证据，但不得把证据当作成功交付根内容。

当前实现不能只补文档。六个技能都存在真实行为差距：

- `school-pptx` 已有最强的 held-directory-descriptor、`O_NOFOLLOW`、同目录 staging 和 descriptor-relative `os.replace`，但仍是 Markdown-first/PPTX-last 两次替换；故障发生在两次替换之间会形成混版，而且 best-effort 异常 deck 会先发布再返回非零。
- `teaching-design-package` 在运行开头调用 `cleanup_public_root` 删除当前公开集合，失败路径也会再次清空公开根；这是 Phase 45 最严重的旧成功版本破坏点。
- `end-of-term-teaching-materials` 会先 unlink 既有四件套，再逐个直写 Markdown、Typst、XLSX、PDF；PDF 编译失败时前三项已经替换。
- `gongwen`、`school-presentation`、`tiaokedan` 都直接写最终路径；验证、大小门、参考比对或 PDF 编译失败可能留下新旧混合、半成品、过大 HTML、manifest/diff 或被提前删除的旧 PDF。

推荐将“发布协议共享”理解为共同状态机、断言、故障点和测试矩阵，而不是运行时跨 skill import。每个安装后的 skill folder 必须自包含；Python 技能可以复用 `school-pptx` 的安全 I/O 设计并各自携带 skill-local publisher module，`teaching-design-package` 可使用 skill-local Node/Bash transaction helper，`gongwen` 必须保持 shell-only Markdown→Typst 转换，其发布层可以用严格 Bash 锁、同根 staging、trap rollback 和现有系统文件命令，不得为了共享代码给 renderer 增加 Python/Node 转换依赖。

## Locked Scope and Planning Consequences

以下约束来自 `45-CONTEXT.md`、`REQUIREMENTS.md` 和 `docs/clean-delivery-directory-contract.md`，planner 不应重新打开：

1. 封闭覆盖六个技能：`end-of-term-teaching-materials`、`gongwen`、`school-pptx`、`school-presentation`、`teaching-design-package`、`tiaokedan`。
2. 不改变内容模型、版式、分页、评分、教学逻辑或最终格式；只改变候选、验证、归档、发布、失败清理和文档边界。
3. 保留现有公共 shell 入口、常用子命令和已发布参数；可以增加内部 helper 和标准故障注入，不得要求 sibling skill 或仓库根脚本参与正常运行。
4. 根一级只允许当前 Markdown、当前最终产物、`sources/`、`assets/`、`history/`、`.work/`。旧 `.teaching-design-package/`、`.tiaokedan/`、manifest、status、model、日志、diff、截图、验证证据、staging 和失败产物不再是成功根例外。
5. 未知文件、旧隐藏诊断和用户资料不自动移动或删除。正常发布遇到不能归属的根项应失败关闭；历史整理必须走只读审计→明确确认→执行的两阶段流程。
6. OpenClaw 与 Hermes Agent 是必需 runtime；支持声明必须基于 whole-folder 安装、支持文件发现、显式脚本 fallback、外部命令、sandbox/allowlist 和写权限的安装期验证。

## Current Skill Inventory

### Cross-skill snapshot

| Skill | Existing public delivery path | Current managed result | Existing staging/verification | Current failure hazard | Reusable base |
|---|---|---|---|---|---|
| `end-of-term-teaching-materials` | `deliver --input --out-dir` | fixed Markdown + Typst + PDF + XLSX | in-memory score checks; direct output writes | unlinks old four-file set before all generation/compile succeeds | Python renderer already centralizes all four outputs and format-specific verification |
| `gongwen` | `render --input --typ [--pdf] [--expected-typ]` | same-stem Markdown + Typst, optional PDF | shell parsing; optional byte compare; Typst CLI | truncates/writes Typst before expected/PDF gates; PDF compile is direct; old set is not archived | shell-only renderer, `same_file_shell`, deterministic fixture test |
| `school-pptx` | `render --input --out-dir [--stem]` | same-stem Markdown + editable PPTX | held root fd; O_NOFOLLOW; owned temp inode; staged PPTX package validation | pair replace is not atomic; between-replace fault mixes versions; best-effort publishes then exits 1 | strongest secure publish implementation and fault hooks |
| `school-presentation` | `render --input [--html] [--manifest]`; `verify --workdir` | Markdown + offline HTML; PDF is a separate export/postprocess surface | deterministic double render and rich verify workdir evidence | writes HTML/manifest before size and full delivery gate; oversized/failed render can overwrite current; manifest can be placed in root | mature deterministic render/verify separation and caller-owned evidence workdir |
| `teaching-design-package` | `render-package [--pdf] --input --out-dir` | course-prefix Markdown + merged PDF + 2 module PDFs | hidden work/staging/debug/status/failure tree; module compile and merge gates | deletes current set at start; sequential public copies; leakage/final-ready failure deletes current; hidden tree persists | best existing multi-artifact staging/merge registry and failure injection env vars |
| `tiaokedan` | `render --input --typ [--pdf] [--expected-typ]` | Markdown + Typst, optional PDF | Python parse/render; reference diff; PDF non-empty check | deletes old PDF before validation, writes Typst before reference/PDF gate; failure leaves mixed set | small Python renderer with clear compile failure boundary |

### `end-of-term-teaching-materials`

**Public contract and outputs**

- Entry: `skills/end-of-term-teaching-materials/scripts/end-of-term-teaching-materials.sh`.
- Final command: `deliver --input <md> --out-dir <dir>`.
- Stable fixed set: `end-of-term-full.md`, `end-of-term-package.typ`, `end-of-term-package.pdf`, `score-list.xlsx`.
- Source materials are agent inputs; only explicitly retained originals belong in `sources/`. The current renderer has no asset copy layer.

**Current implementation**

- `end_of_term/_engine.py::deliver` parses and validates Markdown before opening outputs, which is a useful content gate.
- It then creates the root, unlinks any existing expected public files (except an input-path collision case), writes Markdown, generates Typst and XLSX directly, and compiles PDF directly to the root.
- Calculated-score and score-list checks are in memory before Typst/XLSX publication, but PDF readiness occurs after earlier root writes.

**Failure behavior to replace**

- Any write/compile failure after unlink destroys or partially replaces the prior successful four-file set.
- PDF compilation failure deletes only the candidate PDF; new Markdown/Typst/XLSX remain public.
- No same-content detection, history sequencing, lock, rollback, root unknown-file gate, `.work` ownership or cleanup proof exists.

**Recommended adapter**

- Keep parse/score/render functions intact. Change `deliver` into: create bundle session→generate all four into candidate dir→validate Markdown UTF-8/non-empty, Typst non-empty, XLSX ZIP members/sheet shape, PDF compile exit/non-empty/readable→publish fixed set.
- `validate` remains read-only. Candidate diagnostics stay in the run tree or stderr.
- This is a good first Python adapter after the protocol tests because names are fixed and assets are not part of current successful output.

### `gongwen`

**Public contract and outputs**

- Entry: `skills/gongwen/scripts/gongwen.sh` and `gongwen_lib/*.sh`.
- Existing parameters must remain: `render --input --typ [--pdf] [--expected-typ]`.
- Root is derivable from `dirname(--typ)`; the managed basename is `basename(--typ, .typ)`. The Markdown copy must use that basename. If `--pdf` is present it must resolve to the same safe root and stem; reject cross-root or mismatched-stem publication.
- Existing docs describe a three-file final set, while CLI allows Typst-only. Preserve both modes as exact managed sets (`md+typ` or `md+typ+pdf`); a later run that adds/removes PDF is a changed bundle and therefore archives the previous whole set.

**Current implementation**

- The Markdown→Typst conversion is intentionally Bash-only and must stay so.
- `render_markdown_to_typst` writes the target Typst, optional `--expected-typ` compares after write, and `typst compile` writes the target PDF directly.
- `example` is authoring scaffold generation, not current-version publication; it should keep explicit output semantics and must not silently create history.

**Failure behavior to replace**

- Expected Typst mismatch occurs after target Typst replacement.
- Typst CLI absence/compile failure occurs after target Typst replacement and may leave an old or partial PDF depending on Typst behavior.
- No current Markdown copy is transactionally coupled to generated outputs.

**Recommended adapter**

- Render candidate Typst/PDF under `.work/<run-id>/candidate/`, run `cmp`/reference gate and PDF minimal checks there, then copy the reviewed Markdown into candidate under the stable stem.
- Preserve shell-only conversion. Implement a shell-local publication library or inline functions with `mkdir` exclusive lock, strict `lstat`/`test -L` refusal, `cmp -s`, same-filesystem checks, rollback trap and quoted fixed-name operations. Do not use glob deletion.
- Existing `tests/test_heading_normalization.sh` remains the renderer regression; add publication integration around it rather than replacing it.

### `school-pptx`

**Public contract and outputs**

- Entry: `skills/school-pptx/scripts/school-pptx.sh`.
- Final command and stable args remain `render --input --out-dir [--stem]`.
- Stable set is `<stem>.md` + `<stem>.pptx`; current Phase 43 contract requires Markdown byte preservation, but Phase 45 also locks `media/`→`assets/` normalization. Planner must make the migration explicit: do not silently rewrite arbitrary reviewed Markdown inside render. Prefer requiring finalized input to use `assets/...`, and treat one-time legacy `media/` rewrite as confirmed migration with reference validation.

**Current implementation**

- `SecureRenderDestination` already validates stem, rejects root symlink and final non-regular collisions, holds root descriptor and identity, creates `O_EXCL|O_NOFOLLOW` same-directory temp files, holds inode identities, fsyncs payloads, validates staged PPTX, uses descriptor-relative `os.replace`, fsyncs root, and removes only owned temp inodes.
- This is the reference for path safety, identity checking, owned cleanup and fault hooks across Python adapters.

**Failure behavior to replace**

- Publication is two replaces: Markdown first, PPTX last. `RENDER_BETWEEN_REPLACE_HOOK` intentionally demonstrates a mixed current pair.
- Parser/plan/runtime errors can still produce and publish a structurally valid best-effort pair, then return non-zero. Phase 45 SAFE-01 requires failed candidates not to masquerade as current delivery. Preserve best-effort generation as evidence only under `.work`/explicit verify workdir; do not publish it to the current root.
- No history, exact bundle equality, lock across runs, unknown-root allowlist gate or rollback of already replaced Markdown exists.

**Recommended adapter**

- Extend the destination into a bundle transaction: candidate generation and existing staged package validation remain unchanged; parser/plan/runtime diagnostics block current publication.
- Snapshot/verify the prior pair before replacement, create the next history bundle under the held root, replace the pair under lock, and restore both files plus remove the new history entry on any injected handled failure.
- Preserve `validate`, `template-report` and `verify --workdir` as explicit evidence surfaces; reject evidence paths inside a normal delivery root rather than broadening its allowlist.

### `school-presentation`

**Public contract and outputs**

- Entry: `skills/school-presentation/scripts/school-presentation.sh`.
- `render --input [--html] [--manifest] [--max-size-mb]` must keep accepting the same flags.
- Normal current delivery set should be reviewed Markdown + offline HTML. `manifest.json` is verification evidence, not a final artifact; when `--manifest` is used it must point into `.work/<run-id>/`, a system temp directory, or an explicitly separate caller verification workdir, never the delivery root.
- `bookmark-pdf` is a postprocess helper over an explicitly supplied printed PDF/manifest. Keep it callable, but perform it in work/evidence space; only a workflow that declares PDF as part of its candidate bundle may publish the final PDF. Do not retroactively claim browser printing is automated PDF acceptance.

**Current implementation**

- `cmd_render` resolves input, renders in memory, writes HTML directly, optionally writes manifest directly, then performs the size gate.
- `cmd_verify` correctly owns a caller workdir, writes multiple fixtures/manifests/HTML files there, recomputes deterministic behavior, and writes `verification-manifest.json`.

**Failure behavior to replace**

- An over-size HTML is already written before failure.
- A render or manifest write can overwrite existing current artifacts independently.
- Media warnings are recorded, not necessarily fatal; Phase 45 final publication must decide which are safe fallback and which violate required referenced-resource validity. Required missing assets must block publication.

**Recommended adapter**

- Render HTML and optional manifest in the candidate run tree, run existing size/offline/structure checks, validate every persistent `assets/` reference, then publish only Markdown+HTML (and only explicitly declared final PDF, if a future workflow has actually created it).
- Keep the rich verify command unchanged in purpose but ensure docs say its workdir is not a delivery root. Add root pollution assertions to verify.

### `teaching-design-package`

**Public contract and outputs**

- Entry: `skills/teaching-design-package/scripts/teaching-design-package.sh`.
- Final path remains `render-package --pdf --input --out-dir`.
- Dynamic stable set is course-prefix `1+1+N`; currently four files: one unified Markdown, one merged package PDF, one teaching-plan PDF, one teaching-design PDF.
- Existing `model`, `manifest`, non-PDF `render-package`, `plan-split` and `render-split` command names/flags must remain, but diagnostic/model/status outputs belong in an explicit workdir, not a successful delivery root.

**Current implementation**

- It already has the strongest multi-output candidate producer: model, module Markdown/Typst, module PDFs, merge plan and merged PDF are built under `.teaching-design-package/work|staging|debug`, with useful module/merge failure injection variables.
- The candidate set is copied sequentially to root only after module and merge checks.

**Failure behavior to replace**

- `cmd_render_package` calls `cleanup_public_root` before candidate work, deleting the previous successful version.
- `record_failure` also calls `cleanup_public_root`.
- Publication uses sequential `fs.copyFileSync` into final paths, then leakage/final-ready checks. A failure after copy deletes public files instead of restoring the previous version.
- `.teaching-design-package/` persists on both success and failure, contrary to Phase 45’s locked root allowlist.
- `cleanup_public_root` uses broad filename patterns and is not safe around unknown user files.

**Recommended adapter**

- Keep package model, formal renderers, module registry, staging compile, merge ordering and existing failure injection semantics.
- Relocate the entire hidden tree to `.work/<run-id>/`; stop creating `.teaching-design-package/` in delivery root.
- Delete `cleanup_public_root` from normal/failure paths. Derive the exact dynamic public set from the candidate model, validate it in staging, then pass the explicit filename list to a skill-local transaction publisher.
- Course-name changes require current-set discovery: accept exactly one structurally valid existing `1+1+N` set even if its prefix differs, archive it as the previous version, and reject ambiguous/multiple prefix groups as unknown content requiring cleanup confirmation.

### `tiaokedan`

**Public contract and outputs**

- Entry: `skills/tiaokedan/scripts/tiaokedan.sh` with unchanged `render --input --typ [--pdf] [--expected-typ]`.
- Derive root/stem exactly as for `gongwen`; preserve `md+typ` and optional `md+typ+pdf` modes.
- Existing hidden `.tiaokedan/` is only a documented possible diagnostic convention and is not currently written. Phase 45 should remove it from successful/failure root guidance; diagnostics stay in the run tree or stderr.

**Current implementation**

- Python parser blocks unresolved review markers before Typst generation.
- `render_command` deletes an existing PDF before parsing, writes Typst directly, performs expected comparison after write, then compiles PDF and removes only incomplete PDF on failure.

**Failure behavior to replace**

- A validation/compile run can remove the old PDF and leave a new Typst with an old Markdown.
- Expected mismatch prints an unbounded diff to stderr and leaves candidate Typst public.

**Recommended adapter**

- Move all candidate generation, expected comparison and PDF compile under `.work/<run-id>/candidate/`; bound public mismatch output and retain detailed diff only inside the run tree until cleanup.
- Reuse the Python bundle transaction pattern, but keep the renderer module and command arguments stable.

## Recommended Delivery Protocol

### 1. Explicit per-skill `DeliverySpec`

Every final-publication path needs a closed specification known before mutation:

- delivery root and stable public names;
- required and optional managed files for this invocation;
- persistent managed assets referenced by the current Markdown;
- format-specific minimal validators;
- current-set discovery rules;
- allowed first-level directories;
- commands that are diagnostic/authoring only and therefore not current publication.

Do not discover managed files with broad globs at deletion time. Discovery may classify existing state read-only, but mutation must use an explicit, validated relative-name list. `sources/` is user-owned and never mutated by normal publication. `assets/` contains only resources intentionally made persistent for the current version; arbitrary input files are not copied there.

### 2. State machine

Use the same conceptual states in every implementation:

```text
inspect root
  -> acquire same-root lock
  -> create owned .work/<run-id>
  -> generate complete candidate
  -> minimal validate candidate
  -> discover + validate current managed set
  -> exact set/content comparison
       -> identical: remove own run, release lock, no history
       -> first publish: publish candidate, fsync, cleanup
       -> changed: reserve next history, snapshot old set,
                   publish candidate, verify root, commit history,
                   cleanup
  -> on handled failure before commit: restore old set exactly,
                                       remove new finals/history,
                                       remove own run, release lock
```

The run tree should be no larger than necessary:

```text
.work/<run-id>/
├── candidate/       # complete candidate public set and candidate assets
├── rollback/        # exact old managed set until commit
└── evidence/        # temporary logs/diff/status used by gates
```

No persistent run manifest is needed. An internal journal may exist while a transaction is live, but it must be bounded, use only relative managed names/states, and be deleted during successful or rolled-back cleanup.

### 3. Root inspection and unknown-file gate

Before candidate publication, inspect root without following symlinks:

- allowed directories: `sources`, `assets`, `history`, `.work` only;
- current managed files: exactly one valid bundle according to the skill’s current-set discovery;
- all other entries, symlinks, device files, sockets, duplicate stems/prefixes, legacy hidden diagnostics or legacy `media/` are unknown.

Unknown entries must produce a bounded audit list and stop before mutation. Do not call the historical cleanup workflow automatically. Legacy `media/` and hidden directories require the same confirmation gate as other old agent output; after confirmation, migrate only referenced media to `assets/`, rewrite the affected text references, validate them, and leave unapproved content untouched.

### 4. Candidate equality

“相同内容” means both of the following:

1. managed relative-path sets are equal (including optional PDF presence and managed asset paths);
2. every corresponding regular file has identical bytes.

Do not compare only Markdown, stem, mtime, size or a stored manifest. Compute hashes/stream comparisons from held regular files and use hashes only in memory/evidence. Identical candidates create no `history/`, do not touch current mtimes/inodes, and remove the owned run tree.

### 5. History sequence and complete bundle

- Under the same lock, scan only non-symlink directories whose names match `^[0-9]{3,}$`.
- Next sequence is `max(existing numeric sequences)+1`, padded to at least three digits; do not reuse gaps.
- A version directory contains the old Markdown, every old final artifact, and any skill-owned assets needed for that Markdown to remain readable. Because an archived Markdown at `history/001/name.md` resolves `assets/x` as `history/001/assets/x`, referenced managed assets must be copied/moved into the same history version when the Markdown uses that path.
- `sources/` is not versioned or moved automatically. Unknown assets are not assumed managed.
- Never auto-delete history. Never create separate sequence numbers per artifact.

### 6. Transaction and rollback strategy

Portable filesystems do not expose one atomic operation that swaps several stable files plus `assets/` and `history/`. The implementation can and must guarantee candidate isolation and rollback for all handled failures, injected exceptions, `INT`/`TERM` traps and normal command errors; it must not claim mathematical cross-file atomicity under `SIGKILL`, power loss or filesystem corruption.

Recommended practical transaction:

1. Hold the delivery root identity and same-root lock for the full critical section.
2. Build and validate candidate before touching current.
3. Copy/hard-link the exact current managed files into `.work/<run-id>/rollback/`, fsync them, and re-hash against current. For assets, copy only the explicit managed paths; do not hard-link mutable files that later code might edit in place.
4. Prepare the history version from the verified rollback snapshot. Make it visible only as an exact closed bundle; if any later handled failure occurs, remove this newly created sequence.
5. Publish each candidate via same-directory atomic replace, tracking each completed name. Existing files are never truncated in place.
6. Run a post-publish root whitelist + byte/hash + format-readability check.
7. On any pre-commit exception, restore every old name from rollback with replace, remove newly introduced names, verify old hashes and existing history hashes, then remove the new sequence.
8. Fsync files and relevant directories, remove evidence/candidate/rollback, remove the owned run, remove empty `.work`, then release the lock.

Add a bounded recovery journal only if executor plans and tests include interrupted-process recovery. The safe rule is: a later invocation that finds an owned incomplete journal must recover/rollback before accepting any new candidate; it must not guess based only on mtimes. A stale unrelated `.work` entry is not command-owned and is not auto-deleted.

### 7. Lock and path safety

- Lock lives inside `.work` so no new root-level name is needed. Acquire exclusively; concurrent runs fail clearly instead of racing history sequence numbers.
- Validate every public/history/work name as one or more safe relative components: no absolute path, `..`, NUL, slash injection or platform separator escape.
- Refuse delivery root, support directory, managed file, history entry or candidate component symlinks. Hold and compare directory/file identities where the language supports it.
- Require `.work`, root and history to be on the same device for rename-based publication. If safe replace/rollback primitives are unavailable, fail closed with a runtime capability error.
- Cleanup removes only inode/path entries recorded as created by this run; no broad `find ... -delete`, wildcard rm or filename-pattern cleanup against the user root.

## Minimal Validation by Artifact

Minimal validation is not a replacement for renderer regression or human UAT. It is the last publication gate proving the candidate set is complete and readable:

| Artifact | Required publication gate |
|---|---|
| Markdown | regular non-symlink file, non-empty, UTF-8 readable, skill content validation/review markers passed, persistent relative asset references resolve inside candidate/current `assets/` |
| Typst | regular/non-empty/UTF-8 readable; generated by the existing renderer; if PDF requested, exact candidate Typst is the compile input |
| PDF | compile command exit 0, regular non-empty file, `%PDF-` header plus existing reader/merge validation where already available |
| XLSX | regular non-empty ZIP; required OOXML members readable; existing four-column/sort assertions pass |
| PPTX | existing bounded ZIP/XML/relationship `validate_staged_package`; expected slide count; no parser/plan/runtime error for current publication |
| HTML | UTF-8/readable/non-empty; size cap; offline single-file/required DOM tokens; required asset fallback policy passes |
| Teaching package | all registered module PDFs pass, merge order equals registry, merged PDF non-empty/readable, exact `1+1+N` candidate set exists |

Verification reports, logical JSON, status/model files, template reports, screenshots and diffs are temporary evidence, not additional final artifacts.

## Public Interface Preservation Map

| Command category | Phase 45 behavior |
|---|---|
| Final delivery (`deliver`, final `render`, `render-package --pdf`) | Same command/flags; internally redirects renderer output to `.work`, validates and transactionally publishes stable root set |
| Authoring scaffold (`example`) | Same explicit output behavior; not automatically treated as a revision transaction unless the requested path is intentionally the declared current Markdown workflow |
| Read-only validation (`validate`, `info`, `version`) | No delivery mutation; optional JSON/report only at explicit non-delivery evidence path |
| Verification (`verify --workdir`, `template-report`) | Writes only caller-owned verification workdir; docs and guards distinguish it from a delivery root |
| Package diagnostic commands (`model`, `manifest`, non-PDF render/split) | Same command names/flags; outputs remain diagnostic/work products under explicit workdir, never successful root sidecars |
| PDF postprocess (`bookmark-pdf`) | Same args; output is work/evidence unless a higher-level candidate bundle explicitly declares it final |

## Historical Agent Output Cleanup

`docs/agent-output-cleanup-prompt.md` already matches SAFE-02 well and should be formalized, not replaced by an eager cleanup command:

1. First pass is read-only and limited to explicit roots; no build, render, Git mutation, symlink following outside authorization or broad home scan.
2. Report exactly three operation groups: safe move, archive requiring confirmation, deletion requiring explicit approval.
3. Record root snapshots/hashes in memory or one bounded report; before execution re-check that audited inputs did not change.
4. Execute only approved items, using the same path/symlink/unknown-file constraints as publication.
5. Prefer user-approved isolation over permanent deletion; never let normal render/deliver trigger historical cleanup.
6. After execution perform only minimal current/history/reference checks and remove temporary evidence.

Planner should include a deterministic dry-run/audit fixture with unknown files, user sources, symlink escape and referenced assets. The execution half must require an explicit approval token or approved plan file produced by the exact audit snapshot; no `--yes` default.

## Recommended Implementation Batches

### Plan 45-01 — Protocol contract and regression harness

- Freeze a machine-checkable cross-skill protocol fixture: root whitelist, managed-set equality, history numbering, unknown-file refusal, owned work cleanup and standard fault points.
- Add the cross-skill regression harness under `test/` or a repository verification script. It may call skill public entries, but production skills must not import it.
- Define format validators and fault injection names before adapting skills so all later plans target the same assertions.
- Include historical cleanup audit/confirmation fixtures because unknown-file policy is shared with publisher discovery.

### Plan 45-02 — Python fixed/small bundles

- Adapt `end-of-term-teaching-materials` and `tiaokedan` using skill-local Python publishers.
- Preserve renderer logic; move all output and expected/PDF gates into candidate trees.
- Cover fixed four-file, two/three-file optional bundle and failure rollback first.

### Plan 45-03 — Presentation bundles

- Extend `school-pptx` held-descriptor publisher with lock/history/equality/rollback and block best-effort current publication.
- Adapt `school-presentation` render to candidate Markdown+HTML publication; keep manifests/verify evidence outside the root.
- Add explicit `media/`→`assets/` confirmed migration/reference tests without silently rewriting unrelated content.

### Plan 45-04 — Shell and complex multi-output bundles

- Add a shell-safe transactional adapter for `gongwen` without changing its shell-only conversion guarantee.
- Refactor `teaching-design-package` hidden staging into `.work/<run-id>`, remove destructive cleanup, publish its explicit model-derived `1+1+N` set through a skill-local transaction helper.
- Reuse existing TDP module/merge failure variables and add standardized archive/publish interruption points.

### Plan 45-05 — Full matrix, docs and runtime portability

- Run all six public-entry matrices and repository-wide static guards.
- Update root `README.md`, `docs/directory-spec.md`, `docs/compatibility-matrix.md`, `templates/skill/SKILL.md`, six `SKILL.md` files and each owning artifact reference.
- Remove successful-root documentation for `.teaching-design-package/` and `.tiaokedan/`; retain explicit verification-workdir guidance.
- Verify six runtime rows consistently mention whole-folder support files, explicit command fallback, dependencies/external commands, read/write permissions, sandbox/allowlist, delivery root, `.work`, history and failure cleanup; OpenClaw/Hermes claims remain installation-time verified.

Plans 45-02, 45-03 and 45-04 can run in parallel after 45-01 because they touch disjoint skill folders. Plan 45-05 must follow all adapters to avoid writing documentation against transient behavior. Keep cross-skill harness ownership in 45-01/45-05 so parallel plans do not edit one shared registry concurrently.

## Validation Architecture

Validation must prove the protocol at three levels: shared black-box invariants, each real public command, and repository documentation/runtime consistency.

### Layer A — Static command and self-contained installation

- `bash -n` all six shell dispatchers and shell libraries.
- `python3 -m py_compile` all changed Python publishers/renderers; syntax/import check Node helpers.
- Copy each whole skill folder to an isolated temporary install and run `--help`/`info` plus its lightweight fixture command without repository sibling imports.
- Assert public command names and existing flags remain present.
- Static scan forbids runtime imports/calls from one covered skill to another covered skill or to a repository-root publisher helper.

### Layer B — First publication for all six skills

For each skill, invoke the real public final-delivery command in a fresh temporary root using its canonical fixture and controlled dependency environment:

- exit 0;
- exact declared current managed set exists, files are regular/non-empty/readable;
- no history is created on first publication;
- root first-level names equal the skill whitelist;
- no manifest/status/model/log/diff/screenshot/staging/failure/legacy hidden directory leaks;
- own `.work/<run-id>` is gone and empty `.work` is removed;
- `sources/` and unrelated authorized caller paths are unchanged.

Use a deterministic fake `typst` only where it can produce a structurally readable PDF accepted by the same minimal gate; otherwise run the real available tool and record missing dependencies as a test blocker, not a dynamic skip. For `school-pptx`, retain the existing package validator and canonical fixture; for teaching package, retain real registry-order merge evidence inside temporary work until the gate completes.

### Layer C — Changed publication and complete history

For every skill:

1. Snapshot hashes of current set and any existing history.
2. Change both Markdown and at least one generated final artifact through the normal input path.
3. Publish again.
4. Assert `history/001/` contains the exact prior managed path set and hashes, including old managed assets needed by archived Markdown.
5. Assert root contains only the new complete set with stable names.
6. Repeat with pre-existing `history/001` and `history/003`; assert next is `004`, prior history hashes unchanged and no gap reuse.

Dynamic-prefix/stem cases must include a gongwen/tiaokedan/school-pptx stem change and a teaching course-name change. Ambiguous multiple prior sets must fail as unknown instead of selecting one by mtime.

### Layer D — Identical candidate no-op

- Re-run every real public command with byte-identical inputs and deterministic dependencies.
- Assert no new history entry, unchanged root hashes and mtimes/inodes where observable, unchanged existing history, and removed run tree.
- Include optional-set equality: a `md+typ` candidate is not equal to an existing `md+typ+pdf`; exact relative path set is part of identity.
- Mutation test the equality producer so hardcoded “same” or Markdown-only comparison fails.

### Layer E — Generation and validation failure isolation

Per skill, force at least two pre-publication failures:

- generation/tool failure: missing/forced Typst compile, forced teaching module/merge failure, PPTX emit failure, HTML render failure;
- validation failure: unresolved marker/invalid contract, malformed candidate container, empty artifact, missing persistent asset, over-size HTML or PPTX staged package corruption.

For each, assert non-zero bounded output, no false-success text, current root hashes unchanged, existing history hashes unchanged, no new history, no candidate/temporary evidence leakage, and owned `.work` cleanup. `school-pptx` best-effort pair may exist only inside owned work/evidence while handling the failure and must not become current.

### Layer F — Archive/publish interruption and rollback

Standardize test-only fault points, implemented without changing normal CLI shape, for example:

- `after_candidate_validation`
- `after_history_reservation`
- `after_archive_snapshot`
- `after_publish_file_1` (and a middle file for four-file bundles)
- `before_post_publish_verify`
- `before_work_cleanup`

At every supported point for every skill:

- command fails non-zero;
- original current managed set is restored byte-for-byte;
- no mixed-version root remains;
- pre-existing history is unchanged;
- newly reserved history is absent after rollback;
- root whitelist passes;
- own work tree and lock are cleaned.

Also run two concurrent publishers against one root: exactly one owns the lock; the other fails/retries without candidate publication or history sequence collision. Send `INT`/`TERM` to a controlled long-running fault hook and assert trap/finally rollback. If hard-crash recovery journal is implemented, add kill-and-next-run recovery; otherwise docs and tests must not claim SIGKILL/power-loss atomicity.

### Layer G — Unknown files, symlinks and authorization

- Root fixtures include unknown regular files, old `.teaching-design-package/`, old `.tiaokedan/`, legacy `media/`, duplicate final-like names, symlinks at root/support/history/work/final paths, path traversal stems and cross-root `--pdf`/manifest paths.
- Normal publication must stop before mutation and list bounded unknown entries.
- Snapshot all unknown/user files before/after; assert hashes/inodes/targets unchanged.
- Historical cleanup first run emits only audit/plan and performs zero mutation.
- Execution without exact explicit confirmation is rejected; approved fixture executes only listed operations.
- Out-of-authorized-root symlinks are reported but never followed.

### Layer H — Assets, sources and archived reference validity

- Use one referenced image/media fixture for each applicable presentation/document renderer.
- Assert only explicitly persistent referenced resources enter `assets/`; arbitrary source inputs are not copied.
- Migrate a confirmed `media/` fixture to `assets/`, update text references, and re-run minimal renderer/reference checks.
- After revision, parse archived Markdown/Typst/HTML relative references from `history/<sequence>/` and assert they resolve to assets within that version.
- Assert `sources/` remains byte-for-byte unchanged across render, identical no-op, failure and history publication.

### Layer I — Existing renderer regression and truthful UAT boundary

- Keep all existing renderer-specific tests: gongwen heading normalization, end-term score/XLSX assertions, school-presentation deterministic/interaction verification, school-pptx fixed public/21-gate verification, teaching module/merge registry tests, tiaokedan contract/PDF checks.
- Publication tests supplement rather than replace those gates.
- Real PowerPoint/WPS UAT for `school-pptx` and any human visual/export checks remain human-owned; directory standardization must not auto-sign them.
- Mutation guards should prove a publisher cannot declare success from file existence alone when the underlying renderer gate failed.

### Layer J — Documentation and runtime matrix

- Check all six `SKILL.md` files link the clean delivery contract or a stricter artifact reference and contain exact root whitelist, support directory lifecycle, revision/history behavior, failure cleanup and minimal verification.
- Check owning references and actual scripts agree on stable names and whether optional PDF is in the managed set.
- Check README, directory spec, compatibility matrix and `templates/skill/SKILL.md` describe the same six-skill protocol.
- Check exactly six runtime rows per skill and required semantic terms for support discovery, explicit fallback, external command/dependency, write permission, sandbox/allowlist, `.work`, `history`, unknown-file refusal and no persistent evidence.
- Check OpenClaw/Hermes notes use installation-time verification for uncertain discovery and do not claim runtime-specific wrappers.

## Risks and Planning Guards

### Risk 1 — Claiming multi-file atomicity

`os.replace` is atomic per path, not per bundle. Plans must say “candidate isolation + handled-failure rollback + optional crash recovery”, not “the whole set is atomically swapped” unless they introduce and verify a directory-indirection design compatible with stable root filenames.

### Risk 2 — Preserving best-effort by publishing it current

`school-pptx` best-effort behavior is useful diagnostic evidence but conflicts with SAFE-01 when the command is non-zero. Keep generation and editability, change destination to work/evidence, and publish current only on the full success gate.

### Risk 3 — Treating hidden diagnostics as allowed forever

Phase 45 explicitly supersedes `.teaching-design-package/` and `.tiaokedan/` root exceptions. Renaming them to another hidden directory does not satisfy CLEAN-03; only `.work/<run-id>` or system temp is allowed, and it must be cleaned.

### Risk 4 — Broad cleanup against dynamic names

The current TDP cleanup patterns can delete user content. All mutation must use an explicit set derived from a validated current/candidate bundle. Ambiguity means stop and route to confirmation-based cleanup.

### Risk 5 — Breaking shell-only `gongwen`

Do not add Python/Node as a Markdown conversion dependency. Publication safety may use portable shell/filesystem primitives, but the documented conversion stack remains Bash + optional Typst.

### Risk 6 — History without assets

Moving only Markdown/final binaries can leave archived Markdown with broken `assets/...` references. Treat skill-owned referenced assets as version members for archive/reference validation, while never moving `sources/` automatically.

### Risk 7 — Documentation-only runtime claims

OpenClaw/Hermes support must remain installation-time checked. Tests can validate whole-folder self-containment and explicit invocation locally; they cannot prove an uninstalled runtime’s automatic discovery.

### Risk 8 — Parallel plan conflicts

The six skill folders are parallelizable, but README/matrix/template and the cross-skill test registry are shared. Assign shared files to one foundation/finalization plan only; other plans should add skill-local tests and report required registry entries rather than editing the central list concurrently.

## Requirement Coverage

| Requirement | Research implementation target |
|---|---|
| CLEAN-01 | six explicit adapters; existing renderer/output capability retained |
| CLEAN-02 | per-skill `DeliverySpec` and root-state black-box assertions |
| CLEAN-03 | all temporary diagnostics relocated to owned `.work`/verification workdir; legacy hidden root exceptions removed |
| REV-01 | complete candidate under `.work/<run-id>/candidate` before current mutation |
| REV-02 | artifact-specific minimal validation table and no persistent evidence |
| REV-03 | exact path-set + byte equality; no-op history and unchanged current |
| REV-04 | locked next sequence, complete old bundle, stable-name new bundle, no auto-deletion |
| SAFE-01 | rollback snapshot, handled-failure fault matrix, signal/concurrency tests, truthful hard-crash limitation |
| SAFE-02 | existing cleanup prompt formalized as snapshot-bound two-stage confirmation workflow |
| VERIFY-01 | Layers B–I across all six real public entries |
| DOCS-01 | one final synchronization plan across root docs, templates, six entries and artifact references |
| RUNTIME-01 | whole-folder self-contained tests and consistent six-runtime safety/fallback notes |

## Planner Checklist

- Do not create a root runtime publisher imported by installed skills.
- Do not delete or restore the user’s currently deleted Phase 41–45 planning files; this research commit must contain only `45-RESEARCH.md`.
- Every executor task must name the exact public command and current failure point it is replacing.
- Every skill plan must include real first/change/same/failure/interruption/unknown/cleanup acceptance criteria, not only unit tests of a helper.
- Shared docs and central matrix changes belong after behavior is implemented and verified.
- Keep the plan checker focused on all 12 requirement IDs and the `## Validation Architecture` layers above.

