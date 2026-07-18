---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
reviewed: 2026-07-18T18:38:41Z
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
  critical: 6
  warning: 4
  info: 0
  total: 10
status: issues_found
---

# Phase 48: Code Review Report

**Reviewed:** 2026-07-18T18:38:41Z
**Depth:** standard
**Files Reviewed:** 20
**Status:** issues_found

## Summary

标准深度审查发现 6 个必须在发布前修复的正确性、安全和数据完整性问题，以及 4 个可靠性问题。最严重的缺陷会把招聘 URL 与电话号码写入正式产物路径或 Markdown、允许重复事实字段静默覆盖、让 `validate` 对不可渲染资料误报通过、在未确认的预检中覆盖既有隐藏证据，以及允许已通过版本门禁的 Typst 快照被原地替换后继续执行。

最小复现确认：重复 `专业` 字段以最后一个值覆盖且校验通过；`candidate.directions: [123]` 校验通过；URL 形式的 target source 原样进入最终 Markdown；姓名 `张三13800000000` 原样进入正式 stem。

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: 招聘来源 URL 被公开到预检与正式 Markdown

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_final_markdown.py:136`
**Related:** `skills/graduate-resume/scripts/graduate_resume_cli.py:782`
**Issue:** target 的 `source` 只要求是非空字符串，随后既被写入公开预检矩阵，也被原样写入 `graduate-resume-delivery/v1` 的 `target.source`。使用 `https://jobs.example.test/private?id=123` 的最小复现确认 URL 明文存在于最终 Markdown。这直接违反 D-12“最终 Markdown 不含原始招聘 URL”和安全章节的披露边界，也可能泄露带查询参数的私有招聘链接。
**Fix:** 在 canonical 校验时把 `source` 限定为有界的来源描述/类别并拒绝 URL，或在投影时只发布来源类别与不可逆摘要；公开预检和最终 Markdown 都不得复制原始 URL。

```python
if re.match(r"(?i)^[a-z][a-z0-9+.-]*://", source):
    raise CliError("VALIDATION_FAILED", "target.source 必须是来源描述，不能是 URL。")
```

### CR-02: 安全 stem 未检测电话、邮箱或身份证信息

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_render.py:233`
**Issue:** `safe_component()` 只规范化字符和长度，`build_stem()` 直接把姓名、单位和岗位拼入文件名。姓名 `张三13800000000` 会生成 `张三13800000000简历-通用-保守稳妥`；同理，邮箱或身份证号也可经这些字段进入 current/history 路径。D-15 和 `SKILL.md` 明确禁止电话、邮箱、身份证进入 stem，因此这是可触发的隐私泄露。
**Fix:** 在拼接前对三个组件执行集中式敏感标识检测；命中电话、邮箱、身份证或 URL 时稳定失败，并在 canonical 字段校验与 stem 单元测试中覆盖这些负例。

```python
def reject_sensitive_component(value: str) -> None:
    if EMAIL_RE.search(value) or PHONE_RE.search(value) or ID_CARD_RE.search(value) or URL_RE.search(value):
        raise CliError(RENDER_INPUT_INVALID, "文件名组件包含禁止的敏感标识。")
```

### CR-03: 重复 Markdown 字段静默覆盖已解析事实

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_cli.py:380`
**Issue:** bullet 解析直接执行 `entry[field] = ...`，没有检查同一条目是否已出现该字段。两个 `- 专业：...`、`- 招聘要求：...` 或 `- 已确认：...` 会以后者静默覆盖前者并通过校验。最小复现中第二个“专业”成功替换第一个值且 `validate_document()` 返回 passed，导致人类可见的冲突资料被机器悄悄选边，破坏事实完整性和可审阅性。
**Fix:** 每个条目的规范字段必须唯一；赋值前若字段已存在则以稳定 `MARKDOWN_INVALID` 失败，并为普通事实与 target 添加重复字段负例。

```python
if field in entry:
    raise CliError("MARKDOWN_INVALID", f"第 {line_number} 行重复字段: {label}")
entry[field] = parse_value(field, raw_value)
```

### CR-04: `validate` 接受渲染器必然拒绝的嵌套值

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_cli.py:447`
**Related:** `skills/graduate-resume/scripts/graduate_resume_cli.py:500`
**Issue:** validator 对 `candidate.contact` 只检查键名，对 `candidate.directions` 只检查外层是 list，对 target requirements 也只检查外层类型；它不验证元素均为安全非空字符串。`directions: [123]` 的最小复现会被 `validate` 判定 passed，但正式布局在 `_display_string()` 中失败。由此公开的 schema gate 会对不可发布资料给出错误成功结论，违背工作流“validate 后进入 final render”的契约。
**Fix:** 抽取统一的安全字符串、字符串列表和 contact 值校验器，在 `validate_candidate()`、`validate_targets()` 及所有可选列表字段上递归应用；对应负例必须在 `validate` 阶段失败。

### CR-05: 未确认预检会覆盖既有隐藏证据记录

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_render.py:187`
**Related:** `skills/graduate-resume/scripts/graduate_resume_cli.py:895`
**Issue:** evidence 文件名只由 `version_id + condition_digest` 构成，未包含 canonical hash 或 projection digest。只要招聘条件与四态未变，候选事实或 canonical bytes 变化后仍会命中同名文件；`persist()` 在 bytes 不同时用 `os.rename()` 直接覆盖旧证据。更严重的是它在 delivery preflight 和 `--confirm` 判断之前执行，因此一次未确认预检即可破坏已发布版本对应的旧审计绑定，造成证据数据丢失。
**Fix:** 文件身份至少加入 canonical hash 与 projection digest，已存在且内容不同时必须拒绝而不是覆盖；若证据属于正式发布审计，则先写 candidate evidence，并在 delivery 确认事务成功后原子发布，预检不得改写持久证据。

