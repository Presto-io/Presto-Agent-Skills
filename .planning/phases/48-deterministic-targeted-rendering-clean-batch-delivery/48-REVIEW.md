---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
reviewed: 2026-07-18T07:39:39Z
depth: standard
files_reviewed: 17
files_reviewed_list:
  - skills/graduate-resume/templates/targeting-policy.json
  - skills/graduate-resume/scripts/graduate_resume_targeting.py
  - skills/graduate-resume/scripts/test_targeting_contract.py
  - skills/graduate-resume/fixtures/targeting/multi-state-targets.md
  - skills/graduate-resume/scripts/graduate_resume_final_markdown.py
  - skills/graduate-resume/scripts/graduate_resume_render.py
  - skills/graduate-resume/scripts/test_render_contract.py
  - skills/graduate-resume/fixtures/render/targeted-photo.md
  - skills/graduate-resume/scripts/graduate_resume_layout.py
  - skills/graduate-resume/scripts/graduate_resume_typst.py
  - skills/graduate-resume/scripts/graduate_resume_delivery.py
  - skills/graduate-resume/scripts/test_delivery_transaction.py
  - skills/graduate-resume/scripts/test_phase48_cli.py
  - skills/graduate-resume/references/targeted-render-delivery-contract.md
  - skills/graduate-resume/scripts/graduate_resume_cli.py
  - skills/graduate-resume/SKILL.md
  - skills/graduate-resume/templates/graduate-resume.md
findings:
  critical: 6
  warning: 2
  info: 0
  total: 8
status: issues_found
---

# Phase 48: Code Review Report

**Reviewed:** 2026-07-18T07:39:39Z
**Depth:** standard
**Files Reviewed:** 17
**Status:** issues_found

## Summary

本次审查发现 6 个阻断发布的正确性/安全/数据安全问题，以及 2 个审计与公开契约偏差。最严重的问题包括：`declined` 事实会进入正式简历、Typst/PDF 丢失联系方式和技能/成果列表、事实 ID 可突破 Markdown→Typst 信任边界、authority 删除历史会让后续所有发布无法启动，以及 `--confirm` 没有绑定用户实际看过的预检摘要。

现有 37 个 Phase 48 测试全部通过，但下列最小复现仍成立，说明测试覆盖未触达这些边界。

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: `declined` 事实被当作可发布事实

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_cli.py:345`
**Issue:** `validate_candidate` 和 `validate_entry_list` 只阻断 `pending`，却允许 `declined` 通过。后续 targeting 会枚举所有条目，不再检查状态，因此候选人明确拒绝使用的个人信息或经历会进入最终 Markdown/Typst/PDF。这直接违反契约“只消费 `status: verified`”并存在隐私泄露风险。最小复现中 candidate 与 education 均为 `declined` 时，`validate_document()` 仍返回 `passed`。
**Fix:** final render 校验应只接受 `verified`；若 `declined` 需要保留在 canonical 源中，应在投影前显式过滤且不得进入 known/selected facts。

```python
if candidate.get("status") != "verified":
    issues.append("candidate.status 必须为 verified，才能进入 final render。")

if entry.get("status") != "verified":
    issues.append(f"{area}.status 必须为 verified，才能进入 final render。")
```

### CR-02: Typst/PDF 静默丢失联系方式与列表型核心内容

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_layout.py:209`
**Issue:** `project_containers` 只把字符串字段加入 `ContainerPlan.fields`。因此 profile 中的 `contact` 映射和 `directions` 列表被丢弃，skills 的 `items`、projects 的 `outcomes/tools`、education 的 `courses/honors` 等列表也不进入 `_container_text()`。最终 Markdown 虽保存完整 JSON，但正式 Typst/PDF 会静默缺少电话号码、邮箱、专业技能和项目成果等简历核心内容。模板复现中 profile 仅剩 name/status/headline/summary，skills 仅剩 group，projects 仅剩 title/role。
**Fix:** 建立受控的 section/field 展示序列化器，递归处理允许的映射和字符串列表，并让测量与发射消费同一规范化文本；添加断言确保最终 Typst 包含 contact、items、outcomes、tools 等字段。

```python
def display_value(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, list) and all(isinstance(item, str) for item in value):
        return "；".join(item.strip() for item in value if item.strip()) or None
    if isinstance(value, Mapping):
        parts = [f"{key}: {shown}" for key, item in value.items() if (shown := display_value(item))]
        return "；".join(parts) or None
    return None
```

### CR-03: 未校验事实 ID 可注入任意 Typst 代码

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_typst.py:93`
**Issue:** `container.id` 被直接插入 Typst 双引号字符串，而 canonical 事实 ID 在 `validate_entry_list` 中只校验“非空”和重复，不应用 `_STABLE_ID_RE`。攻击者可在 Markdown 元数据中放入引号、括号和 `#`，突破字符串边界。最小复现 ID `x");#panic("injected");#("` 会生成 `#list-entry("projects", "x");#panic("injected");#("", ...)`。这至少可稳定破坏渲染，并允许候选输入执行受 Typst 能力边界约束的任意表达式。
**Fix:** 在 canonical 解析/校验边界对所有事实 ID 和 target ID 使用严格、统一的稳定 ID grammar；Typst 发射端仍应对 `container.id` 调用专用字符串转义，形成纵深防御。

