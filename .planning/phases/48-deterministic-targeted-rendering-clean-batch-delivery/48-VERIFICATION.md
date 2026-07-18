---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
verified: 2026-07-18T07:50:21Z
status: gaps_found
score: 1/5 must-haves verified
overrides_applied: 0
gaps:
  - truth: "用户只能从已核实事实生成通用版和定向版，事实 ID 不能突破最终 Markdown 到 Typst 的信任边界。"
    status: failed
    reason: "final render 校验仅拒绝 pending，declined 事实仍通过；事实 ID 仅检查非空和重复，恶意 ID 可进入 Typst 字符串并注入表达式。"
    artifacts:
      - path: "skills/graduate-resume/scripts/graduate_resume_cli.py"
        issue: "candidate 与条目 status=declined 可通过 validate_document；事实 ID 未应用稳定 ID grammar。"
      - path: "skills/graduate-resume/scripts/graduate_resume_typst.py"
        issue: "container.id 未经 Typst 字符串转义直接拼接到 list-entry 调用。"
    missing:
      - "final render 边界只接受 status=verified，或在投影前可靠过滤 declined。"
      - "对所有事实 ID 应用统一稳定 ID grammar，并在 Typst emitter 再次转义。"
      - "新增 declined 与恶意 ID 的端到端负例。"
  - truth: "每个版本的 Markdown、Typst、PDF 三件套都保留所选事实的实质内容。"
    status: failed
    reason: "最终 Markdown 保存完整事实，但布局只投影字符串字段，联系方式映射及 skills/items、projects/outcomes/tools 等列表不会流入 Typst/PDF。"
    artifacts:
      - path: "skills/graduate-resume/scripts/graduate_resume_layout.py"
        issue: "project_containers 只保留 isinstance(value, str) 的字段，动态数据流为空洞。"
      - path: "skills/graduate-resume/scripts/graduate_resume_typst.py"
        issue: "emit_typst 只消费已被裁空的 container.fields。"
    missing:
      - "为允许的映射和字符串列表建立受控展示序列化器。"
      - "让布局测量与 Typst 发射消费同一规范化文本。"
      - "断言联系方式、技能项、项目成果和工具真实出现在 Typst/PDF。"
  - truth: "用户在单份和批量预检中都能查看每条硬条件的四态结果，并可追溯到受保护证据。"
    status: failed
    reason: "batch 输出逐条件行，但单目标 render 只输出四态计数；文档承诺的完整 condition evidence 未持久化，临时 evidence 也只保存 VersionProjection 和主题页数。"
    artifacts:
      - path: "skills/graduate-resume/scripts/graduate_resume_cli.py"
        issue: "非 batch 分支丢弃 condition_public 中的 conditions 数组。"
      - path: "skills/graduate-resume/scripts/graduate_resume_render.py"
        issue: "未保存 HardConditionEvaluation.to_evidence_projection()，condition digest 无对应审计证据。"
    missing:
      - "render 与 batch 使用同一有界逐条件公开投影。"
      - "保存 digest 绑定的完整隐藏条件证据，或收缩文档承诺并明确审计边界。"
  - truth: "批量发布的预检确认、完整 history、连续 no-op、rollback 与 fail-closed 语义在后续运行中持续成立。"
    status: failed
    reason: "authority 删除目标并归档后，下一次运行因历史 stem 不在当前 safe_stems 而永久失败；CLI 的 --confirm 不接受上一轮 approval_digest，而是在新进程中重算并自动使用新 digest，未绑定用户实际审阅的预检。"
    artifacts:
      - path: "skills/graduate-resume/scripts/graduate_resume_delivery.py"
        issue: "_inspect_history 要求历史 stem 仍属于当前 authority safe_stems。"
      - path: "skills/graduate-resume/scripts/graduate_resume_cli.py"
        issue: "无 --approval-digest 参数，确认时直接传入本次新计算的 delta.approval_digest。"
    missing:
      - "历史 stem 应按独立安全 grammar 和完整 triple 验证，不依赖当前 authority 集合。"
      - "authority 确认必须提交并校验用户上一轮看到的 approval digest。"
      - "新增目标删除后再次相同 batch/no-op，以及预检后 current 变化的跨进程回归。"
  - truth: "显式照片模式请求若无法满足必须失败关闭，不能静默改成另一种正式版本。"
    status: failed
    reason: "--photo-mode photo 配合 no-photo canonical 输入返回成功预检，并将输出改写为 photo_mode=no-photo。"
    artifacts:
      - path: "skills/graduate-resume/scripts/graduate_resume_layout.py"
        issue: "resolve_layout_photo 在检查显式 photo 请求前先因 photo.status=no-photo 返回 None。"
    missing:
      - "显式 photo 请求缺少 provided 路径时返回 PHOTO_ASSET_INVALID；仅 auto 可降级。"
      - "新增公开 CLI 负例，断言 current/history 不变。"