```python
name = f"{projection.version_id}-{canonical_hash}-{projection.digest}-{projection.condition_digest}.json"
if existing is not None and existing != raw:
    raise CliError(RENDER_INPUT_INVALID, "同名证据与既有绑定冲突。")
```

### CR-06: Typst 快照只校验 inode，版本门禁后仍可被原地篡改执行

**Classification:** BLOCKER
**File:** `skills/graduate-resume/scripts/graduate_resume_typst_runtime.py:104`
**Issue:** resolver 虽记录了 `snapshot_sha256`，但 `run()` 仅比较 `st_dev/st_ino`，不复验 mode、size 或 hash。快照文件归当前用户所有；对其 chmod 后原地覆写可保留 inode，后续 `run()` 会执行被替换的二进制。这样恶意程序可在 `--version` 通过后获得任意命令执行，破坏“所有消费者共享 immutable 0.15.0 snapshot”的安全声明。
**Fix:** 优先通过 held executable descriptor/fexecve 等机制执行不可替换对象；若平台限制至少在每次执行前复验完整 identity、mode、size 与 SHA-256，并缩短校验到 exec 的窗口。增加 snapshot 原地覆写但 inode 不变的负例。

## Warnings

### WR-01: CJK 长度按字符截断却按字节拒绝，导致合法 stem 延迟失败

**Classification:** WARNING
**File:** `skills/graduate-resume/scripts/graduate_resume_render.py:242`
**Related:** `skills/graduate-resume/scripts/graduate_resume_delivery.py:58`
**Issue:** `safe_component()` 用 Unicode 字符数执行 48 字符限制，而 delivery owner prefix 使用 96 UTF-8 bytes、完整 stem 使用 180 bytes。40 个汉字的姓名可通过 stem 构建，却在 `DeliverySpec` 以 `delivery owner prefix is unsafe` 延迟失败。错误边界不一致，且用户得到的是投递层错误而不是明确的命名错误。
**Fix:** 统一采用 UTF-8 byte budget，在 `safe_component()` 中按完整 stem/prefix 预算安全截断并保留摘要；构建矩阵时就验证最终 owner prefix 与 stem。

### WR-02: 定向照片 fixture 引用了不存在的资产

**Classification:** WARNING
**File:** `skills/graduate-resume/fixtures/render/targeted-photo.md:7`
**Issue:** fixture 声明 `photo: media/source-photo.jpg`，但 `fixtures/render/media/source-photo.jpg` 不存在，且范围内测试没有消费该 fixture。它可通过当前 schema 校验，却无法完成照片渲染，因此不能作为可靠的“定向照片渲染字面 fixture”。
**Fix:** 提供受控 fixture 图片或把路径改为实际存在且位于授权 assets root 下的相对资产，并加入真实 render 负载测试，确保缺失资产不会再次漏检。

### WR-03: 主题测试在源码模板目录使用固定探针文件

**Classification:** WARNING
**File:** `skills/graduate-resume/scripts/test_theme_contract.py:138`
**Issue:** 测试固定创建 `templates/.theme-contract-probe.typ` 与相邻 PDF。并行测试会互相覆盖/删除文件，进程中断会留下脏文件，测试运行还会修改源码树，与可重复、隔离的 fixture 约定冲突。
**Fix:** 在 `TemporaryDirectory()` 中创建探针并复制或引用受控模板；每个测试使用唯一工作目录，不向 `skills/graduate-resume/templates/` 写入临时产物。

### WR-04: 已确认 target 可绕过结构化招聘要求进入发布

**Classification:** WARNING
**File:** `skills/graduate-resume/scripts/graduate_resume_cli.py:488`
**Issue:** `validate_targets()` 只要求 `id/company/role/source/as_of`，并仅在 `requirements` 存在时检查外层类型（第 500-502 行）。字段缺失时，`evaluate_hard_conditions()` 又将其默认成空元组（`graduate_resume_targeting.py:439`），故 `render --target` 和 `batch` 会成功构造条件计数全为 0 的 projection 并允许发布。此行为违反 D-01 对 confirmed target 必须包含结构化 `requirements` 的投影前提，使四态检查与 gap gate 在该目标上失效。
**Fix:** 在 canonical 校验阶段要求 `requirements` 为非空安全字符串列表，并增加缺失、空列表及空字符串列表的 CLI 负例。

```python
requirements = target.get("requirements")
if not isinstance(requirements, list) or not requirements or any(
    not isinstance(item, str) or not item.strip() for item in requirements
):
    issues.append(f"{area}.requirements 必须是非空字符串列表。")
```

---

_Reviewed: 2026-07-18T18:38:41Z_
_Reviewer: the agent (gsd-code-reviewer)_
_Depth: standard_
