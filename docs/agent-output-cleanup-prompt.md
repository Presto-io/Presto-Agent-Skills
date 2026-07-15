# Agent 硬盘产物整理提示词

本提示词定义历史 agent 产物的 snapshot-bound `audit → confirm → execute` 两阶段协议。它独立于普通 render/deliver；任何渲染或发布命令都不得自动触发该流程。

## Approval Contract

- 输入必须包含用户逐项明确授权的 roots；空列表、`~`、主目录泛扫、父目录推断或未授权邻接目录均拒绝。
- 阶段一只允许 no-follow `lstat`、有界读取、容器只读检查和内存哈希。它不得移动、归档、重命名、隔离、覆盖、删除、render、build、format、安装依赖、修改 Git，或创建 delivery sidecar。
- 审计 snapshot 必须绑定每个授权 root 的相对路径、对象类型、size、mtime_ns、inode/device（可用时）、regular file bytes hash 和 symlink 自身信息；不得跟随 symlink 读取目标内容。
- 审计输出必须给出三组 exact relative operations：`安全移动`、`需确认归档`、`需明确批准删除`。每项包含授权 root 标识、source、destination、operation 和理由；不得使用 glob、目录递归通配或“其余文件”等开放表达。
- `.teaching-design-package/`、`.tiaokedan/`、legacy `media/`、unknown user file、用户原始资料和任意 symlink 都必须进入确认门，不得自动归入安全操作。
- 阶段二只接受与 snapshot 摘要完全绑定的 approval token，或包含同一 snapshot 摘要与 exact approved operations 的 approved plan。没有确认、部分口头概括、默认 `--yes`、过期 snapshot 或超出授权 root 的操作一律拒绝且零 mutation。
- 执行前重新生成 snapshot；任何 path、type、identity、metadata 或 bytes 不匹配都视为 changed-after-audit，必须拒绝旧批准并重新审计。
- 阶段二只执行 exact approved operations；未批准项保持原 path、bytes、inode（适用时）和 symlink target 不变，不得顺手扩展范围。

## Reusable Prompt

```text
你现在要整理历史 AI agent 在本地留下的散乱产物。严格执行以下两阶段协议；默认只能进入阶段一。

【授权 roots】

- <填写精确绝对 root 1>
- <填写精确绝对 root 2>

只处理上述逐项授权 roots。不得把 `~`、用户主目录、共同父目录或邻接目录解释为授权；不得扫描凭据、浏览器、聊天、照片、邮件、云盘、系统或应用数据。路径越权立即报告并拒绝。

【阶段一：只读审计】

1. 以 lstat/no-follow 方式遍历授权 root；符号链接只记录链接自身和文本 target，不跟随。symlink escape 无论目标是否存在都标为“需确认”，不得读取目标。
2. 为授权 root 生成 snapshot：记录 exact relative path、对象类型、size、mtime_ns、inode/device（平台可用时）、regular file SHA-256 和 symlink target。snapshot 保存在内存或系统临时目录，不写入交付 root。
3. 只做非破坏性检查：regular/non-empty/readable、文本引用、容器是否可有界打开、文件的成套关系。不得重新 render/build，也不得用文件名中的 final/最新版作为唯一判断。
4. 识别当前 Markdown、当前最终产物、旧成功版本、用户 sources、持续引用 assets、中间证据、失败产物和 unknown。无法确定用途时保守归为 unknown。
5. `.teaching-design-package/`、`.tiaokedan/`、legacy `media/`、unknown user file、用户资料与全部 symlink 必须走确认门，禁止静默迁移或删除。
6. 输出一份 bounded audit report，并将全部建议变更拆成且只拆成三组 exact relative operations：
   - 安全移动
   - 需确认归档
   - 需明确批准删除
   每项写明 root 标识、operation、source、destination、理由；不得使用 glob、递归通配、“同类文件”或开放范围。
7. 报告 snapshot digest、操作计划 digest、预计数量、风险与回退方法，然后停止。阶段一不得移动、归档、重命名、隔离、覆盖、删除、render、build、format、运行包管理器、修改 Git 或创建 manifest/status/model/log/diff/screenshot/sidecar。

【确认输入】

阶段二只接受以下之一：

- 与 snapshot digest 和 plan digest 完全绑定的 approval token；或
- 明确列出同一 snapshot digest、plan digest 与 exact approved operations 的 approved plan。

拒绝缺少 digest 的“全部同意”、默认 --yes、从对话猜测批准、追加未审计操作或超出授权 root 的 destination。

【阶段二：确认后执行】

1. mutation 前以同一算法重新生成当前 snapshot。若任何 path、type、identity、metadata、bytes 或 symlink target 与审计 snapshot 不匹配，返回 STALE_SNAPSHOT，零 mutation，并要求重新审计。
2. 逐项校验 approved operation 的 source/destination 都是授权 root 内的安全相对路径；拒绝 absolute、`..`、NUL、分隔符逃逸、symlink traversal、覆盖现有 unknown 或越权 root。
3. 只执行 exact approved operations，不处理未批准项。先处理获批的完整历史 bundle，再处理获批 sources/assets 与引用修正，最后处理逐项获批的隔离或删除。
4. 删除必须逐文件明确批准；优先使用用户明确批准位置的隔离目录。不得创建默认隔离目录，也不得永久删除唯一副本。
5. 每次历史归档必须把同版 Markdown、全部最终产物和保持引用有效的 managed assets 放入同一个 history/<sequence>/；sources 不自动归档。
6. 执行后只做最小只读验证：当前 bundle 完整非空、引用有效、history 成套、未批准项 snapshot 不变、根目录无新 sidecar。临时证据完成后删除。
7. 最终报告实际完成与拒绝的 exact operations，以及完全未触碰的文件。任何不确定性都必须停止并询问，不得猜测。
```

## Required Refusal Results

- `UNCONFIRMED_EXECUTION`：没有 snapshot-bound approval；零 mutation。
- `STALE_SNAPSHOT`：审计后任何受审对象发生变化；零 mutation并重新审计。
- `UNAUTHORIZED_ROOT`：source、destination 或扫描请求不在逐项授权 roots 内；零 mutation。
- `SYMLINK_ESCAPE`：操作需要跟随 symlink 或目标越过授权边界；零 mutation。
- `PLAN_MISMATCH`：请求操作不在 exact approved operations 中；零 mutation。

失败结果必须有界、不得输出 traceback，也不得包含“整理成功”等 false-success 文案。
