# Phase 46 Baseline

本文件记录 `graduate-resume` 在 Phase 46 要冻结的范围，便于后续 Phase 47-49 继续实现。

## Deliverables

- skill-local `SKILL.md`
- canonical `graduate-resume.md` 模板
- 资料契约参考文档
- fixture 基线
- 公开 CLI 入口骨架

## Source Contract

Phase 46 的资料源现为 `graduate-resume/v2`：YAML frontmatter 只保留 `schema`、首页信息栏 `profile`、可选的本地 `photo` 路径和派生 `preferences`；教育、技能、证书、项目、实训、经历与 target 位于 Markdown 正文。省略 `photo` 即无照片。正文标题和条目边界表达模块语义，稳定 ID/复核状态以紧邻条目的 `resume` 注释保存；正文顺序不构成事实语义，后续布局容器由 renderer 派生。

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
- `plan` 现输出脱敏 `FrozenResumePlan`：受控主题、照片模式、精确 1/2 页、测量哈希和推荐/对照建议。可用 `graduate-resume.sh plan --theme <conservative|modern|expressive>` 明确选择保守稳妥 (conservative)、现代简洁 (modern)、个性设计 (expressive)。
- `verify` 先运行 skill-local schema fixture，再运行固定布局样张矩阵；受控 Typst 0.15.0 使用 skill-local 字体和 `--ignore-system-fonts` 编译，并在临时 workdir 中检查 A4、页锚点和 PNG 安全区。
- 可选 AI 整理模式只能产出待审阅草稿，不得混入 final CLI 主路径。

## Fixture Baseline

建议至少维护以下 fixture：

- `valid-photo-single-target.md`
- `valid-no-photo.md`
- `valid-generic-no-target.md`
- `valid-multi-target.md`
- `error-missing-required.md`
- `error-unknown-field.md`
- `error-duplicate-id.md`
- `error-pending-core-fact.md`
- `error-photo-invalid-path.md`
- `error-unconfirmed-target.md`

## Fonts And Dependencies

Phase 46 已冻结并公开以下“必须受控”的要求：

- 当前 `plan` / `verify` 会探测 `python3`、PyYAML 和 `typst` 是否可用，作为后续固定依赖基线。
- Typst 编译锁定 0.15.0。
- 中文字体必须作为 skill-local 受控依赖处理，不能依赖系统 fallback，并以 `--ignore-system-fonts` 编译。
- 照片槽位上限为 35 mm x 49 mm；默认 contain 等比、禁止拉伸，只有主题显式许可且主体安全区域完整时才可受控裁切。

## Next Phase Hand-Off

进入 Phase 47 前，应默认以下内容已稳定：

- 资料 schema 不再为主题切换而改写。
- YAML `photo` 是可选的本地路径；字段不存在即无照片。
- target 是独立 brief，不污染基础资料。
- fixture 能覆盖有照、无照、通用、多目标和关键失败边界。
- ThemeSpec/ThemeRegistry 可新增纯视觉主题，首批三种主题不是永久上限；新增主题不得改写 schema 或已验证事实。
- Phase 47 只交付冻结布局和临时样张证据。正式三件套、批量发布与历史/回滚留给 Phase 48，跨 runtime 与跨环境验收留给 Phase 49。
