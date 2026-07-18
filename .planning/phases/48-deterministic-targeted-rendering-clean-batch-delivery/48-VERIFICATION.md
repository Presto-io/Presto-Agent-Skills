---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
verified: 2026-07-18T13:56:41Z
status: gaps_found
score: 1/5 must-haves verified
overrides_applied: 0
re_verification:
  previous_status: gaps_found
  previous_score: 1/5
  gaps_closed:
    - "declined/pending publication、事实 ID 注入、结构化字段丢失和显式照片静默降级已关闭。"
    - "单目标逐条件公开投影、digest-bound hidden evidence 已接通。"
    - "历史 stem 已与当前 authority 解耦，删除目标后的连续 no-op 已恢复。"
    - "--confirm 已要求用户提交上一独立预检的 --approval-digest。"
  gaps_remaining: []
  regressions: []
gaps:
  - truth: "正式定向只能消费显式标记为 verified 的事实，缺失、拼错或重复复核状态必须失败关闭。"
    status: failed
    reason: "Markdown metadata 未校验精确字段和重复键，并以 verified 作为缺省状态；未复核事实可被静默提升后进入定向、条件判定和正式三件套。"
    artifacts:
      - path: "skills/graduate-resume/scripts/graduate_resume_cli.py"
        issue: "parse_metadata 覆盖重复键；parse_markdown_facts 使用 metadata.get('status', 'verified')。"
    missing:
      - "非 target 条目必须精确且唯一地提供 id/status，target 必须只提供 id。"
      - "缺失、拼错、额外或重复 metadata key 的 CLI 负例。"
  - truth: "照片校验与消费必须绑定同一 no-follow 文件快照，不能在校验后跟随替换的 symlink。"
    status: failed
    reason: "resolve_layout_photo 只返回逻辑路径；CLI 随后按路径重新 read_bytes，存在可复现的校验后 symlink 替换窗口。"
    artifacts:
      - path: "skills/graduate-resume/scripts/graduate_resume_layout.py"
        issue: "校验图片后仅返回 PhotoAsset 路径，没有返回 held descriptor 或已验证 bytes。"
      - path: "skills/graduate-resume/scripts/graduate_resume_cli.py"
        issue: "_resolve_publication_photo 对已验证路径执行第二次可跟随 symlink 的读取。"
    missing:
      - "在 held assets-root descriptor 下以 O_NOFOLLOW 打开并从同一 descriptor 校验、读取有界 bytes。"
      - "校验后 inode/symlink swap 回归。"
  - truth: "最终事实、canonical hash 与审批摘要必须来自同一个不可变输入快照。"
    status: failed
    reason: "load_resume 读取并解析一次，发布编排又从路径重读 bytes 计算 canonical_hash；文件在两次读取间变化时会用旧事实渲染、却声明绑定新 hash。"
    artifacts:
      - path: "skills/graduate-resume/scripts/graduate_resume_cli.py"
        issue: "ResumeDocument 不保存原始 bytes/hash；_command_publication 在投影后再次 document.path.read_bytes()。"
    missing:
      - "一次 no-follow、有界读取后冻结原始 bytes/hash，解析、渲染与审批全部消费同一快照。"
      - "单进程 load 后替换 canonical 的负例。"
  - truth: "Phase 48 投递根只能包含平铺正式 triples 和事务 history/.work，不接受 sources/assets 或私密附件。"
    status: failed
    reason: "DeliverySession 将 sources/assets 作为合法支持目录且不检查其内容；临时根中的 sources/private.txt 与 assets/private.txt 均被接受。"
    artifacts:
      - path: "skills/graduate-resume/scripts/graduate_resume_delivery.py"
        issue: "SUPPORT_DIRECTORIES 包含 sources/assets，_inspect_current 只确认它们是目录。"
    missing:
      - "Phase 48 只允许 history 和事务拥有的 .work；sources/assets 一律 unknown fail-closed。"
      - "非空 sources/assets 在 mutation 前失败且 current/history 不变的回归。"
  - truth: "受控渲染必须实际锁定 Typst 0.15.0，不能仅依赖命令名或错误文案。"
    status: failed
    reason: "字体探测、照片规范化与 PDF 编译均未调用 typst --version；伪造的 Typst 9.9 只要返回预期 fonts 文本即可通过当前门禁。"
    artifacts:
      - path: "skills/graduate-resume/scripts/graduate_resume_layout.py"
        issue: "_validate_font_visibility 只运行 fonts 子命令。"
      - path: "skills/graduate-resume/scripts/graduate_resume_typst.py"
        issue: "normalize_photo_bytes 只检查 shutil.which 后直接 compile。"
      - path: "skills/graduate-resume/scripts/graduate_resume_render.py"
        issue: "_compile_typst 直接调用字符串 typst。"
    missing:
      - "唯一 Typst resolver，冻结绝对路径并精确校验版本 0.15.0。"
      - "三个生产消费者复用同一已验证可执行文件，增加错误版本假实现负例。"
