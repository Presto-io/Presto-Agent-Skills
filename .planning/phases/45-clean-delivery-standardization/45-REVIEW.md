---
phase: 45-clean-delivery-standardization
reviewed: 2026-07-16T15:28:53Z
depth: standard
files_reviewed: 43
files_reviewed_list:
  - README.md
  - docs/compatibility-matrix.md
  - docs/directory-spec.md
  - skills/README.md
  - skills/end-of-term-teaching-materials/SKILL.md
  - skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md
  - skills/end-of-term-teaching-materials/scripts/end_of_term/_engine.py
  - skills/end-of-term-teaching-materials/scripts/end_of_term/delivery.py
  - skills/end-of-term-teaching-materials/scripts/end_of_term/test_delivery.py
  - skills/gongwen/SKILL.md
  - skills/gongwen/references/format-and-rendering.md
  - skills/gongwen/scripts/gongwen.sh
  - skills/gongwen/scripts/gongwen_lib/commands.sh
  - skills/gongwen/scripts/gongwen_lib/delivery.sh
  - skills/gongwen/tests/test_clean_delivery.sh
  - skills/gongwen/tests/test_heading_normalization.sh
  - skills/school-pptx/SKILL.md
  - skills/school-pptx/fixtures/clean-delivery/confirmed-assets.md
  - skills/school-pptx/references/renderer-and-pagination.md
  - skills/school-pptx/references/verification-contract.md
  - skills/school-pptx/scripts/pptx_render.py
  - skills/school-pptx/scripts/verify_markdown_contract.py
  - skills/school-pptx/scripts/verify_pptx_renderer.py
  - skills/school-presentation/SKILL.md
  - skills/school-presentation/references/authoring-and-layout.md
  - skills/school-presentation/references/verification-contract.md
  - skills/school-presentation/scripts/school_presentation/_engine.py
  - skills/school-presentation/scripts/school_presentation/delivery.py
  - skills/school-presentation/scripts/school_presentation/test_delivery.py
  - skills/teaching-design-package/SKILL.md
  - skills/teaching-design-package/references/format-and-orchestration.md
  - skills/teaching-design-package/scripts/delivery-transaction.js
  - skills/teaching-design-package/scripts/package-model.js
  - skills/teaching-design-package/scripts/teaching-design-package.sh
  - skills/teaching-design-package/scripts/test-delivery-transaction.js
  - skills/tiaokedan/SKILL.md
  - skills/tiaokedan/references/markdown-contract.md
  - skills/tiaokedan/references/pdf-workflow.md
  - skills/tiaokedan/scripts/delivery_transaction.py
  - skills/tiaokedan/scripts/test_delivery_transaction.py
  - skills/tiaokedan/scripts/tiaokedan_renderer.py
  - templates/skill/SKILL.md
  - test/clean-delivery/verify_clean_delivery.py
findings:
  critical: 9
  warning: 3
  info: 0
  total: 12
status: issues_found
---

# Phase 45: Code Review Report

**Reviewed:** 2026-07-16T15:28:53Z
**Depth:** standard
**Files Reviewed:** 43
**Status:** issues_found

## Summary

六个交付实现的候选、history、回滚与文档边界整体趋于一致，但仍存在可达的越界删除、真实信号未回滚、首次发布中断残留、父级符号链接逃逸，以及动态文件组发现歧义。自动故障点测试没有覆盖若干真实异步窗口，因此当前不能把 handled signal、unknown fail-closed 或资产边界视为已证明。

## Narrative Findings (AI reviewer)

## Critical Issues

### CR-01: TDP cleanup 可经符号链接父目录删除交付根外内容

**File:** `skills/teaching-design-package/scripts/delivery-transaction.js:413`
**Issue:** `cleanup` 仅校验 `runId`，随后用 `path.resolve(root)/.work/<runId>` 和纯词法 `path.relative` 作为删除边界；它既不验证 delivery root，也不拒绝 `.work` 为符号链接。若 `<root>/.work` 指向外部目录，公开可达的 `cleanup` 会递归删除外部同名 run 目录。审查中用临时目录实际复现，外部 sentinel 被删除；shell 的 `EXIT/INT/TERM` trap 会调用这条路径，因此不是测试专用死代码。
**Fix:** cleanup 必须先以 `lstat + O_NOFOLLOW/O_DIRECTORY` 持有 root 与 `.work`，逐级 no-follow 打开并核对 inode，再只通过目录描述符删除精确 run-id 子树；任何父级符号链接或身份变化均失败关闭。补充公开 CLI 的 `.work` 符号链接逃逸负例并断言外部 sentinel 不变。

### CR-02: TDP publisher 吞掉真实 INT/TERM 并继续发布

