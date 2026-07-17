# Phase 46 Baseline

本文件记录 `graduate-resume` 在 Phase 46 要冻结的范围，便于后续 Phase 47-49 继续实现。

## Deliverables

- skill-local `SKILL.md`
- canonical `graduate-resume.md` 模板
- 资料契约参考文档
- fixture 基线
- 公开 CLI 入口骨架

## CLI Boundary

Phase 46 冻结以下命令名，并已实现其中的基础离线能力：

- `validate`
- `target`
- `plan`
- `render`
- `batch`
- `verify`

约束：

- `validate`、`target`、`plan`、`render`、`batch`、`verify` 全部离线、零 token。
- `validate` 校验受限 schema、稳定事实 ID、必填资料、待确认事实、照片状态和 target 完整度。
- `target` 只输出归一化 target brief 摘要；无 target 时明确转为通用版。
- `plan` 输出 Phase 46 baseline plan、依赖探测和字体策略占位，不做最终布局。
- `verify` 运行 skill-local fixture 回归并报告 Python、PyYAML、Typst 与受控 CJK 字体策略基线。
- 可选 AI 整理模式只能产出待审阅草稿，不得混入 final CLI 主路径。

## Fixture Baseline

建议至少维护以下 fixture：

- `valid-photo-single-target.md`
- `valid-no-photo-declined.md`
- `valid-generic-no-target.md`
- `valid-multi-target.md`
- `error-missing-required.md`
- `error-unknown-field.md`
- `error-duplicate-id.md`
- `error-pending-core-fact.md`
- `error-photo-pending.md`
- `error-unconfirmed-target.md`

## Fonts And Dependencies

Phase 46 已冻结并公开以下“必须受控”的要求：

- 当前 `plan` / `verify` 会探测 `python3`、PyYAML 和 `typst` 是否可用，作为后续固定依赖基线。
- 后续 Typst 编译必须锁定版本。
- 中文字体必须作为 skill-local 受控依赖处理，不能依赖系统 fallback。
- 编译时应避免系统字体漂移，后续推荐 `--ignore-system-fonts`。

## Next Phase Hand-Off

进入 Phase 47 前，应默认以下内容已稳定：

- 资料 schema 不再为主题切换而改写。
- 照片状态明确，可区分 provided / pending / declined。
- target 是独立 brief，不污染基础资料。
- fixture 能覆盖有照、无照、通用、多目标和关键失败边界。
