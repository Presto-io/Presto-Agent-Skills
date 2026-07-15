# Clean Delivery Directory Contract

本契约是所有会创建交付文件的技能必须遵守的公共 authority。它规定一套可复验的 `DeliverySpec`、candidate-first 状态机、历史版本规则和失败恢复边界。每个技能必须在自身目录内实现该协议；生产运行时不得 import、调用 sibling skill 或仓库根测试 helper。

## DeliverySpec

每条最终发布路径都必须在 mutation 前得到一个封闭的 `DeliverySpec`，至少包含：

- `delivery_root`：用户明确授权的交付根目录。
- `current_names`：当前 Markdown 与当前最终产物的显式相对路径集合；可选 PDF 等模式变化必须改变该集合。
- `managed_assets`：当前 Markdown 或最终产物持续引用、由技能明确管理的 `assets/` 相对路径集合。
- `current_discovery`：只读识别零套或恰好一套完整 current bundle 的规则；重复 stem、重复前缀或多套候选均为歧义。
- `minimal_validators`：逐产物的存在、regular、non-symlink、非空、可读和格式检查，以及持续资源引用检查。
- `allowed_directories`：默认仅为 `sources/`、`assets/`、`history/`、`.work/`；确需其他长期支持目录时，必须由技能 artifact contract 显式声明。

受管交付集合等于 `current_names + managed_assets`。相同内容必须同时满足 relative path-set 完全相等和每个对应文件 bytes 完全相等；不得只比较 Markdown、mtime、size、stem 或缓存 manifest。

## Required Layout And Ownership

```text
<delivery-root>/
├── <current-markdown>.md
├── <current-final-artifact>.*
├── sources/
├── assets/
├── history/
│   └── 001/
└── .work/
    └── <run-id>/
        ├── candidate/
        ├── rollback/
        └── evidence/
```

没有内容的目录不预创建。各目录所有权如下：

- `sources/`：用户明确要求长期保留的原始资料；normal publish 永不自动归档、移动、重命名、删除或改写 `sources/`。
- `assets/`：当前版本持续引用的显式 managed assets；任意输入资料不得因“可能有用”而自动复制进入。
- `history/`：被新成功版本替换的完整旧受管集合；技能不得自动删除、压缩或重编号历史。
- `.work/<run-id>/candidate/`：完整候选集合；候选通过所有最小验证前不得触碰 current。
- `.work/<run-id>/rollback/`：发布前逐文件复制并复验的旧受管集合。
- `.work/<run-id>/evidence/`：本次 gate 所需的有界日志、diff、状态或验证证据；不得发布到根目录。

根目录一级只允许 `DeliverySpec.current_names` 中的当前文件和允许支持目录。manifest、status、model、JSON、日志、diff、截图、验证报告、缓存、staging、失败产物、随意版本副本、legacy `.teaching-design-package/`、legacy `.tiaokedan/` 和 legacy `media/` 均不是普通发布的长期例外。

## Candidate-First State Machine

每次可能改变 current 的运行必须按以下顺序执行：

1. 验证授权 root 身份，在同根 `.work/` 内取得排他锁；并发运行无法安全取得 same-root lock 时失败关闭。
2. 创建本次 owned `.work/<run-id>/{candidate,rollback,evidence}`。
3. 在 `candidate/` 中生成完整候选集合并运行 `DeliverySpec.minimal_validators`。
4. 以 `lstat`、held descriptor 或等价 no-follow 机制只读检查根目录，发现 current 并验证完整显式受管集合。
5. 若 current 不存在，执行首次发布；若 path-set+bytes 相等，保持 current inode、mtime 与 history 不变并只清理本次 owned work；若内容变化，进入历史与发布事务。
6. changed 发布先从已逐文件验证的 `rollback/` 快照准备单一 history bundle，再通过逐文件 replace 发布 candidate，并执行 post-publish root、bytes、格式和引用检查。
7. 成功后清理本次 candidate、rollback、evidence、run 目录与锁；仅当 `.work/` 为空且确属本次可清理范围时删除它。

禁止在候选完整生成和验证前删除、覆盖、移动或截断 current。禁止 broad glob、`find -delete`、通配符 `rm`、按文件名模式清理用户根目录，或让 normal render/deliver 自动触发历史整理。

## Root Inspection And Fail-Closed Rules

普通发布在任何 current/history mutation 前，必须拒绝并给出有界诊断：

