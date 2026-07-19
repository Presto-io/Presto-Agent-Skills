---
gsd_state_version: 1.0
milestone: v1.19
milestone_name: 毕业生高级简历生成器
status: executing
stopped_at: Phase 49 context gathered
last_updated: "2026-07-19T04:58:04.437Z"
last_activity: 2026-07-19 -- Phase 47 planning complete
progress:
  total_phases: 4
  completed_phases: 1
  total_plans: 16
  completed_plans: 13
  percent: 81
---

# State: Presto Agent Skills

## Project Reference

See: `.planning/PROJECT.md` (updated 2026-07-18)

**Core value:** A skill authored in the canonical repository format can be understood, reviewed, and adapted by every supported agent runtime with minimal manual rewrite.
**Current focus:** Phase 49 — 聚合验证、跨 Runtime 与发布验收

## Current Position

Phase: 49 (聚合验证、跨 Runtime 与发布验收) — EXECUTING
Plan: 1 of 2
Status: Ready to execute
Last activity: 2026-07-19 -- Phase 47 gap closure verified

## Workflow Preferences

- Mode: YOLO
- Granularity: Coarse
- Execution: Parallel
- Research: Yes
- Plan Check: Yes
- Verifier: Yes
- UI phase hints: Yes

## Latest Shipped Milestone

v1.18 standardized clean delivery across all six file-writing skills with candidate-first publication, byte-exact no-op detection, whole-bundle history, handled rollback, confirmation-gated cleanup, six-runtime documentation, and a strict six-skill verification aggregate.

Phase order:

- Phase 45: 全技能干净交付目录标准化改造

## Accumulated Context

### Decisions

- [Phase 47]: 页数门槛只读取版本化测量配置并将其 SHA-256 冻结在计划中；强制双页不以最低利用率拒绝，公开 plan 投影只公开布局元数据和字段名。

- [Phase 46]: `graduate-resume/v2` 的唯一事实源使用混合 Markdown/YAML：首页信息栏 `profile`、可选本地 `photo` 路径与派生 `preferences` 在 YAML，教育、技能、证书、项目、实训、经历和目标在 Markdown 正文；缺少 `photo` 即无照片，正文顺序不构成事实语义，布局容器由渲染器派生。
- [Phase 45]: Teaching Design Package expected_public_filenames is the sole dynamic mutation authority; current discovery accepts zero or one complete old prefix group and fails closed on ambiguity.
- [Phase 45]: Teaching Design Package model, status, module, merge, and debug outputs are evidence in an owned .work run or explicit diagnostic workdir, never current.
- [Phase 45]: Teaching Design Package portable guarantees cover exact candidate isolation and handled error/INT/TERM rollback, not SIGKILL, power loss, or multi-path hard atomicity.
- [Phase 45]: Gongwen --typ real parent/stem owns the exact Markdown+Typst pair; optional same-root/stem PDF changes it to a triple and archives the prior whole bundle.
- [Phase 45]: Gongwen PDF compilation consumes candidate Typst bytes through stdin while the reviewed Markdown parent remains the Typst root for existing assets references.
- [Phase 45]: Gongwen cleanup mutates only validated fixed names owned by the current Bash run; unknown, legacy, symlink, partial, and stale-work states fail before current mutation.
- [Phase 45]: End-of-term delivery uses one exact fixed four-file managed set; unknown, partial, symlink, legacy, and stale-work states fail before mutation.
- [Phase 45]: Typst compilation defaults `SOURCE_DATE_EPOCH` to zero so byte-identical reviewed input can produce a true no-op without changing output content.
- [Phase 45]: End-of-term runtime support uses whole-folder installation, explicit shell fallback, and installation-time verification for OpenClaw and Hermes Agent.
- [Phase 45]: Delivery equality requires the exact managed relative path set and byte equality, including explicitly managed assets.
- [Phase 45]: Portable guarantees cover per-path replace and handled failure/INT/TERM rollback, not SIGKILL, power loss, or cross-file atomicity.
- [Phase 45]: Historical cleanup execution requires exact approved operations bound to an unchanged no-follow snapshot.