---

# Phase 48: 确定性定向渲染与干净批量交付 Verification Report

**Phase Goal:** 用户能离线生成通用版及多个透明、可追溯的定向简历三件套，并在失败时保持当前成功交付。
**Verified:** 2026-07-18T13:56:41Z
**Status:** gaps_found
**Re-verification:** 是，上一轮缺口关闭后复核；本轮发现新的生产边界阻断项

## Goal Achievement

### Observable Truths

| # | Roadmap Success Criterion | Status | Evidence |
|---|---|---|---|
| 1 | 同一已核实资料生成通用版及每个单位+岗位的定向版，且只选择、排序或强调已核实事实 | ✗ FAILED | `stats=pending`、缺失 `status`、重复 `status` 均被解析为 `verified` 并通过校验；53 项现有窄测试未覆盖。 |
| 2 | 用户可查看硬条件四态；gap 可明确放行且简历不暗示满足 | ✗ FAILED | 逐条件公开行、hidden evidence 和 gap gate 已接通，但状态提升漏洞会把未复核 evidence 当作 verified，四态中的 `meets` 不再可信。 |
| 3 | 每个版本记录实际主题、页数、照片模式、目标及来源/日期，且不抓取或猜测招聘信息 | ✓ VERIFIED | final Markdown 记录上述字段；目标信息只来自本地 canonical/CLI，生产路径未发现网络调用。canonical hash 错绑另作为可追溯性阻断。 |
| 4 | 每个成功版本同 stem 输出正式命名的 Markdown、Typst、PDF 三件套，投递根保持干净 | ✗ FAILED | triples/命名可生成，但 delivery transaction 明确接受任意非空 `sources/`、`assets/`，违反路线图和 D-13 的干净投递根。 |
| 5 | 单份/批量完整预检，失败零部分发布，并保持 candidate-first、no-op、history、rollback、unknown/symlink fail-closed | ✗ FAILED | reviewed digest、history/no-op 和故障 rollback 测试通过；但 canonical 两次读取与照片二次路径读取使预检不能绑定实际消费快照，cleanup 错误还会被静默吞掉。 |

**Score:** 1/5 truths verified