---

# Phase 48: 确定性定向渲染与干净批量交付 Verification Report

**Phase Goal:** 用户能离线生成通用版及多个透明、可追溯的定向简历三件套，并在失败时保持当前成功交付。
**Verified:** 2026-07-18T07:50:21Z
**Status:** gaps_found
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Roadmap Success Criterion | Status | Evidence |
|---|---|---|---|
| 1 | 同一已核实资料生成通用版及每个单位+岗位的定向版，且只选择、排序或强调已核实事实 | ✗ FAILED | `declined` 事实仍通过 final render 校验；恶意事实 ID 可进入 Typst；Typst/PDF 又丢失列表型已选事实。 |
| 2 | 用户可查看硬条件四态；gap 可明确放行且简历不暗示满足 | ✗ FAILED | 四态判定与逐目标 gap gate 本身通过测试，但单目标 `render` 只公开 counts，不公开逐条件状态；隐藏证据承诺未实现。 |
| 3 | 每个版本记录实际主题、页数、照片模式、目标及来源/日期，且不抓取或猜测招聘信息 | ✓ VERIFIED | 最终 Markdown schema 写入 theme/page/photo/target/source/as_of，目标策略为离线本地数据；未发现网络调用。显式照片请求静默降级另列阻断 gap。 |
| 4 | 每个成功版本同 stem 输出正式命名的 Markdown、Typst、PDF 三件套，投递根保持干净 | ✗ FAILED | 命名、三主题、三后缀和干净根可生成，但 Typst/PDF 丢失联系方式、技能和项目列表，动态交付物为 HOLLOW，不能视为完整简历三件套。 |
| 5 | 单份/批量完整预检，失败零部分发布，并保持 candidate-first、no-op、history、rollback、unknown/symlink fail-closed | ✗ FAILED | candidate-first、故障回滚、unknown/symlink、单次 no-op 测试通过；但目标删除后的 history 阻断所有后续运行，且跨命令确认未绑定用户审阅 digest。 |

**Score:** 1/5 roadmap must-haves verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|---|---|---|---|
| `skills/graduate-resume/templates/targeting-policy.json` | 冻结离线定向策略 | ✓ VERIFIED | 存在、字段受控、原始 bytes SHA-256 绑定。 |
| `skills/graduate-resume/scripts/graduate_resume_targeting.py` | 稳定投影、四态条件、gap gate | ⚠ PARTIAL | resolver 和四态逻辑实质存在；其“verified facts”前置保证被 CLI validator 的 declined 漏洞破坏。 |
| `skills/graduate-resume/scripts/graduate_resume_final_markdown.py` | 可重读、绑定完整的最终 Markdown | ✓ VERIFIED | emitter → reopen → parse → binding 校验已接通。 |
| `skills/graduate-resume/scripts/graduate_resume_render.py` | 三主题候选矩阵与完整 triples | ⚠ HOLLOW | 三主题矩阵、final Markdown 重读和 Typst 编译已接通，但隐藏条件 evidence 未写入，且下游布局丢失动态字段。 |
| `skills/graduate-resume/scripts/graduate_resume_layout.py` | 所选事实的冻结布局 | ✗ HOLLOW | 只投影字符串字段，映射/列表内容被静默裁掉；显式 photo 请求可降级。 |
| `skills/graduate-resume/scripts/graduate_resume_typst.py` | 机械消费重读模型并安全发射 Typst | ✗ UNSAFE | 消费重读模型成立，但 `container.id` 未转义，且输入字段已被布局裁空。 |
| `skills/graduate-resume/scripts/graduate_resume_delivery.py` | 动态 triple 事务、history、rollback | ⚠ PARTIAL | candidate-first、no-op、rollback、unknown/symlink gate 可用；authority 删除后的历史连续运行失败。 |
| `skills/graduate-resume/scripts/graduate_resume_cli.py` | render/batch 公开编排与确认 | ⚠ PARTIAL | generic/target/batch、三主题与 delta 已接通；单 target 四态、approval digest 绑定和 verified-only 校验不完整。 |
| `skills/graduate-resume/scripts/test_phase48_cli.py` | Phase 48 固定验收矩阵 | ⚠ INSUFFICIENT | 37/37 阶段测试与 56/56全量测试通过，但未覆盖本报告的最小反例。 |