```python
if not isinstance(entry_id, str) or _STABLE_ID_RE.fullmatch(entry_id) is None:
    issues.append(f"{area}.id 必须使用稳定 ID grammar。")

safe_id = typst_string(container.id)
body.append(f'#list-entry("{heading}", "{safe_id}", [{content}], show-heading: {show_heading})')
```

### CR-04: authority 删除目标后，历史目录会永久阻断后续发布

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_delivery.py:273`
**Issue:** `_inspect_history` 要求历史中的每个 stem 仍属于本次 `spec.safe_stems`。但 CLI 的 safe stems 只由本次 planned stems 与当前平铺文件发现得到；authority 删除的 stem 只剩在 history，下一次运行不会再进入 safe stems。结果是第一次删除成功并归档后，下一次相同 batch 在打开 session 时失败：`history contains an unknown stem`。这破坏了 history、no-op 和连续发布语义。
**Fix:** 历史 stem 应按独立的安全 stem grammar、主题后缀和完整 triple 结构验证，而不是要求仍在当前权威集合；或者以 no-follow 方式安全发现并显式纳入历史 registry，但不得让历史内容重新影响 current authority 集合。

### CR-05: `--confirm` 未绑定用户实际审阅过的 authority 预检

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_cli.py:754`
**Issue:** 预检命令输出 `approval_digest`，但 CLI 没有参数让确认命令提交这个 digest。追加 `--confirm` 后，程序在新进程中重新计算当前 snapshot/delta，并把刚计算出的 digest直接传给 `publish()`。因此预检与确认之间若 current 新增或变化，authority 确认会自动批准一组用户从未看过的 removals/updates，存在覆盖或删除正式三件套的数据损失风险。`DeliverySession.publish()` 的二次 preflight 只能防住同一进程内的 TOCTOU，不能绑定跨命令的人类确认边界。
**Fix:** 增加必填的 `--approval-digest <digest>`（至少 authority `--confirm` 必填），只接受上一轮预检输出的值；确认命令重算后必须与用户提交的 digest 相等，否则要求重新预检。文档示例也应改为显式携带 digest。

### CR-06: 显式 `--photo-mode photo` 在无照片输入上被静默降级

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_layout.py:374`
**Issue:** `resolve_layout_photo` 看到 canonical `photo.status == "no-photo"` 就直接返回 `None`，即使调用者显式传入 `photo_mode=photo`。CLI 随后把结果改写为 `photo_mode: no-photo` 并成功预检，而不是用稳定错误码拒绝不可能满足的显式请求。用户要求照片版却得到无照片版，公开参数语义不可信。
**Fix:** 当请求模式为 `photo` 且没有 provided path 时抛出 `PHOTO_ASSET_INVALID`；只有 `auto` 才允许根据事实自动降级为 no-photo。

```python
requested = preferences.get("photo_mode")
if requested == "photo" and photo.get("status") != "provided":
    raise _photo_error()
if requested == "no-photo" or photo.get("status") == "no-photo":
    return None
```

## Warnings

### WR-01: 单目标 render 预检丢弃逐条件四态详情

**Classification:** WARNING
**File:** `skills/graduate-resume/scripts/graduate_resume_cli.py:777`
**Issue:** 代码已经在 `condition_public` 中构建每条 condition 的 ID、predicate 和 state，但非 batch 分支只输出 counts 与 warning ID，丢弃 `conditions` 数组。这与 `SKILL.md` 和 D-06/D-16 所述“逐条件四态”预检不一致，也削弱了用户在确认单目标发布前的可审阅性。
**Fix:** render 与 batch 使用同一有界 condition public projection；单目标 payload 应包含 `condition_public[target_id]`，同时继续排除 reason 与 evidence fact IDs。

### WR-02: 契约承诺的 owned hidden evidence 实际未保存

**Classification:** WARNING
**File:** `skills/graduate-resume/scripts/graduate_resume_render.py:146`
**Issue:** D-06 声称完整 condition reason 与 evidence fact IDs 写入 owned hidden evidence，但渲染 evidence 只保存 `VersionProjection` 和主题页数；CLI 计算的 `HardConditionEvaluation` 也只用于公开摘要，没有调用或持久化 `to_evidence_projection()`。此外该 evidence 位于命令临时目录并在命令结束时销毁。结果是 condition digest 没有可审计的对应证据，文档与实现漂移。
**Fix:** 将每个目标的 `to_evidence_projection()` 传入候选矩阵，在 owned `.work/.../evidence` 中保存并在事务成功/失败策略下明确管理；不得发布到 delivery root。若 Phase 48 不要求持久审计，则应删除文档中的该承诺并明确 evidence 仅为进程内验证。

---

_Reviewed: 2026-07-18T07:39:39Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