上一轮五类缺口均有当前代码与回归证明已关闭；本报告中的五项是独立复核代码审查后确认的新阻断项，不是沿用旧报告结论。

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `skills/graduate-resume/templates/targeting-policy.json` | 冻结离线定向策略 | ✓ VERIFIED | 精确字段、版本和 raw-bytes SHA-256 存在。 |
| `skills/graduate-resume/scripts/graduate_resume_targeting.py` | 稳定投影、四态条件与 gap gate | ⚠ PARTIAL | 算法与 evidence 投影实质存在；上游 metadata 状态提升破坏 verified-evidence 前提。 |
| `skills/graduate-resume/scripts/graduate_resume_final_markdown.py` | 可重读并绑定的最终 Markdown | ✓ VERIFIED | emitter -> reopen -> parse -> binding 校验已接通。 |
| `skills/graduate-resume/scripts/graduate_resume_layout.py` | 冻结布局、照片与字体门禁 | ✗ UNSAFE | 结构字段已恢复、显式 photo 已 fail-closed；照片只返回路径且 Typst 未验证版本。 |
| `skills/graduate-resume/scripts/graduate_resume_typst.py` | 机械、安全、受控版本发射 | ⚠ PARTIAL | 稳定 ID/文本边界已修复；照片规范化只检查命令存在性。 |
| `skills/graduate-resume/scripts/graduate_resume_render.py` | 三主题候选矩阵与 triples | ⚠ PARTIAL | final Markdown 重读、结构化内容、hidden evidence 可用；编译未锁 Typst 版本。 |
| `skills/graduate-resume/scripts/graduate_resume_delivery.py` | 干净 root、事务、history、rollback | ✗ UNSAFE | history/digest/rollback 已修复；仍接受 sources/assets，且清理错误全部吞掉。 |
| `skills/graduate-resume/scripts/graduate_resume_cli.py` | render/batch 编排与快照绑定 | ✗ UNSAFE | 四态与 reviewed digest 已接通；metadata、照片和 canonical 快照三条信任边界仍破裂。 |
| `skills/graduate-resume/scripts/test_phase48_cli.py` | Phase 48 固定验收矩阵 | ⚠ INSUFFICIENT | 53/53 Phase 48 相关测试通过，但五个 Critical 最小反例仍成功。 |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| canonical parser | publication fact view | 显式 verified 状态 | ✗ NOT_WIRED | parser 在状态缺失/拼错时自行补成 verified。 |
| target evaluator | public rows + hidden evidence | 同一 evaluation/digest | ✓ WIRED | CLI 同时持久化公开行与完整隐藏 evidence。 |
| renderer | final Markdown loader | write -> reopen -> parse -> validate | ✓ WIRED | `render_candidate_matrix` 使用重读模型。 |
| photo resolver | normalized photo bytes | 同一 no-follow 快照 | ✗ NOT_WIRED | resolver 返回路径，CLI 二次 path read。 |
| parsed canonical facts | canonical hash/approval | 同一 immutable bytes | ✗ NOT_WIRED | parse 与 hash 分两次路径读取。 |
| CLI | delivery transaction | patch/authority + reviewed digest | ✓ WIRED | `mode` 明确按 render/batch 选择，用户 digest 原样交给 publish；SDK regex 的 false negative 不改变代码证据。 |
| delivery transaction | delivery root discovery | exact allowlist | ✗ PARTIAL | managed triples/history/.work 可控，但 sources/assets 被无界放行。 |
| render/layout/typst | Typst executable | 精确 0.15.0 resolver | ✗ NOT_WIRED | 三个消费者没有共同版本门禁。 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| final Markdown/Typst/PDF | selected facts | parsed canonical -> publication view | malformed metadata 可提升为 verified | ✗ UNTRUSTED |
| condition public/evidence | `HardConditionEvaluation` | publication facts + target conditions | 公开/隐藏投影一致，但 evidence trust 可被状态提升破坏 | ⚠ PARTIAL |
| canonical binding | `canonical_hash` | publication 时重新读取 input path | 与先前解析事实可能不是同一 bytes | ✗ DISCONNECTED |
| normalized photo | `photo_bytes` | resolver 逻辑路径的二次读取 | 可跟随校验后替换的 symlink | ✗ UNTRUSTED |
| delivery current | triples + support directories | held root descriptor | triples 实质流动；sources/assets 内容未审计 | ✗ POLLUTABLE |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Phase 48 相关窄回归 | `python3 -m unittest test_targeting_contract.py test_render_contract.py test_delivery_transaction.py test_phase48_cli.py -v` | 53 tests, OK, 16.491s | ✓ PASS（覆盖不足） |
| graduate-resume 全量发现 | `python3 -m unittest discover -s skills/graduate-resume/scripts -p 'test_*.py' -q` | exit 0 | ✓ PASS（覆盖不足） |
| metadata 拼错/缺失/重复必须拒绝 | 临时改写 `valid-no-photo.md` 后 `load_resume` + `validate_document` | 三种输入均 `ACCEPTED verified passed` | ✗ FAIL |
| 照片校验后 symlink swap | resolve 后将 `photo.jpg` 替换为指向另一 JPEG 的 symlink，再执行 CLI 同构读取 | `followed_alternate=True` | ✗ FAIL |
| canonical 同快照绑定 | load 后改写原文件，再按发布路径计算 hash | parsed body 为旧内容，claimed hash 为新文件 | ✗ FAIL |
| delivery root 拒绝 sources/assets | 各放入 `private.txt` 后打开 `DeliverySession` | `sources_private=ACCEPTED`、`assets_private=ACCEPTED` | ✗ FAIL |
| Typst 精确版本门禁 | mock `which=/fake/typst-9.9` 且 fonts 返回预期文本 | fake 9.9 被接受，唯一调用为 `fonts` | ✗ FAIL |

### Probe Execution