### Key Link Verification

| From | To | Via | Status | Details |
|---|---|---|---|---|
| target resolver | targeting policy | 严格字段、version、SHA-256 | ✓ WIRED | `verify.key-links` 通过。 |
| canonical validator | verified fact resolver | final render 前置校验 | ✗ NOT_WIRED | validator 接受 `declined` 和任意非空事实 ID，无法提供“只含 verified facts”的可信输入。 |
| renderer | final Markdown loader | 写入后 reopen/parse/validate | ✓ WIRED | `emit_final_markdown` 后立即 `load_final_resume`。 |
| final Markdown fact view | frozen layout | selected facts → containers | ✗ HOLLOW | 数据链路存在，但只保留字符串字段，映射/列表不流动。 |
| frozen layout | Typst emitter | container fields 与 IDs | ✗ UNSAFE | 内容不完整，ID 未进行 Typst 字符串转义。 |
| CLI | delivery transaction | patch/authority preflight → publish | ⚠ PARTIAL | 模式选择与事务调用存在，但确认 digest 由确认进程自行重算。 |
| delivery transaction | history | 归档完整旧 triples | ✗ BROKEN | 旧目标归档成功后，下一 session 把该历史 stem 判为 unknown。 |

### Data-Flow Trace (Level 4)

| Artifact | Data Variable | Source | Produces Real Data | Status |
|---|---|---|---|---|
| final Markdown | selected facts | canonical facts + VersionProjection | Yes，正文 JSON 完整 | ✓ FLOWING |
| frozen layout | `ContainerPlan.fields` | `FinalResumeDocument.fact_view()` | 仅字符串；contact/items/outcomes/tools 丢失 | ✗ HOLLOW |
| Typst/PDF | `_container_text(container)` | `ContainerPlan.fields` | 消费的是已裁空字段 | ✗ HOLLOW |
| condition evidence | `condition_digest` | `HardConditionEvaluation.matrix` | digest 有值，但完整 evidence 未传入/持久化 | ✗ DISCONNECTED |
| publication confirmation | `approval_digest` | 当前进程 `session.preflight()` | 真实 delta，但不是用户上一轮提交的 digest | ✗ UNBOUND |

### Behavioral Spot-Checks

| Behavior | Command | Result | Status |
|---|---|---|---|
| Phase 48 窄回归 | `python3 -m unittest ...test_phase48_cli.py -v` | 37 tests, OK | ✓ PASS（覆盖不足） |
| graduate-resume 全量回归 | `python3 -m unittest discover -s skills/graduate-resume/scripts -p 'test_*.py' -v` | 56 tests, OK | ✓ PASS（覆盖不足） |
| declined 必须拒绝 | 将 fixture 的 candidate/education 改为 `declined` 后调用 `validate_document` | 返回 `status: passed` | ✗ FAIL |
| 列表/联系方式流入布局 | 对 author template 调用 `project_containers` | profile 无 contact；skills 仅 group；projects 仅 title/role | ✗ FAIL |
| 事实 ID 不得注入 Typst | 使用 ID `x\");#panic(\"injected\");#(\"` 完成 final Markdown 重读并 emit Typst | 输出包含 `#panic("injected")` | ✗ FAIL |
| authority 删除后可继续运行 | 发布旧目标 → authority 删除归档 → 新 session | `DeliveryError: history contains an unknown stem` | ✗ FAIL |
| 显式 photo 无资产必须失败 | `render ... --photo-mode photo` 使用 no-photo fixture | exit 0，payload 为 `photo_mode: no-photo` | ✗ FAIL |
| 单目标显示逐条件四态 | target render + not-applicable | 仅返回 counts，无 condition rows | ✗ FAIL |
| 确认绑定已审阅 digest | 检查 `render/batch --help` 与确认路径 | 仅 `--confirm`；无 approval digest 输入 | ✗ FAIL |