- [v1.17]: Phase numbering continues after v1.16; this milestone starts at Phase 41 and ends at Phase 44.
- [v1.17]: Requirements coverage is limited to current v1.17 requirements only.
- [v1.17]: Build order follows research: hand-normalized standard template, hand-authored Markdown fixture/contract, renderer, then verification/runtime/UAT gate.
- [v1.17]: `school-pptx` is a new PPTX skill line, not a reopening of `school-presentation` HTML output.
- [Phase 41]: `standard-school` is the first controlled PPTX theme and is backed by a skill-local `.pptx`, YAML manifest, and `template-report` evidence command.
- [Phase 42]: Public Markdown exposes 10 authorable layouts; the manifest-owned `closing` remains exactly one implicit final page.
- [Phase 42]: Phase 43 consumes the source-located logical document model instead of reparsing Markdown.
- [Phase 42]: Validation aggregates bounded diagnostics and remains non-zero when safe missing-media fallback metadata is retained.
- [Phase 42]: All ten YAML formatter values must resolve to string scalars before entering the logical model.
- [Phase 42]: Fixed example output is published only through held no-follow directory descriptors; missing capabilities fail closed.
- [Phase 42]: `fixture-example` owns an explicit five-gap registry plus the secure-I/O capability companion.
- [Phase 43]: Dynamic table, gallery, and timeline objects derive every geometry and text budget from manifest subregions and presets.
- [Phase 43]: Physical pagination decisions are frozen, JSON-projectable values that the later PPTX emitter cannot mutate.
- [Phase 43]: CJK measurement uses deterministic grapheme-aware East Asian width fallback without CWD font discovery or PowerPoint autofit.
- [Phase 43]: All semantic splitting and structured balancing complete before PPTX emission and produce immutable physical plans. — This keeps emitter behavior deterministic and prevents PPTX object creation from changing pagination.
- [Phase 43]: PPTX emission consumes only the frozen PhysicalDeckPlan and never reruns pagination. — This keeps object generation deterministic and preserves the reviewed physical mapping.
- [Phase 43]: Transition mode is explicitly none for v1.17 emission. — Unstable viewer-specific transitions remain out of scope and absence is a valid PPTX-12 outcome.
- [Phase 43]: Render imports canonical parse_document in-process and publishes only the reviewed Markdown plus validated PPTX. — Avoids parser drift and public logical-model sidecars.
- [Phase 43]: Markdown-first and PPTX-last are individually atomic publications; PPTX is the deck-ready commit point. — Two independent files cannot form one cross-file transaction, so the crash window stays explicit and tested.
- [Phase 43]: Structurally valid best-effort decks remain editable and visually unpolluted while render exits non-zero and names affected logical slides. — Artifact existence must not be confused with successful rendering.
- [Phase 43]: Staged PPTX save and validation remain bound to duplicated streams for one held O_RDWR inode; path names are used only for identity checks and descriptor-relative replace.
- [Phase 43]: Public object failures expose only allowlisted stable codes and generic remediation; unknown object errors collapse to PPTX_OBJECT_INVALID.
- [Phase 43]: Code body text uses a delimiter-agnostic one-run monospace helper; optional code subheadings remain separate rich-text shapes.
- [Phase 43]: Multiple frozen code fragments on one physical slide are reconstructed only at their existing source-line boundary before literal emission.
- [Phase 43]: Two-column target slots, cover slot values, visible contents numbering, and native table row heights are immutable plan fields consumed mechanically by the emitter.
- [Phase 43]: Table content height is derived only from `table.height - table_name.height`; measured rows use ceil-to-EMU bounds and repeated headers retain one frozen height.
- [Phase 43]: Public template-report preflights all ZIP metadata, then chunk-reads bounded XML before parsing or relationship use. — This closes production reader drift while keeping public failures stable and bounded.
- [Phase 43]: Every non-code body slot uses one mixed-fragment textbox; code fragments are direct monospace runs while ordinary fragments retain native rich-text styles.
- [Phase 43]: Header-only tables are valid one-page native tables with exactly one frozen row and positive row height.
- [Phase 43]: Pillow bomb and format/decode failures cross the public boundary only through precise allowlisted codes and bounded generic diagnostics.
- [Phase 43]: Phase 43 aggregate has a fixed 21-gate order with exact required/called equality, zero dynamic skips, raw-evidence recomputation, and AST mutation guards against false-green producer constants.
- [Phase 43]: Mixed body pagination and native emission share frozen 24pt/22pt target-slot typography and controlled spacing. — This prevents successful PPTX output from silently clipping code measured at a smaller size.
- [Phase 43]: Media validation and `add_picture` consume one bounded descriptor-read payload, closing the media TOCTOU window; the 21-gate aggregate verifies capacity vectors and source-derived producer evidence.
- [Phase 43]: Paginator and emitter consume one frozen paragraph sequence, so headings, paragraphs, list items, code runs, line spacing, and paragraph spacing share one full-frame capacity contract.
- [Phase 43]: Contents freeze 26pt typography and dedicated code freezes 14pt typography; both public render and reopened PPTX evidence block successful clipping or font drift.
- [Phase 43]: The fixed 21-gate aggregate recomputes equality from raw text/media/projection/target hashes and rejects constant producer evidence through AST mutation guards.
- [Phase 44]: Public verification owns one fixed eight-gate authority and publishes current JSON/Markdown evidence from the same bounded observed projection.
- [Phase 44]: Plan 44-01 reserves later gates as explicit `NOT_IMPLEMENTED` failures; foundation completion cannot produce a false public PASS.
- [Phase 44]: Required Python imports are observed fresh while Pandoc remains optional and never changes gate readiness while unused.
- [Phase 44]: Public verify executes exact fixed registries of 8 top-level gates, 6 negative cases, and the reused 21-gate Phase 43 authority with required/called equality and zero dynamic skips.
- [Phase 44]: Fresh canonical evidence is SHA-256-bound to the reopened 13-logical/32-physical delivery; structural claims are recomputed from OOXML and native editable objects.
- [Phase 44]: Negative mutations remain inside per-case copied trees and must fail non-zero with exact stable codes, bounded output, unchanged canonical hashes, and no false-success evidence.
- [Phase 44]: One concise canonical `school-pptx/SKILL.md` owns the runtime-neutral workflow; renderer, verification, and UAT detail remains in progressive references.
- [Phase 44]: Documentation integrity is part of the public evidence-integrity gate and checks the canonical entry, fixed 8/6/21 contracts, six runtime rows, and repository discovery links.
- [Phase 44]: OpenClaw and Hermes Agent support remains installation-time verified with explicit script fallback; no untested automatic discovery path is claimed.
- [Phase 44]: The final human acceptance is bound to canonical PPTX SHA-256 `ed99daa1b7a187a2adb57f9769c1ecf282bc48ad950309cfbef3805a8f9af963` and verification run `76d62c9155092a76`; Mrered passed all 10 checks in WPS Presentation 12.1.26035 on macOS 26.5.2.
- [Phase 45]: Tiaokedan --typ owns the delivery root and stable stem; optional --pdf must use the same root and stem and changes the exact managed set.
- [Phase 45]: Tiaokedan expected comparison and PDF compilation consume only owned candidates before current mutation.
- [Phase 45]: Tiaokedan legacy .tiaokedan, media, unknown, symlink, partial, and stale-work states require audit rather than automatic cleanup.
- [Phase 45]: School PPTX current delivery is the exact reviewed Markdown, validated PPTX, and confirmed assets/... paths that remain referenced by the bundle.
- [Phase 45]: School PPTX archives old pair and managed assets under one sequence so archived Markdown references resolve without mutating sources/.
- [Phase 45]: Parser, planner, runtime, or validation failures keep editable best-effort output in owned work evidence and never publish it as current.
- [Phase 45]: School Presentation current is exactly reviewed Markdown plus offline HTML and explicitly referenced assets; manifests and verify evidence remain outside the delivery root.
- [Phase 45]: A same-root reviewed Markdown may seed first HTML publication, but handled failure restores its original bytes and creates no false history.
- [Phase 45]: School Presentation legacy media requires confirmed migration to assets; missing required assets and unsafe evidence paths fail before current mutation.
- [Phase 45]: Repository discovery names exactly six implemented writing skills; no unlisted skill inherits clean-delivery status implicitly.
- [Phase 45]: Verification workdirs are caller-owned evidence roots rather than delivery roots, and normal publication never promotes diagnostic evidence to current.
- [Phase 45]: OpenClaw and Hermes Agent support remains installation-time verified with explicit public-script fallback and no automatic-discovery claim.
- [Phase 47]: 三个首批主题只登记视觉 token；照片以逻辑相对资产和冻结 contain/forbid 策略进入计划，不携带物理路径或事实。 — 主题扩展不得改写 graduate-resume/v2。
- [Phase 47]: 受控字体清单在计划前验证 SHA-256 与 Typst 可见性；批准上游 Bold 的物理 700 保持原样并承担 UI 语义 600 角色。 — 不篡改上游 OFL 字体且不依赖系统回退。
- [Phase 47]: 固定布局矩阵使用字面 fixture/theme 注册表并在临时 workdir 验证 PDF/PNG；正式交付仍属 Phase 48。 — 防止隐式样张漂移且避免把临时证据发布为投递产物。
- [Phase 48]: 事实排序固定为受控模块顺序、pin 优先、整数相关性降序和稳定事实 ID；正文顺序不参与投影。 — 确保正文重排不会改变版本语义。
- [Phase 48]: 只有 education_level、major_exact、certificate_exact、fresh_graduate_status 可产生 meets/gap；其他条件回退 unknown。 — 相关性不能作为资格证明。
- [Phase 48]: current 身份只消费显式 safe stem 与登记主题后缀，不通过连字符反向解析单位或岗位。 — 防止含连字符的单位或岗位被错误识别为 managed identity。
- [Phase 48]: patch 保留非 candidate current；authority removals 必须由绑定整个 no-follow current snapshot 的批准摘要确认。 — 区分单份更新与权威批量替换，并阻止确认后的 TOCTOU。
- [Phase 48]: history 只归档 updated/removed 完整 triples，handled rollback 恢复整个原 current path set 与 bytes。 — 同时满足最小历史副本与全批失败恢复。
- [Phase 48]: render 固定 generic/单 target patch，batch 固定 generic + all confirmed targets authority；确认绑定同一 held-root preflight digest。 — 区分单份保留与权威批量移除，并阻止确认后的 snapshot 漂移。
- [Phase 48]: Phase 48 aggregate 使用字面固定 13 gate registry 观察窄测试。 — 禁止动态发现、动态跳过或把 Phase 49 authority 冒充为本阶段证据。
- [Phase 48]: not-applicable 只有 target ID、condition ID、1..200 Unicode code points reason 的三参数公开入口。 — 消除第二入口歧义，完整理由仅留 hidden evidence。
- [Phase 48]: canonical 可保留 declined，但正式 publication 对任何非 verified 候选事实 fail closed。
- [Phase 48]: 事实 ID 使用统一稳定 grammar，profile 固定为 profile，canonical、resolver、final Markdown 与 Typst 四层复验。
- [Phase 48]: ContainerPlan.fields 同时驱动高度、分页和 Typst/PDF。
- [Phase 48]: 显式 photo 必须绑定 provided 安全本地资产，只有 auto 可降级 no-photo。
- [Phase 48]: 含 target 的正式 render/batch 必须显式授权独立 evidence root；generic-only publication 不创建隐藏证据。
- [Phase 48]: 历史 stem 以 verified canonical 姓名生成的冻结 owner_prefix、独立结构和登记主题校验，不依赖当前 authority membership。
- [Phase 48]: patch 与 authority 统一要求 reviewed approval digest，摘要绑定完整 candidate/current bytes、canonical hash 和 delivery/evidence root path+inode。
- [Phase 48]: 非 target metadata 精确且唯一为 id/status，target 精确且唯一为 id；缺失、额外、空值或重复在事实投影前失败。
- [Phase 48]: canonical 输入以 4 MiB 有界 O_NOFOLLOW 普通文件 descriptor 单次读取，并冻结 source bytes 与 SHA-256。
- [Phase 48]: canonical path 只用于定位和默认 assets-root；final Markdown、evidence 与 approval payload 统一消费 source_sha256。
- [Phase 48]: Phase 48 投递根的 support allowlist 仅保留 history 与 .work；sources/assets 的任何文件系统形态都按 unknown fail closed。 — 防止私密附件或诊断材料被合法 current 吸收。
- [Phase 48]: close() 固定尽力执行全部 owned cleanup，再以 operation、相对 owned name 与 errno 聚合为一个 bounded DeliveryError。 — 确保清理失败不会被首个错误截断或伪装成成功。
- [Phase 48]: cleanup 首次失败后 session 进入 closed 状态，重复 close 不重试不确定 syscall，也不产生新的错误。 — 避免 close 失败后的 descriptor 状态不确定性造成二次误操作。
- [Phase 48]: Typst 只通过 PATH 定位一次源候选，版本、字体、照片与 PDF 全部执行 held descriptor 复制的 immutable 0.15.0 snapshot。 — 阻止版本门禁后 PATH 或 Cellar target 替换改变真实渲染对象。
- [Phase 48]: 照片 leaf 在 held assets-root 下 O_NOFOLLOW 打开一次，格式、大小、SHA-256、规范化与 approval 共享同一 frozen bytes。 — 关闭照片校验后按逻辑路径二次读取的 TOCTOU。
- [Phase 48]: plan/render/batch 各自恰好持有一个 TypstExecutable context；validate/target 与渲染工具链保持解耦。 — 让所有生产 subprocess 共用同一版本门禁，同时保持离线 schema 命令无工具链依赖。

