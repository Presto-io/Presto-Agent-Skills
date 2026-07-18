---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
reviewed: 2026-07-18T19:19:35Z
depth: standard
files_reviewed: 20
files_reviewed_list:
  - skills/graduate-resume/SKILL.md
  - skills/graduate-resume/fixtures/render/targeted-photo.md
  - skills/graduate-resume/fixtures/targeting/multi-state-targets.md
  - skills/graduate-resume/references/targeted-render-delivery-contract.md
  - skills/graduate-resume/scripts/graduate_resume_cli.py
  - skills/graduate-resume/scripts/graduate_resume_delivery.py
  - skills/graduate-resume/scripts/graduate_resume_final_markdown.py
  - skills/graduate-resume/scripts/graduate_resume_layout.py
  - skills/graduate-resume/scripts/graduate_resume_render.py
  - skills/graduate-resume/scripts/graduate_resume_targeting.py
  - skills/graduate-resume/scripts/graduate_resume_typst.py
  - skills/graduate-resume/scripts/graduate_resume_typst_runtime.py
  - skills/graduate-resume/scripts/test_delivery_transaction.py
  - skills/graduate-resume/scripts/test_phase48_cli.py
  - skills/graduate-resume/scripts/test_render_contract.py
  - skills/graduate-resume/scripts/test_targeting_contract.py
  - skills/graduate-resume/scripts/test_theme_contract.py
  - skills/graduate-resume/templates/graduate-resume.md
  - skills/graduate-resume/templates/resume-themes.typ
  - skills/graduate-resume/templates/targeting-policy.json
findings:
  critical: 4
  warning: 0
  info: 0
  total: 4
status: issues_found
---

# Phase 48: Code Review Report

**Reviewed:** 2026-07-18T19:19:35Z
**Depth:** standard
**Files Reviewed:** 20
**Status:** issues_found

## Summary

本次独立复审确认：原 CR-03、CR-04 与 WR-01..WR-04 已按公开 CLI 路径关闭；CR-01、CR-02、CR-05、CR-06 的修复仍有可证明的绕过或原子性缺口。新增/未关闭 BLOCKER 共 4 项，WARNING 为 0。

已执行的针对性测试均通过：重复字段、带 scheme 的 URL、嵌套不可渲染值、Typst 同 inode 覆写前校验，以及定向证据正常持久化。最小复现同时证实 `safe_component("张三010-12345678")` 仍返回含电话号码的 stem；将 target 来源改为 `www.jobs.example.test/private?id=123` 后，`validate_document()` 返回 `passed`。

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: 裸域名招聘 URL 仍可写入正式 Markdown

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_cli.py:515`
**Related:** `skills/graduate-resume/scripts/graduate_resume_final_markdown.py:136`
**Issue:** 修复仅拒绝以 `scheme://` 开头的 `source`。招聘链接常以 `www.jobs.example.test/private?id=123` 或 `jobs.example.test/path` 形式提供；这些值不是纯来源描述，却会通过校验，并由最终 Markdown 的 target metadata 原样发布。复现已确认前一种裸域名形式校验通过，故 CR-01 未真实关闭。
**Fix:** 用结构化 URL/域名检测覆盖 scheme URL、`www.`、域名加路径或查询串，并只允许受限的来源类别文本。投影前再次断言 source 不符合 URL/域名模式。

```python
SOURCE_URL_RE = re.compile(
    r"(?i)^(?:[a-z][a-z0-9+.-]*://|www\\.|(?:[a-z0-9-]+\\.)+[a-z]{2,}(?:[/?#].*)?$)"
)
if SOURCE_URL_RE.match(source.strip()):
    issues.append(f"{area}.source 必须是来源描述，不能是 URL。")
```

### CR-02: stem 敏感信息检测仍遗漏座机和旧版身份证号

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_render.py:239`
**Issue:** `_PHONE_RE` 仅匹配中国大陆 11 位移动号码，`_ID_CARD_RE` 仅匹配 18 位身份证号。复现 `safe_component("张三010-12345678")` 返回原始电话号码；同类座机、国际号码和 15 位旧版身份证均可由姓名、单位或岗位进入 delivery/history 路径。这违反 D-15 和 `SKILL.md` 的“不得把电话、邮箱、身份证写入输出 stem”边界，故 CR-02 未真实关闭。
**Fix:** 使用覆盖实际允许资料地域的集中敏感标识策略，至少拒绝中国座机、国际 E.164 形式和 15/18 位身份证；更稳妥的是把 profile/contact 中的敏感字段与 stem 组件隔离，并对所有组件加入这些负例。

```python
PHONE_RE = re.compile(r"(?<!\\d)(?:\\+?\\d{1,3}[- ]?)?(?:1[3-9]\\d{9}|0\\d{2,3}[- ]?\\d{7,8})(?!\\d)")
ID_CARD_RE = re.compile(r"(?<!\\d)(?:\\d{15}|\\d{17}[0-9Xx])(?!\\d)")
```

### CR-03: 证据持久化失败发生在 delivery 提交之后，无法回滚正式产物

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_cli.py:955`
**Related:** `skills/graduate-resume/scripts/graduate_resume_delivery.py:685`
**Issue:** `session.publish()` 已将 current/history 提交并清除 `_mutation_started`，随后才循环调用 `evidence_sink.persist()`。若证据根在两者之间被替换、磁盘写满、`os.rename`/`fsync` 失败或第二个 target 的证据冲突，CLI 会失败，但 `DeliverySession.__exit__()` 不会调用 `_rollback()`，留下已更新的正式 triple 与缺失/部分隐藏证据。该状态既违反 D-06 的审计绑定，也违反 D-17“任一 handled failure 保持整个原 current path set 与 bytes”；现有测试只覆盖成功持久化，未覆盖此顺序。
**Fix:** 在提交前把证据写入 DeliverySession 持有的工作树，或让 publish 接受并原子处理 evidence payload；只有 current/history 与所有 evidence 均成功 fsync 后才提交。任何 evidence 写入或身份检查失败都必须走同一 rollback 路径，并加入“第二份 evidence persist 抛错时 current/history/evidence 均回到原快照”的回归测试。

### CR-04: Typst 快照仍存在校验到执行之间的可替换竞态

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_typst_runtime.py:123`
**Issue:** 本次修复在 `run()` 中复验 inode、mode、size 和 SHA-256，但第 130 行仍以路径交给 `subprocess.run()` 执行。攻击者只需在第 123-129 行检查完成后、子进程 exec 前原地 chmod/覆写该同 inode 快照，即可绕过复验并执行替换内容。快照根由同一用户持有，原 CR-06 所述的本地同用户篡改威胁模型仍成立；现有测试只覆盖“覆写发生在 run 调用之前”，没有覆盖 TOCTOU 窗口。
**Fix:** 在支持的平台使用已持有的可执行文件描述符（例如 `fexecve`）执行，避免按路径二次解析；若必须经路径执行，则把快照置入攻击者无法写入的隔离权限域，并将身份校验和 exec 放到不可由同用户替换的受控 helper 中。新增同步钩子测试，在 hash 校验完成后替换快照并断言绝不执行替换程序。

---

_Reviewed: 2026-07-18T19:19:35Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
