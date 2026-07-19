# 定向渲染与干净批量交付契约

本文档定义 `graduate-resume` 在 `graduate-resume/v2` 事实源通过校验后的离线目标投影、三主题 Markdown/Typst/PDF 渲染和正式投递行为。公开 CLI 不联网、不抓取招聘信息、不调用模型，也不把本次派生结果写回 canonical 事实源。

## D-01..D-08：目标投影与四态条件

- **D-01 事实边界：** 只消费 `status: verified` 的稳定事实 ID 和 `confirmed: true` 的 target；target 必须含稳定 `id`、`company`、`role`、`source`、`as_of` 和结构化 `requirements`。
- **D-02 不可变投影：** generic 或单个 target 各自形成 `VersionProjection`，绑定 canonical SHA-256、离线 targeting policy SHA-256、selected fact IDs、trace、页数反馈和条件摘要；派生 metadata 不回写 `graduate-resume/v2`。
- **D-03 确定排序：** 受控模块顺序优先，其次是 pin、整数相关性降序和稳定事实 ID；正文重排不改变结果。
- **D-04 本次覆盖：** `--retain FACT_ID`、`--exclude FACT_ID`、`--pin FACT_ID` 均可重复；未知、重复、冲突或排除核心事实稳定失败。覆盖只对本次命令有效。
- **D-05 受控谓词：** 只有 `education_level`、`major_exact`、`certificate_exact`、`fresh_graduate_status` 能输出 `meets` 或 `gap`。其他招聘条件不得用相似度推断，统一输出 `unknown` warning。
- **D-06 四态：** 每个 condition 固定为 `meets`、`gap`、`unknown`、`not-applicable` 之一。公开预检显示 condition ID、受控谓词、状态、计数和 digest；完整 reason 与 evidence fact IDs 只写 owned hidden evidence。每个隐藏证据文件绑定 canonical hash、projection digest 和 condition digest；同名但 bytes 不同的既有绑定必须失败，绝不覆盖。
- **D-07 逐目标放行：** `--allow-gap-target TARGET_ID` 仅放行该 target 的本次生成，不扩散到其他 target，不形成长期或全局 bypass。存在 gap 且未放行时，候选生成与正式投递均不开始。
- **D-08 唯一不适用语法：** 唯一公开入口是可重复的 `--not-applicable <target-id> <condition-id> <reason>`。两个 ID 使用稳定 ID grammar；reason 必须作为一个经 shell 引号保护的 UTF-8 argv，trim 后为 1..200 Unicode code points，拒绝 NUL、CR、LF 和全部 Unicode 控制字符。同一 target/condition pair 即使理由相同也不得重复；未知 target、未选择 target、未知 condition、generic 使用均稳定失败。不存在 JSON override 文件、`TARGET=JSON` 或第二种拼写。

三主题共享同一 selected fact ID tuple。页数反馈按 `conservative`、`modern`、`expressive` 固定顺序计算；任一主题不满足 `auto|1|2` 预算时，每轮只移除最低优先级且非 core/retain/pin 的一个事实，再让三个主题共同重算。没有可移除事实时稳定失败，不允许某个主题私自删事实。

## D-09..D-12：版本矩阵与最终 Markdown

- **D-09 单份选择：** `render` 必须在 `--generic` 与 `--target TARGET_ID` 中二选一，并固定生成保守稳妥、现代简洁、个性设计三个主题。
- **D-10 批量权威：** `batch` 默认展开 `generic + all confirmed targets`，每个版本固定生成三个主题；任一目标、条件、主题或 triple 失败时整个矩阵不可发布。
- **D-11 正式三件套：** 每个版本/主题恰好生成同 stem 的 `.md`、`.typ`、`.pdf`。三主题共享 selected fact digest，但各自保留主题、页数和照片模式。
- **D-12 最终 Markdown 检查点：** 正式 Markdown 使用 `graduate-resume-delivery/v1` 精确 schema，绑定 canonical hash、policy/hash、version、target、theme、page/photo、selected IDs、trace summary、condition counts/digest、gap allow snapshot 和 body hash。渲染顺序固定为 write Markdown → reopen → safe parse → validate binding → frozen layout → Typst → PDF；Typst 不得绕过重读后的 Markdown 消费 Python 内存事实。

最终 Markdown 只包含发布所需的有界摘要和所选事实，不包含完整 condition reason、evidence fact IDs、preview/comparison 页面、随机 run ID、当前时间、机器绝对路径或 canonical 照片源路径。

## D-13..D-19：命名、预检与事务