- 不属于显式 managed set 或允许支持目录的 unknown entry；
- 任意 root、current、support、history、work 或 candidate symlink，包括越过授权 root 的 symlink escape；
- device、socket、FIFO 或其他非 regular file/非真实目录对象；
- duplicate current group、歧义 stem/前缀或无法验证的旧 bundle；
- legacy hidden diagnostics、legacy `media/` 或未确认的用户资料；
- absolute path、`..`、NUL、分隔符注入、跨设备路径或其他越界 component。

这些条目不得被普通发布自动移动、归档、隔离或删除；只能进入 snapshot-bound 的历史整理确认流程。清理只允许移除本次运行记录为 owned 的明确路径/identity；无关 stale `.work` 项必须保留并失败关闭。

## History Rules

在同一排他锁内，仅扫描 `history/` 下名称匹配 `^[0-9]{3,}$` 且为 non-symlink directory 的条目。下一序号是现有合法数字的 `max + 1`，至少三位零填充；不得复用 gap。例如已有 `001/` 和 `003/` 时下一版必须是 `004/`。

一个 history sequence 必须包含旧版 Markdown、全部同版最终产物和旧 Markdown 继续可读所需的全部 managed `assets/`。若 archived Markdown 在 `history/001/name.md` 中引用 `assets/x`，则资源必须随版本进入 `history/001/assets/x`，并通过引用检查。`sources/` 不进入历史，normal publish 也不移动或修改它。不同 artifact 不得拆分序号，未知 asset 不得擅自归类为 managed asset。

历史只能从 verified rollback snapshot 建立，不得先移动 current 再尝试生成或验证 candidate。既有 history 的 path-set 与 bytes 在发布、失败和回滚过程中必须保持不变。

## Replace, Rollback And Atomicity Boundary

`os.replace` 或同文件系统 rename 只保证单个路径的原子替换，不保证多个稳定文件、`assets/` 与 `history/` 组成一个跨路径原子事务。本契约只承诺：

- candidate 在 current mutation 前完整且已验证；
- 每个旧文件进入 `rollback/` 后逐文件核对 path-set+bytes；
- 每次单文件 replace 都被记录，post-publish 前仍可判定已替换和新增路径；
- handled failure、普通命令错误、已捕获异常以及 `INT`/`TERM` 会恢复旧集合，移除本次新引入文件和本次新 history sequence，并验证旧 current 与既有 history 的 bytes；
- cleanup 只处理本次 owned 路径，随后释放 same-root lock。

本契约不承诺 `SIGKILL`、断电、内核或文件系统损坏下自动恢复，也不声称“多文件原子发布”。若某技能没有实现并验证 bounded recovery journal，后续运行不得猜测或宣称能自动恢复硬崩溃中断的事务；应保守失败关闭并请求审计。即使实现 journal，也只能声明其测试覆盖的恢复窗口。

## Minimal Verification

最小发布 gate 至少证明：

- Markdown/Typst/HTML 为 regular、non-symlink、非空、UTF-8 可读，并通过技能既有内容 gate；
- PDF 由候选输入成功生成、非空且具有有效 PDF header，并执行技能已有 reopen/merge gate；
- XLSX/PPTX/DOCX 等容器可有界打开并包含既有契约要求的成员；
- HTML 满足既有 size/offline/DOM gate；动态 bundle 满足声明的精确文件集合与既有 registry/order gate；
- 所有 persistent relative asset references 都解析到候选或 current 的显式 managed `assets/`；
- 根目录最终白名单、受管 path-set+bytes 和 current format gate 全部通过。

验证优先使用退出状态、内存或 `.work/<run-id>/evidence/`，不得为证明成功在交付根保留 sidecar。自动最小验证不替代既有 renderer regression 或用户拥有的 PowerPoint/WPS 等人工 UAT。

## Skill Authoring Requirement

所有写文件的 canonical `SKILL.md` 或其 artifact contract 必须列出完整 `DeliverySpec`、稳定 current names、可选模式、支持目录生命周期、candidate-first 流程、identical no-op、changed whole-bundle history、handled rollback、unknown fail-closed、minimal validators 和人工验收边界。Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw 与 Hermes Agent 的 adapter notes 必须保持同一写入安全语义；runtime 差异只能说明发现、显式调用 fallback、依赖、权限与 sandbox/allowlist。