### Pending Todos

None yet.

### Blockers/Concerns

- [Phase 48] 标准代码审查仍记录 6 个 Blocker 与 3 个 Warning；正式阶段 verifier 已通过，进入 Phase 49 前应决定是否先运行 `/gsd:code-review 48 --fix`。
- [Phase 48] 安全执行门尚无 `48-SECURITY.md`，推进前需运行 `/gsd:secure-phase 48`。

## Performance Metrics

| Phase-Plan | Duration | Tasks | Files |
|------------|----------|-------|-------|
| 42-01 | 47 min | 3 | 4 |
| Phase 42 P02 | 11min | 3 tasks | 8 files |
| 42-03 | 22 min | 3 | 3 |
| Phase 43 P01 | 6 min | 3 tasks | 6 files |
| Phase 43 P02 | 12 min | 3 tasks | 2 files |
| Phase 43 P03 | 14 min | 3 tasks | 4 files |
| Phase 43 P04 | 19 min | 3 tasks | 3 files |
| Phase 43 P05 | 20 min | 2 tasks | 3 files |
| Phase 43 P06 | 29 min | 2 tasks | 3 files |
| Phase 43 P07 | 16 min | 3 tasks | 8 files |
| Phase 43 P08 | 18 min | 2 tasks | 3 files |
| Phase 43 P09 | 27 min | 3 tasks | 4 files |
| Phase 43 P10 | 25 min | 3 tasks | 5 files |
| Phase 43 P11 | 55 min | 3 tasks | 5 files |
| Phase 44 P01 | 47 min | 3 tasks | 5 files |
| Phase 44 P02 | 37 min | 3 tasks | 6 files |
| Phase 44 P03 | 17 min | 3 tasks | 9 files |
| Phase 44 P04 | human UAT | 10 checks | 4 planning files |
| Phase 45 P01 | 9 min | 3 tasks | 4 files |
| Phase 45 P02 | 21 min | 3 tasks | 5 files |
| Phase 45 P03 | 12 min | 3 tasks | 6 files |
| Phase 45 P04 | 38 min | 2 tasks | 8 files |
| Phase 45 P05 | 19 min | 3 tasks | 6 files |
| Phase 45 P06 | 21 min | 2 tasks | 7 files |
| Phase 45 P07 | 10h 41m | 3 tasks | 6 files |
| Phase 45 P08 | 20 min | 2 tasks | 5 files |
| Phase 45 P09 | 2h 50m | 3 tasks | 5 plan-owned files |
| Phase 47 P01 | 37 min | 3 tasks | 10 files |
| Phase 47 P02 | 28 min | 3 tasks | 6 files |
| Phase 47 P03 | 34min | 3 tasks | 12 files |
| Phase 47 P04 | 17 min | verification gap closure | 6 files |
| Phase 48 P01 | 11min | 2 tasks | 4 files |
| Phase 48 P03 | 11min | 2 tasks | 2 files |
| Phase 48 P04 | 23min | 3 tasks | 5 files |
| Phase 48 P05 | 39min | 3 tasks | 8 files |
| Phase 48 P06 | 37min | 3 tasks | 6 files |
| Phase 48 P07 | 14min | 2 tasks | 2 files |
| Phase 48 P09 | 12min | 2 tasks | 2 files |
| Phase 48 P08 | 46min | 3 tasks | 8 files |

## Session Continuity

Last session: 2026-07-18T17:23:56.942Z
Stopped at: Phase 49 context gathered
Resume file: .planning/phases/49-runtime/49-CONTEXT.md

## Operator Next Steps

- Review Phase 48 advisory debt, then discuss or plan Phase 49.
