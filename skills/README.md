# Skills

Canonical skills live here.

Current skills:

- `party-member-study-notes-cn`: 从学习材料与已确认个人经历起草、审阅党员学习笔记、心得体会和组织生活记录；默认优先依赖 `gongwen` 交付 PDF，不可用时用已有 PDF 工具兜底，并保留 Markdown 源稿，不计入六技能自动发布覆盖。

- `vocational-practical-exam`: 职业技能等级认定实操出题、逐字母版重构、评分表与只读 DOCX 审计。
- `vocational-theory-exam`: 职业技能等级认定理论命题、多套等值卷及独立答案评分文件。
- `vocational-exam-package`: 显式依赖并复用前两项技能，统一套号、版本、成员集合与整包验收；安装时需三项完整目录。

职业认定技能安装须携带二进制母版：实操技能内两份用户原始 DOCX，理论技能内考生卷和答案两份派生 DOCX。试卷包复用依赖中的模板，不保留分叉副本；理论派生模板尚待用户人工版式审阅。

- `end-of-term-teaching-materials`: 期末教学提交材料和表格的 Markdown intermediate 到固定模板 Typst/PDF、deterministic table artifacts、calculated score evidence 和 workbook 的工作流。
- `graduate-resume`: `0.3.2` 毕业生简历工作流；真实资料校验后，离线生成通用或定向的三主题 Markdown/Typst/PDF，支持实际排版测量、强制双栏主题、网格信息栏、图标与岗位词组强调，以及预检、确认发布和完整三件套历史。Phase 49 完整验收、六 runtime 安装与人工 UAT 仍需独立证据；真实学生资料及成品严禁进入仓库。
- `gongwen`: 类公文 Markdown intermediate 到 Presto gongwen Typst/PDF 的工作流。
- `school-presentation`: 学校正式汇报、课程展示、培训课件、招生宣讲或项目答辩材料的 Markdown logical-slide intermediate 到离线 HTML 演示文稿的工作流；生成物内置 preview、overview、playback、presenter markup、课堂交互/结构化版式和一键最终 PDF 导出。
- `school-pptx`: 已审阅 Markdown logical slides 到受控模板、原生可编辑 PPTX 的工作流；public verify 检查结构与负例，真实 PowerPoint/WPS UAT 仍由人类完成。
- `teaching-design-package`: 教学设计整包 Markdown intermediate 到授课进度计划表/教学设计方案/可选期末材料拆分 Typst/PDF status 的编排工作流；旧授课计划和实操教案版式已迁入 package-owned renderer，正常运行不依赖 sibling skill folders。
- `tiaokedan`: `调课单`/`调课说明` Markdown intermediate 到 skill-local Typst/PDF 的单表单工作流；Markdown 可省略标题、收文对象、表格序号列和表格后落款行，renderer 自动补默认值、序号和宋体加粗标题，教师确认 `tiaokedan.md` 后再运行 final render gate。

`end-of-term-teaching-materials`、`gongwen`、`school-presentation`、`school-pptx`、`teaching-design-package`、`tiaokedan` 六个技能构成当前 explicit managed clean-delivery coverage；`graduate-resume` 及其他未纳入该集合的技能不能据此声称已完成完整验收。六者都遵守同一 [canonical clean-delivery contract](../docs/clean-delivery-directory-contract.md)：完整 candidate 先验门，exact path-set+bytes 相同则 no-op，changed 将完整旧 bundle 放入同一 `history/<max+1>/`，handled failure 回滚，unknown/legacy/symlink/partial 状态在 mutation 前失败关闭。历史散乱产物只能通过 [audit → confirm → execute cleanup contract](../docs/agent-output-cleanup-prompt.md) 整理。

成功 delivery root 只包含技能声明的当前 Markdown、当前最终产物，以及按需存在的 `sources/`、`assets/`、`history/`、`.work/`。`sources/` 不由普通发布修改；只有显式 managed 且持续引用的 assets 随版本归档。manifest、status、model、log、diff、screenshot、staging、验证证据和失败产物不属于 current；调用方 verification workdir 也不等同 delivery root。

Expected layout:

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    ├── references/
    ├── scripts/
    └── templates/
```

Only `SKILL.md` is required. Add supporting folders only when the skill needs them.

`graduate-resume` 还必须保留 `fonts/`、`assets/icons/`、fixtures 和对应许可，不能只安装入口或脚本。任何技能目录都不是学生资料存储区；简历技能的仓库发布规则见 [repository-publication.md](graduate-resume/references/repository-publication.md)。

Directory ownership:

- `SKILL.md` is the lightweight semantic entry: trigger intent, objective, inputs, high-level process, Markdown intermediate, output overview, verification entry, safety boundary, and runtime adapter notes.
- `references/` holds progressive disclosure material: long format rules, artifact contract details, renderer notes, support resources such as calendars, UAT checklists, and troubleshooting.
- `scripts/` holds public helper commands and skill-local internal modules. Keep public command names, common flags, output filenames, manifest keys, and behavior stable when splitting scripts.
- `templates/` holds copyable Markdown intermediates, output scaffolds, or renderer templates. Do not mix long documentation into templates.

Artifact contract discovery:

| Skill | Markdown intermediate | Artifact contract |
|-------|-----------------------|-------------------|
| `end-of-term-teaching-materials` | `templates/end-of-term-full.md` | `references/data-contract.md`, `references/workflow-and-artifacts.md` |
| `graduate-resume` | `templates/graduate-resume.md` | `SKILL.md`, `references/schema-and-review-contract.md`, `references/targeted-render-delivery-contract.md`, `references/job-focused-writing.md`, `references/phase-49-verification-contract.md`, `references/repository-publication.md`, `scripts/graduate-resume.sh` |
| `gongwen` | `templates/gongwen-full.md` | `references/format-and-rendering.md` |
| `school-presentation` | `templates/school-presentation-full.md` | `references/authoring-and-layout.md`, `references/playback-and-export.md`, `references/verification-contract.md` |
| `school-pptx` | `scripts/school-pptx.sh example --out-dir <dir>` 生成 `fixtures/school-pptx-full.md` 与 companion media | `SKILL.md`, `references/markdown-contract.md`, `references/template-contract.md`, `references/template-editing.md`, `references/renderer-and-pagination.md`, `references/verification-contract.md`, `references/visual-uat.md`, `scripts/school-pptx.sh`, `templates/standard-school.pptx`, `templates/standard-school.manifest.yaml` |
| `teaching-design-package` | `templates/teaching-design-package-full.md` | `SKILL.md`, `references/format-and-orchestration.md`, `scripts/teaching-design-package.sh` |
| `tiaokedan` | `templates/tiaokedan.md` | `SKILL.md`, `references/markdown-contract.md`, `references/pdf-workflow.md`, `scripts/tiaokedan.sh` |

Before adding a new skill, copy `templates/skill/SKILL.md` and fill the runtime adapter table for all required runtimes.

Every skill that writes files must also follow `docs/clean-delivery-directory-contract.md`: keep only the current Markdown and current final deliverables at the delivery root, archive previous successful output sets together under `history/`, and clean temporary verification from `.work/`.