- **D-13 平铺正式输出：** delivery root 只平铺正式 `.md/.typ/.pdf` triples，以及事务管理所需的 `history/`；不发布 manifest sidecar、condition JSON、完整 evidence、preview、comparison、规范化照片中间件或日志。
- **D-14 完整 triple 历史：** 任一文件 bytes 变化即把整个旧 triple 分类为 `updated`；authority 移除的旧 triple 分类为 `removed`。history 只归档 updated/removed 的完整旧 triple，不复制 unchanged。
- **D-15 安全命名：** generic stem 为 `<姓名>简历-通用-<正式主题名>`，target stem 为 `<姓名>简历-<单位>-<岗位>-<正式主题名>`。组件先 NFKC，再限制字符、长度和分隔符；完整矩阵预检 stem collision。不得把电话、邮箱、身份证、source URL 或绝对路径放入文件名。
- **D-16 确认前预检：** 公开输出显示权威版本矩阵、完整 safe stems、page/photo/source/as_of、逐条件四态、gap allow，以及 `added/updated/unchanged/removed`。没有 `--confirm` 时不改变 current/history 或隐藏证据根；定向命令使用由调用者预先创建的独立隐藏证据根，确认发布完成后才持久化证据。
- **D-17 绑定确认：** `batch` 的确认摘要绑定完整 no-follow current snapshot 和 delta；确认后 current 变化必须重新预检。完整 candidate matrix 成功后才进入一次事务，任一 handled failure 保持整个原 current path set 与 bytes。
- **D-18 patch 与 no-op：** `render` 固定 `mode=patch`，只能新增或更新所选版本，保留其他 current stems 且不得产生 removals。相同输入为 true no-op，不创建 history，不改变 current inode 或 mtime。
- **D-19 authority 与 rollback：** `batch` 固定 `mode=authority`，确认后发布 candidate exact set 并移除 obsolete stems。事务使用 held directory、no-follow 检查、owned `.work`、完整旧 current rollback 和发布后 exact-set/bytes 验证；unknown、partial、symlink、stale work、collision 或批准摘要漂移均在 mutation 前失败。

## D-20：Typst 受控执行域

`plan`、`render`、`batch` 只可通过 `/usr/local/libexec/presto-graduate-resume-typst-exec` 启动已冻结的 Typst bytes。Python 仅传递 held snapshot fd、SHA-256、协议版本和受限 argv；helper 从 `getuid()`/`getgid()` 获取真实调用者、清空补充组并永久降权后运行 Typst，不接收 caller uid/gid。未安装 helper、`root:wheel`/`4755` 或完整父目录链不合格、mode 可写，或 Darwin ACL/等价扩展权限不能以真实调用者证明不可写时，必须在任何 Typst、candidate、current 或 history mutation 前以 `TYPST_RUNTIME_INVALID` fail closed。

该能力只能由管理员显式审阅 C source 的固定 SHA-256 后安装；安装脚本不调用 `sudo`，从同一 held source descriptor 冻结 root-owned staging，以受信绝对编译器和 `env -i` 受控环境构建。任何 source、compiler、环境、staging、编译、owner/mode/ACL 或 probe 失败都必须保留旧 helper。修复 `TYPST_RUNTIME_INVALID` 后，先以原参数重跑不含 `--confirm` 的预检，再在成功预检上追加相同确认参数；不得手工绕过 helper 或发布 partial triple。该本地前置条件不宣称完成 Phase 49 runtime 安装验收。

## 照片自包含契约

照片必须来自用户明确提供的本地 JPEG/PNG。使用锁定的 Typst 0.15.0 在零边距白底页面上执行 contain、保持宽高比、允许等比放大、禁止拉伸和裁切，并以 `--format png --ppi 300 --creation-timestamp 0` 生成 `413 × 579`、300 PPI 栅格基准的 PNG。输出重新解码验证 IHDR，移除 EXIF、方向、源文件名和路径 metadata。

规范化 PNG bytes 直接以内嵌 bytes 写入正式 `.typ`；中间 PNG 只存在于 owned workdir。正式 `.md/.typ/.pdf` 不含原始照片绝对路径或 URL。current triple 移动后、旧 triple 进入 history 后，都能在没有原照片目录的环境中仅凭 skill-local fonts 独立重编译 `.typ`。

## 公开命令与恢复

```bash
skills/graduate-resume/scripts/graduate-resume.sh render \
  --input graduate-resume.md --generic \
  --delivery-root delivery

skills/graduate-resume/scripts/graduate-resume.sh render \
  --input graduate-resume.md --target target-grid-001 \
  --not-applicable target-grid-001 condition-0123456789abcdefabcd "招聘方确认本批次不适用" \
  --delivery-root delivery

skills/graduate-resume/scripts/graduate-resume.sh batch \
  --input graduate-resume.md \
  --allow-gap-target target-grid-001 \
  --delivery-root delivery
```

先检查预检 JSON，再以完全相同参数追加 `--confirm`。失败时先按稳定错误码修正事实、target ID、condition ID、覆盖冲突、gap allow、照片、字体、stem collision 或 delivery-root 异常，再重新运行预检；不要手工拼接 partial triple 或删除 `.work`/history 来绕过审计。

## Phase 49 边界

Phase 48 只证明本地开发环境的离线功能，不宣称已完成六 runtime 安装验收、聚合故障注入 authority、PDF 结构/布局 gate 或非开发环境字体人工 UAT。这些验收属于 Phase 49。