### Probe Execution

Step 7c: SKIPPED（Phase 48 PLAN/SUMMARY 未声明 `probe-*.sh`，仓库中无本阶段约定 probe）。

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| TARGET-01 | 48-01, 48-02, 48-04 | ✗ BLOCKED | declined 可发布、恶意事实 ID 可注入、Typst/PDF 丢失已选事实。 |
| TARGET-02 | 48-01, 48-04 | ✗ BLOCKED | 四态算法与 gap allow 可用，但单目标不透明且完整 evidence 未落地。 |
| TARGET-03 | 48-01, 48-02, 48-04 | ✓ SATISFIED | 最终 Markdown 记录实际主题/页数/照片/目标/source/as_of；未发现抓取或实时声明。 |
| DELIVERY-01 | 48-02, 48-04 | ✗ BLOCKED | stem、命名和 triple 集合正确，但 Typst/PDF 实质内容不完整。 |
| DELIVERY-02 | 48-03, 48-04 | ✗ BLOCKED | 候选矩阵失败零发布通过；但 authority 确认不绑定用户审阅的跨命令预检，不能称为完整预检确认。 |
| DELIVERY-03 | 48-03, 48-04 | ✗ BLOCKED | rollback/no-op/fail-closed 部分通过；完整 history 会阻断后续 publication。 |

无 orphaned requirement：六个 Phase 48 requirement 均被计划声明并映射一次；Phase 49 只覆盖 VERIFY-01..04，不明确承接上述正确性缺口，因此没有项目可延期过滤。

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|---|---:|---|---|---|
| `skills/graduate-resume/scripts/graduate_resume_cli.py` | 345 | 只拒绝 pending | 🛑 Blocker | declined 私密/拒绝事实可进入正式投递。 |
| `skills/graduate-resume/scripts/graduate_resume_layout.py` | 209 | 只接收字符串字段 | 🛑 Blocker | 核心简历内容在 Typst/PDF 中静默丢失。 |
| `skills/graduate-resume/scripts/graduate_resume_typst.py` | 93 | 未转义的 candidate-controlled ID | 🛑 Blocker | Typst 注入/稳定渲染破坏。 |
| `skills/graduate-resume/scripts/graduate_resume_delivery.py` | 273 | history 依赖当前 safe_stems | 🛑 Blocker | 删除目标后所有后续发布无法启动。 |
| `skills/graduate-resume/scripts/graduate_resume_cli.py` | 754 | confirm 使用本次自动重算 digest | 🛑 Blocker | 用户确认可能批准未审阅的更新/删除。 |
| `skills/graduate-resume/scripts/graduate_resume_layout.py` | 374 | 显式 photo 静默降级 | 🛑 Blocker | 用户请求与实际交付不一致。 |
| `skills/graduate-resume/scripts/graduate_resume_cli.py` | 777 | 单目标只输出 counts | ⚠ Warning | 逐条件四态不可审阅。 |
| `skills/graduate-resume/scripts/graduate_resume_render.py` | 146 | condition evidence 未保存 | ⚠ Warning | digest 缺少可审计对应证据，文档漂移。 |

阶段修改文件未发现未引用的 `TBD`、`FIXME` 或 `XXX` 债务标记。

### Human Verification Required

无。当前失败均由代码检查和最小复现确定，不需要以人工 UAT 替代判定；视觉、跨环境字体和六 runtime 验收属于 Phase 49。

### Gaps Summary

Phase 48 已搭出完整的离线命令、三主题矩阵、最终 Markdown 重读、候选优先事务和大部分 fail-closed 骨架，但目标尚未达成。阻断点不是“文件不存在”，而是可信数据边界和连续发布语义失效：拒绝事实可发布、核心内容在 Typst/PDF 中丢失、事实 ID 可注入、历史阻断后续批次、确认未绑定用户审阅摘要。现有 56 项测试全部通过，却没有覆盖这些反例，不能据此接受阶段。

---

_Verified: 2026-07-18T07:50:21Z_
_Verifier: the agent (gsd-verifier)_
