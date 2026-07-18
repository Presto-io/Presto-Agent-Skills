---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
reviewed: 2026-07-18T13:42:57Z
depth: standard
files_reviewed: 18
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
  - skills/graduate-resume/scripts/test_delivery_transaction.py
  - skills/graduate-resume/scripts/test_phase48_cli.py
  - skills/graduate-resume/scripts/test_render_contract.py
  - skills/graduate-resume/scripts/test_targeting_contract.py
  - skills/graduate-resume/templates/graduate-resume.md
  - skills/graduate-resume/templates/resume-themes.typ
  - skills/graduate-resume/templates/targeting-policy.json
findings:
  critical: 5
  warning: 1
  info: 0
  total: 6
status: issues_found
---

# Phase 48: Code Review Report

**Reviewed:** 2026-07-18T13:42:57Z
**Depth:** standard
**Files Reviewed:** 18
**Status:** issues_found

## Summary

本次审查发现 5 个阻断发布的正确性、安全与交付契约问题，以及 1 个会破坏后续交付可用性的清理问题。最严重的缺陷会把拼错或省略复核状态的事实自动提升为 `verified`，允许照片资产在验证后被符号链接替换，以及把旧解析事实绑定到后来重新读取的 canonical hash。

范围内 53 个测试全部通过，但最小复现仍确认：`stats=pending` 会被解析为 `status=verified` 并通过校验；含私密文件的 `sources/` 会被正式投递事务接受；照片验证后替换为 symlink 时后续读取会跟随链接。现有测试只覆盖跨进程内容变化和初始 symlink，没有覆盖验证与消费之间的替换窗口。

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: 缺失或拼错的事实状态被自动提升为 `verified`

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_cli.py:217`
**Issue:** `parse_metadata()` 接受任意键且不拒绝重复键；正文条目随后用 `metadata.get("status", "verified")` 填充状态。因而 `<!-- resume: id=edu-001 stats=pending -->` 或完全省略 `status` 都会静默变成 `verified`，通过 `validate_document()`，并进入 Phase 48 正式 Markdown/Typst/PDF。这个默认值把未复核事实提升为已核实事实，直接违反 D-01 的“只消费 `status: verified`”边界。现有测试只覆盖显式 `status=pending/declined`，没有覆盖缺失、拼写错误或重复 metadata key。
**Fix:** `parse_metadata()` 必须拒绝重复 key；非 target 条目必须精确包含 `id` 与 `status`，target 必须只包含 `id`。不要为复核状态提供 `verified` 默认值，并添加缺失/拼错/重复 `status` 的 CLI 负例。

```python
if key in values:
    raise CliError("MARKDOWN_INVALID", f"{area} 的 resume 元数据键重复: {key}")
values[key] = value

if pending_area[0] != "targets" and set(metadata) != {"id", "status"}:
    raise CliError("MARKDOWN_INVALID", "正文事实必须显式提供 id 与 status。")
```

### CR-02: 照片通过 no-follow 校验后又按路径读取，重新开放 symlink TOCTOU

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_cli.py:665`
**Related:** `skills/graduate-resume/scripts/graduate_resume_layout.py:478`
**Issue:** `resolve_layout_photo()` 逐组件检查 symlink、文件类型和图片 magic 后只返回逻辑路径；CLI 随后重新执行 `(assets_root.resolve(...) / logical_path).read_bytes()`。验证与读取之间若文件被替换为 symlink，第二次读取会跟随链接并消费未授权的替代图片。最小复现已确认：校验返回后把 `photo.jpg` 换成指向另一 JPEG 的 symlink，行 665 会读取链接目标。静态 symlink 测试无法覆盖该窗口。
**Fix:** 在 `assets_root` 的 held directory descriptor 下逐组件使用 `O_NOFOLLOW` 打开最终文件，校验并从同一个 descriptor 读取有界 bytes；让 resolver 返回已验证 bytes（或 held fd），禁止调用者再按路径打开。增加校验后执行 inode/symlink swap 的回归测试。