**File:** `skills/teaching-design-package/scripts/delivery-transaction.js:426`
**Issue:** CLI 为 `SIGINT`、`SIGTERM` 注册空处理器。外部真实信号因此不再触发 Node 默认退出，也不会抛入 `publishBundle` 的 rollback 分支，进程可继续逐文件 rename 并返回成功。现有测试只通过环境变量在 fault hook 内 `process.kill` 后立即主动 `fail()`，证明的是注入异常，而不是实际外部信号语义，与文档“handled INT/TERM 回滚”不符。
**Fix:** 信号处理器应设置中止状态并抛出/触发统一的可回滚取消路径，发布循环每次 mutation 前后检查该状态；回滚完成后恢复标准信号退出码。新增父进程在 `after_publish_file_1` 真实发送 SIGINT/SIGTERM 的测试，不得依赖同一 hook 随后的人工异常。

### CR-03: 期末材料首次发布存在 replace 后、登记前的残留窗口

**File:** `skills/end-of-term-teaching-materials/scripts/end_of_term/delivery.py:364`
**Issue:** 首次发布时先 `os.replace`，下一条语句才把文件名加入 `_published`；Python 信号可在两条语句之间执行。此时 `_old_bytes` 为空，rollback 只删除 `_published` 中的名字，因此刚完成 replace 但尚未登记的文件留在根目录，而空旧状态校验仍会通过。fault injection 都发生在 append 之后，无法覆盖该真实异步窗口。
**Fix:** rollback 在首次发布时删除完整显式 `CURRENT_NAMES`（逐项 no-follow），或在 replace 前记录 pending name 并让 rollback 覆盖 pending/completed 的并集。增加在 replace 与登记之间注入真实信号的测试，并断言根目录回到完全空 current。

### CR-04: school-pptx 首次发布存在相同的未登记文件残留窗口

**File:** `skills/school-pptx/scripts/pptx_render.py:373`
**Issue:** `os.replace`/`unlink` 完成后才执行 `_published.append(name)`，而 `_restore` 只清理 `_published ∪ old_names`。首次发布的 `old_names` 为空，若 INT/TERM 落在 mutation 完成与 append 之间，刚发布的 Markdown、PPTX 或 asset 不在恢复集合中，回滚后可留下 partial current；测试 hook 位于 append 之后，不能证明该窗口安全。
**Fix:** mutation 前登记 pending name，恢复时清理 `candidate_names ∪ old_names` 的显式集合，或用不可分割的状态记录覆盖 pending/completed。补充首次发布真实信号窗口测试，包含根文件与嵌套 asset。

### CR-05: school-presentation 首次发布存在相同的未登记文件残留窗口

**File:** `skills/school-presentation/scripts/school_presentation/delivery.py:453`
**Issue:** 发布或删除完成后才把名字加入 `_published`，而 `_restore` 仅使用 `_published ∪ old_names`。首次发布期间真实信号若在 replace 后、append 前到达，已写入文件不会被恢复逻辑移除，且空旧 bundle 的字节校验无法发现根目录多出的残留文件。
**Fix:** 将 pending mutation 纳入 rollback 覆盖，首次发布失败时按显式 `spec.current_names` 清除全部可能写入项；新增在 append 前触发的 SIGINT/SIGTERM 回归测试。

### CR-06: school-pptx managed asset 可通过父级符号链接逃出输入根

**File:** `skills/school-pptx/scripts/pptx_render.py:266`
**Issue:** `stage_assets` 直接打开 `input_root / relative`，`_read_regular` 的 `O_NOFOLLOW` 只保护最终文件，不保护中间目录。Markdown 引用 `assets/link/secret.png` 且 `assets/link` 是指向输入根外的符号链接时，最终 `secret.png` 是普通文件，读取会成功并把外部内容复制进公开交付。当前 fixture 只覆盖普通 asset，不覆盖父级 symlink。
**Fix:** 从 no-follow 打开的 input root/`assets` 描述符逐级解析每个组件，拒绝任何 symlink 或身份变化；不要用字符串 Path 穿越父目录。加入中间目录 symlink、交换攻击与外部 sentinel/secret 不可读的负例。

### CR-07: school-presentation managed asset 同样可通过父级符号链接逃出输入根

**File:** `skills/school-presentation/scripts/school_presentation/delivery.py:338`
**Issue:** `asset_root / name` 通过路径字符串读取，最终文件虽用 `O_NOFOLLOW`，但 `assets/` 下任意中间目录可为符号链接，导致读取并发布授权输入根外的文件。`_safe_relative_asset` 只检查词法组件，不能阻止该逃逸。
**Fix:** 使用持有的 asset-root 目录描述符逐级 no-follow 打开相对路径，拒绝符号链接目录；补充父级 symlink 和检查后交换测试，验证外部文件既不被读取也不进入 candidate/history。

