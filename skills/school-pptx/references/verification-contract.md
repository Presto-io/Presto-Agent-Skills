# school-pptx Verification Contract

本 reference 是 public `verify` 的长契约；机器事实源仍是 `scripts/verify_school_pptx.py` 中的固定常量和 observed evidence。自动验证不安装依赖、不联网，也不批准真实 viewer UAT。

## Public Entry and Workdir Ownership

```bash
skills/school-pptx/scripts/school-pptx.sh verify --workdir <caller-workdir>
```

`--workdir` 是唯一 public verification root，必须由调用方显式提供且不得复用普通 render delivery root。命令只在该调用方目录下写入：

```text
<caller-workdir>/
├── delivery/                 # current canonical same-stem .md + .pptx only
├── evidence/                 # current bounded verification.json/.md
└── work/<run-id>/            # staging, reports and isolated negative cases
```

证据中的 artifact path 必须相对 workdir。验证不得修改 canonical template、manifest、fixture、用户输入或无关调用方文件；失败运行发布 current `status: failed`，旧 PASS 不得作为当前证据。delivery 与 evidence/work 分离，普通用户交付目录不接收验证 sidecar。

## Fixed Top-level Registry

顺序、名称、唯一性和调用完整性均为公共契约：

1. `dependency-readiness`
2. `example-generation`
3. `template-validation`
4. `canonical-render`
5. `structural-inspection`
6. `phase-43-regression`
7. `negative-cases`
8. `evidence-integrity`

成功时 `required == called`、顺序相同、元素唯一且 `dynamic_skips == 0`。aggregate 从每个 raw gate outcome 重算；缺项、重复、乱序、动态 skip 或失败 gate 都使 public command 非零。

## Fixed Negative Registry

| Case id | Expected stable code |
|---|---|
| `unknown-theme` | `THEME_UNKNOWN` |
| `unknown-layout` | `LAYOUT_UNKNOWN` |
| `missing-media` | `MEDIA_MISSING` |
| `unsupported-styling` | `UNSUPPORTED_STYLE` |
| `unresolved-review-marker` | `REVIEW_MARKER_UNRESOLVED` |
| `template-manifest-mismatch` | `TEMPLATE_MANIFEST_MISMATCH` |

六项必须固定顺序全部执行、零 skip。每项在独立 copied tree 内运行真实 public validate/render/template-report 路径，并断言 non-zero exit、exact code、capture 小于 8192 bytes、无 traceback、无 false-success 文案、无 case root 外写入且 protected hashes 不变。非零 render 的 best-effort pair 只存在于该运行的 owned work evidence 生命周期，不能留在 case delivery 或伪装 current。

## Clean-delivery Publication Regression

`scripts/verify_pptx_renderer.py --self-test delivery-transaction` 使用真实 public render 覆盖 first/change/same、generation/validation failure、七 fault、history gap、unknown/symlink/traversal、lock/work cleanup、sources 与 managed assets。固定七 fault registry 必须满足 `required == called`、唯一且 `dynamic_skips == 0`。confirmed-assets fixture 只纳管 `assets/robot-arm.png`，另置的未引用输入不得复制；changed case 解析 `history/<sequence>/confirmed-assets.md` 的每个 `assets/...` 引用，并验证同 sequence bytes。

这些 gate 只证明 current DeliverySpec 的 exact set+bytes、handled-failure rollback、归档引用和 OOXML 可读性。它们不证明多路径硬原子、`SIGKILL`/断电恢复，也不将 PowerPoint/WPS 人工视觉、编辑、notes 或导出检查标为 PASS。

## Phase 43 Nested Authority

`phase-43-regression` 必须调用既有 21-gate authority，且按下列顺序满足 `required == called`、唯一、`dynamic_skips == 0`：

1. `contract-model`
2. `pagination`
3. `frozen-slot-content`
4. `frozen-numbering-row-heights`
5. `ooxml-bootstrap`
6. `editable-objects`
7. `code-literal-roundtrip`
8. `mixed-fragment-capacity`
9. `frame-capacity-consistency`
10. `emit-structure`
11. `frozen-plan-emission`
12. `cli-publication`
13. `best-effort`
14. `publication-safety`
15. `publication-descriptor-race`
16. `table-header-only`
17. `object-error-bounded`
18. `media-descriptor-binding`
19. `template-reader-security`
20. `determinism`
21. `phase_41_42_regression`

这层是 nested regression，不替代顶层八 gate，也不能复制旧 JSON 作为 fresh result。

## Dependency Semantics

- required：当前 Python，以及 `python-pptx`、Pillow、lxml、PyYAML import readiness；缺失任一项即 fail closed。
- optional：Pandoc。当前路径不使用 Pandoc，因此只记录 availability/version，缺失不影响 PASS。
- 记录 Python implementation/version、sanitized executable identity、选择来源和包版本；不记录用户 home absolute path。
- verifier 不运行 pip/uv/conda install，不下载字体、模板、媒体或任何网络资源。

## Bounded Evidence

`verification.json` 与 `verification.md` 从同一个 in-memory observed candidate 生成。JSON 至少包含：

- `schema_version`、`status`、bounded run id/timestamps；
- 顶层 registry、各 gate status/code/evidence；
- sanitized dependency observations；
- canonical Markdown/PPTX relative path、SHA-256 和 byte count；
- fresh logical/physical counts、layout mapping、logical→physical indices；
- source/reopen contents operands、expected/observed notes；
- media relationships/hashes/crop、native tables、editable code、groups、timeline/gallery；
- geometry-derived `whole_slide_picture_count` 和 `transition_mode`；
- negative registry/cases 与 protected-hash observations；
- bounded stable diagnostics。

证据禁止绝对用户路径、PPTX/raw Markdown bytes、unbounded text/list、traceback、secret 或 PEM 内容。`transition_mode` 只允许 `none|preserved|generated`；当前 `none` 是合法 observed result。canonical baseline 是 13 logical slides → 26 physical slides，但 aggregate 必须从 fresh source/PPTX raw operands 重算，不能硬编码 PASS。

## Freshness, Exit Rules, and Troubleshooting

- fresh PASS：全部 8/6/21 registry 完整，当前 evidence 从本次 artifacts 观察并通过 integrity。
- stale/failed：后续失败必须把 current evidence 更新为 failed；历史成功不能覆盖本次状态。
- public exit `0` 只表示自动验证通过；dependency、render、negative、registry、evidence 或 documentation-integrity 失败均非零。
- `VERIFY_DEPENDENCY_MISSING`：在调用方环境补齐 required Python packages，再重跑；verifier 不代为安装。
- `VERIFY_WORKDIR_UNSAFE`：改用真实、可写、非 symlink 的调用方目录。
- `VERIFY_EVIDENCE_INVALID`：检查 bounded current evidence、固定 registry、文档 canonical links/runtime rows 与源码 drift。
- 某一 public negative diagnostic 改名时，必须同步实现常量、本 reference 和 self-test；不要靠自然语言 substring 兼容。

自动 OOXML reopen 只证明结构。里程碑接受仍需按 [visual-uat.md](visual-uat.md) 在真实 Microsoft PowerPoint 或 WPS Presentation 中完成全部人工项。