### CR-03: canonical hash 可能绑定到与实际渲染事实不同的文件版本

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_cli.py:774`
**Related:** `skills/graduate-resume/scripts/graduate_resume_cli.py:184`
**Issue:** `load_resume()` 在行 184 读取并解析输入，但 `ResumeDocument` 不保存原始 bytes/hash；完成校验、目标投影和布局反馈后，行 774 再次从路径读取文件计算 `canonical_hash`。若输入在两次读取之间变化，最终三件套会使用旧解析事实，却声明绑定新文件的 SHA-256，审批摘要也会认证这个错误绑定。D-02/D-12 所要求的 canonical 可追溯性因此失效，且现有“预检后改文件”测试只覆盖两个独立进程，未覆盖单进程内两次读取。
**Fix:** 一次 no-follow、有界读取输入后，将原始 bytes 和 SHA-256 保存在 `ResumeDocument`；解析、投影、最终 Markdown 与审批摘要都消费同一份不可变快照，不再重读路径。添加在 `load_resume()` 后替换输入文件并断言渲染仍绑定原快照（或稳定失败）的测试。

### CR-04: 正式投递根错误接受契约禁止的 `sources/` 与 `assets/`

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_delivery.py:18`
**Related:** `skills/graduate-resume/scripts/graduate_resume_delivery.py:355`
**Issue:** `SUPPORT_DIRECTORIES` 把 `sources` 和 `assets` 视为合法节点，`_inspect_current()` 仅确认它们是目录，完全不检查内部内容。D-13 明确规定 Phase 48 delivery root 只能包含平铺 triples 和事务所需 `history/`；规范化照片、源文件或其他诊断资产不得进入。最小复现中 `sources/private.txt` 存在时 `DeliverySession` 仍成功打开，既破坏 clean delivery，也可能把个人资料留在用户认为可直接投递的目录中。
**Fix:** Phase 48 的允许支持目录应只包含事务实际拥有的 `history` 与临时 `.work`；把 `sources`/`assets` 当作 unknown 并在 mutation 前失败。增加两个含非空 `sources`、`assets` 的 fail-closed 测试。

### CR-05: “锁定 Typst 0.15.0”只写在错误消息中，代码接受任意版本

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_layout.py:442`
**Related:** `skills/graduate-resume/scripts/graduate_resume_render.py:291`, `skills/graduate-resume/scripts/graduate_resume_typst.py:38`
**Issue:** 字体探测、照片规范化和 PDF 编译都只通过 `shutil.which("typst")`/命令名寻找可执行文件，从未执行并校验 `typst --version`。因此 0.14、0.16 或其他兼容命令只要能完成 fonts/compile 就会被接受，可能产生不同分页、PNG/PDF bytes 和 no-op 结果。当前机器恰好安装 0.15.0，所以测试通过不能证明 SKILL 与照片契约声明的版本锁定。
**Fix:** 建立唯一的 Typst resolver，读取绝对可执行路径并要求版本精确为 `0.15.0`；字体探测、照片规范化和正式编译必须复用该已验证路径。测试应注入一个返回非 0.15.0 版本但能成功退出的假 Typst，并断言稳定失败。

## Warnings

### WR-01: 事务清理错误被全部吞掉，可在“成功”后留下 stale `.work/.lock`

**Classification:** WARNING
**File:** `skills/graduate-resume/scripts/graduate_resume_delivery.py:699`
**Issue:** `close()` 对候选/rollback 文件删除、run 目录删除、`.lock` 删除和 `.work` 删除的所有 `OSError` 都直接忽略；`__exit__()` 也不验证清理结果。发布可向用户返回成功，同时留下锁或 stale run，下一次命令会因并发锁或 stale work fail-closed，且用户无法从本次结果知道需要审计。
**Fix:** 对清理步骤收集错误并在无活动异常时返回明确的 `DELIVERY_CLEANUP_FAILED`；至少重新检查 owned `.lock`、run 目录与 `.work` 是否消失。若 current 已成功发布，错误结果必须明确区分“发布已完成但清理失败”，避免误导用户重试事务。

---

_Reviewed: 2026-07-18T13:42:57Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