### CR-08: gongwen 的检查与发布/回滚之间没有目录身份绑定

**File:** `skills/gongwen/scripts/gongwen_lib/delivery.sh:365`
**Issue:** shell 实现先以路径检查 `DELIVERY_ROOT`，随后用同一路径执行 `mv -f`；期间未持有 root inode，也未在每次 mutation 前重新核对身份。并发替换 root 为指向外部目录的符号链接时，发布或 `delivery_abort` 中的 `rm -f "$DELIVERY_ROOT/$name"` 可写入/删除外部同名文件。开头的 `[[ -d && ! -L ]]` 是 check，不消除后续 use 的竞态。
**Fix:** 将事务发布移入支持目录描述符、`O_NOFOLLOW` 和 dir-fd replace/unlink 的本地 helper（Python/Node 均可，但必须随 skill folder 自包含），shell 只负责参数与命令编排；增加 root 在 candidate 验证后交换为 symlink 的真实负例。

### CR-09: TDP candidate 验证与 rename 之间可交换父目录并移动外部文件

**File:** `skills/teaching-design-package/scripts/delivery-transaction.js:370`
**Issue:** publisher 虽持有 delivery root 描述符，却仍以路径字符串访问 `.work/<run>/candidate`。candidate 在第 332 行验证和读取后，到第 374 行 `renameSync` 前可被交换为指向外部目录的父级符号链接；随后 rename 会把外部同名文件移入交付根，造成根外 mutation。post-check 最多触发回滚，无法把已从外部目录移走的源文件放回。
**Fix:** 持有 `.work`、run、candidate 的 no-follow 目录身份，并通过 dir-fd rename 完成发布；若 Node 运行时不能提供所需原语则失败关闭或改用随 skill 自包含的安全 helper。加入 candidate 父目录交换测试并验证外部文件路径与 bytes 均不变。

## Warnings

### WR-01: 动态 TDP current 发现依赖新 registry suffix，升级时会误判旧完整组

**File:** `skills/teaching-design-package/scripts/delivery-transaction.js:180`
**Issue:** `discoverCurrent` 只从“本次新模型”的 suffix 列表反推旧 current。registry 新增/删除模块时，旧的完整 `1+1+N` 组会按新 suffix 被判 partial；若两个 suffix 存在后缀包含关系，同一文件会匹配多个 suffix 并被判 unknown。这样 `expected_public_filenames` 虽是动态 mutation authority，却不能可靠识别上一版动态集合。
**Fix:** 在 current 中保留不公开的受信任集合描述并不可取，因此应让 discovery 使用严格、无歧义的命名语法和 registry 版本迁移规则，或从受验证的文件组结构穷举唯一分组；构建模型时同时拒绝 suffix 重叠。新增 N=2→N=3、N=3→N=2 与 suffix-overlap 测试。

### WR-02: school-pptx 只验证 history 目录名，不验证历史 bundle 内容

**File:** `skills/school-pptx/scripts/pptx_render.py:203`
**Issue:** `_inspect_history` 仅要求条目名为数字且本身是目录，没有检查每个序号内的 Markdown/PPTX/managed assets 是否为完整、非 symlink、引用一致的同版 bundle。损坏、partial 或含未知文件的历史会被接受并继续生成下一版，与 reference 中“whole-bundle history、malformed history fail-closed”不一致。
**Fix:** 对每个 history sequence 解析其 Markdown，推导该版 managed assets，并验证 exact path set、普通文件、非空、引用存在且无未知项；任何 partial/symlink/额外内容在 current mutation 前失败关闭。

### WR-03: tiaokedan 的 raw Typst gate 可被未枚举的 `#` 表达式绕过

**File:** `skills/tiaokedan/scripts/tiaokedan_renderer.py:35`
**Issue:** `RAW_TYPST_RE` 只列举 `#set/#let/#table/...`，但 renderer 在标题、说明和单元格中直接插入文本。`#include`、`#import`、`#eval`、`#raw` 等未列举表达式可以通过验证并进入生成 Typst，违反“输入不含 raw Typst”的契约，并可能读取编译根内非预期文件或改变输出结构。
**Fix:** 不要靠黑名单识别 Typst；对所有 teacher-authored 文本统一做 Typst 内容转义，仅把受支持的 `<br>` 显式转换成 renderer-owned `#linebreak()`。增加每类 `#` 表达式、方括号和反斜杠的负例/转义测试。

---

_Reviewed: 2026-07-16T15:28:53Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