Step 7c: SKIPPED。Phase 48 的 PLAN/SUMMARY 未声明 `probe-*.sh`，仓库也没有本阶段约定 probe。

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| TARGET-01 | 48-01, 48-02, 48-04, 48-05 | ✗ BLOCKED | 状态缺失/拼错/重复可提升为 verified，违反“只选已核实事实”。 |
| TARGET-02 | 48-01, 48-04, 48-06 | ✗ BLOCKED | 四态、公开行、hidden evidence 与 gap allow 均已实现，但其 verified evidence 前提可被 metadata 状态提升绕过。 |
| TARGET-03 | 48-01, 48-02, 48-04, 48-05 | ✓ SATISFIED | 最终 Markdown 记录实际主题/页数/照片/目标/source/as_of，生产路径无抓取或网络调用。 |
| DELIVERY-01 | 48-02, 48-04, 48-05 | ✓ SATISFIED | 三主题同 stem `.md/.typ/.pdf` 与正式命名由当前回归和实际编译覆盖。 |
| DELIVERY-02 | 48-03, 48-04, 48-06 | ✗ BLOCKED | 跨进程 reviewed digest 已实现；canonical 与照片在单进程内仍存在“校验/解析后重新读取”窗口，完整预检不成立。 |
| DELIVERY-03 | 48-03, 48-04, 48-06 | ✗ BLOCKED | no-op/history/rollback/unknown/symlink 主路径通过；sources/assets 污染被接受，cleanup 失败又无错误信号。 |

六个 Phase 48 requirement 均至少被一个 PLAN frontmatter 声明，无 orphaned requirement。Phase 49 仅明确承接 PDF 结构验证、聚合回归、六 runtime 和跨环境字体 UAT，没有承接上述生产实现缺口；无 deferred 项。

### Code Review Findings Re-check

| Finding | Independent Result | Classification | Evidence |
|---|---|---|---|
| CR-01 metadata 状态提升 | CONFIRMED | 🛑 BLOCKER | 拼错、缺失、重复 status 三个最小反例均通过。 |
| CR-02 照片 symlink TOCTOU | CONFIRMED | 🛑 BLOCKER | resolve 后 swap，二次读取跟随替代文件。 |
| CR-03 canonical hash 错绑 | CONFIRMED | 🛑 BLOCKER | 旧 parsed body 与新 claimed hash 可同时出现。 |
| CR-04 sources/assets 污染 | CONFIRMED | 🛑 BLOCKER | 两个私密文件目录均被 DeliverySession 接受。 |
| CR-05 Typst 版本未锁 | CONFIRMED | 🛑 BLOCKER | fake 9.9 通过字体门禁，代码无 `--version` 调用。 |
| WR-01 cleanup 错误吞掉 | CONFIRMED（静态） | ⚠ WARNING | `close()` 的 unlink/rmdir/close OSError 全部 `pass`，`__exit__` 不检查结果。 |

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| `graduate_resume_cli.py` | 221, 287 | 重复 metadata 覆盖 + verified 缺省 | 🛑 Blocker | 未核实事实可进入正式输出和资格判定。 |
| `graduate_resume_cli.py` | 665 | 校验后按路径二次读照片 | 🛑 Blocker | 可消费未经授权替代文件。 |
| `graduate_resume_cli.py` | 774 | 解析后重读 canonical 计算 hash | 🛑 Blocker | 可追溯绑定声明错误。 |
| `graduate_resume_delivery.py` | 18, 355 | sources/assets allowlist | 🛑 Blocker | 投递根可保留私密或中间资产。 |
| `graduate_resume_layout.py` | 442 | 只检查 typst 命令存在 | 🛑 Blocker | 不同版本可改变布局与 bytes。 |
| `graduate_resume_delivery.py` | 690-738 | 清理 OSError 全部吞掉 | ⚠ Warning | 成功后可遗留 stale `.work/.lock`，下一次运行才失败。 |

阶段生产文件未发现未引用的 `TBD`、`FIXME` 或 `XXX` 债务标记。

### Human Verification Required

无。五项阻断均由代码检查和无状态临时目录最小复现确定；视觉、跨 runtime 与跨环境字体 UAT 属于 Phase 49，不能替代本阶段失败判定。

### Gaps Summary

上一轮报告指出的信任边界、结构化内容、condition evidence、history 连续性和 reviewed digest 缺口已经关闭，现有回归也全部通过。但 Phase 48 目标仍未达成：解析器可把未复核事实提升为 verified，照片与 canonical 都没有把验证和消费绑定到同一快照，投递根允许 `sources/assets` 污染，声明锁定的 Typst 版本没有任何代码门禁。五项 Critical 均被独立复现，不能进入 Phase 49。

---

_Verified: 2026-07-18T13:56:41Z_
_Verifier: the agent (gsd-verifier)_
