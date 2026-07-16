# Clean Delivery Deterministic Fixtures

本目录定义 Phase 45 跨技能黑盒 harness 的最小 fixture API。fixture 只在 `TemporaryDirectory` 或调用者显式提供的测试 root 中实例化；生产技能不得读取本目录。

## Snapshot Model

测试 snapshot 以 relative path 排序，记录对象 type、regular file bytes、SHA-256、size、mtime_ns、inode/device（可用时）和 symlink 自身 target。比较必须覆盖 path set 与 bytes；零 mutation 断言同时比较 hash、inode、mtime_ns 和 symlink target（平台不提供的字段可标记 unavailable，不得动态跳过 bytes/path checks）。

## Required Scenarios

- `unknown-user-file`：根目录含 `notes-private.txt` 和一个未声明最终产物；普通发布与 cleanup 未确认执行必须拒绝，文件 hash/inode/mtime 不变。
- `user-source`：`sources/original-notes.md` 代表用户唯一原始资料；首次发布、changed、identical、failure 与 cleanup audit 后 path+bytes+inode 均不变。
- `referenced-asset`：当前 Markdown 引用 `assets/diagram.png`；changed 发布后旧 Markdown 与旧 asset 必须一起进入同一 `history/<sequence>/`，归档引用可解析。
- `symlink-escape`：授权 root 内链接指向 root 外 sentinel；审计只记录链接自身，不读取或改变 sentinel，执行返回 `SYMLINK_ESCAPE`。
- `stale-work`：`.work/other-run/` 属于非本次运行；publisher 与 cleanup 均不得删除，普通发布按契约失败关闭。
- `changed-after-audit`：审计完成后修改一个 regular file bytes，并覆盖 inode-preserving 与 inode-changing 两种变体；旧 approval 必须返回 `STALE_SNAPSHOT` 且全树零 mutation。
- `legacy-confirmation`：`.teaching-design-package/`、`.tiaokedan/` 与 `media/` 均只能出现在需确认组，不得自动执行。

## Cleanup Fixture API

每个 cleanup case 提供：

1. `authorized_roots`：精确绝对测试 roots；
2. `before_snapshot`：audit 前的 path/type/bytes/identity snapshot；
3. `expected_groups`：三组 exact relative operations；
4. `approval`：绑定 snapshot digest、plan digest 和 exact operations 的 token/plan；
5. `expected_result`：`UNCONFIRMED_EXECUTION`、`STALE_SNAPSHOT`、`UNAUTHORIZED_ROOT`、`SYMLINK_ESCAPE`、`PLAN_MISMATCH` 或明确成功结果；
6. `after_snapshot`：拒绝时与 `before_snapshot` 完全相等，成功时只有 exact approved operations 发生变化。

第一阶段额外断言 subprocess 不调用 render/build/Git mutation，不创建 delivery sidecar，且所有原 path、bytes、hash、inode、mtime 与 symlink target 均保持不变。

可执行 fixture 由 `python3 test/clean-delivery/cleanup_protocol_runner.py --self-test` 在系统临时目录中实例化完整 delivery folder。它真实执行 `audit → approval → execute`，并固定验证 `UNCONFIRMED_EXECUTION`、approval/plan mismatch、`STALE_SNAPSHOT`、`SYMLINK_ESCAPE` 和未批准 unknown delete 全部零 mutation；最后只执行一条 snapshot-bound exact move。fixture 从不接收或扫描真实用户目录。

## Bundle Shapes

fixture API 至少能表达二文件 bundle（Markdown + 一个最终产物）和四文件 bundle（Markdown + 三个最终产物），并允许附加 managed `assets/`、不受管 `sources/`、既有 `history/001`/`history/003` 以及 owned/unrelated `.work` 条目。

## REVIEW 与 Verification 负向 Fixtures

中央 `report_validation_gate` 必须从临时文件构造并拒绝以下 REVIEW 变体：frontmatter 缺失或重复字段、未知 `depth/status`、`status: skipped`、重复或越界 `files_reviewed_list`、scope/count/total/status 不一致、缺少 Narrative section、CR-/BL-/WR-/IN- 位于错误 section、重复或未知 finding ID，以及缺少 reviewed-scope `File+line`、`Issue` 或 `Fix` 的正文。零项 severity section 可省略；若存在 structural pre-pass，`## Structural Findings (fallow)` 必须独立且先于 `## Narrative Findings (AI reviewer)`。

最终 Verification 负向 fixture 同样只在临时目录实例化，必须覆盖 requirement 缺失、重复、未知 ID、未知 enum、非整数或非零 exit、空 command/evidence/assertion、非 `passed` status、strict aggregate 非零，以及与 REVIEW status/critical-or-blocker/warning/info 不一致。任何负向 fixture 被接受都使 strict aggregate 非零，不得计作 skip 或 xfail。

模板与 canonical `SKILL.md` 中的 `- [ ]` 是供安装者或人工验收执行的检查项，不是里程碑执行状态。中央文档 gate 校验检查项语义和 runtime rows，但不得因为这些模板/清单保持未勾选就把自动回归误判为失败，也不得把未勾选项伪造为已完成证据。
