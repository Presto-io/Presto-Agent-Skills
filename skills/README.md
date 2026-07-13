# Skills

Canonical skills live here.

Current skills:

- `end-of-term-teaching-materials`: 期末教学提交材料和表格的 Markdown intermediate 到固定模板 Typst/PDF、deterministic table artifacts、calculated score evidence 和 workbook 的工作流。
- `gongwen`: 类公文 Markdown intermediate 到 Presto gongwen Typst/PDF 的工作流。
- `school-presentation`: 学校正式汇报、课程展示、培训课件、招生宣讲或项目答辩材料的 Markdown logical-slide intermediate 到离线 HTML 演示文稿的工作流；生成物内置 preview、overview、playback、presenter markup、课堂交互/结构化版式和一键最终 PDF 导出。
- `teaching-design-package`: 教学设计整包 Markdown intermediate 到授课进度计划表/教学设计方案/可选期末材料拆分 Typst/PDF status 的编排工作流；旧授课计划和实操教案版式已迁入 package-owned renderer，正常运行不依赖 sibling skill folders。
- `tiaokedan`: `调课单`/`调课说明` Markdown intermediate 到 skill-local Typst/PDF 的单表单工作流；Markdown 可省略标题、收文对象、表格序号列和表格后落款行，renderer 自动补默认值、序号和宋体加粗标题，教师确认 `tiaokedan.md` 后再运行 final render gate。

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

Directory ownership:

- `SKILL.md` is the lightweight semantic entry: trigger intent, objective, inputs, high-level process, Markdown intermediate, output overview, verification entry, safety boundary, and runtime adapter notes.
- `references/` holds progressive disclosure material: long format rules, artifact contract details, renderer notes, support resources such as calendars, UAT checklists, and troubleshooting.
- `scripts/` holds public helper commands and skill-local internal modules. Keep public command names, common flags, output filenames, manifest keys, and behavior stable when splitting scripts.
- `templates/` holds copyable Markdown intermediates, output scaffolds, or renderer templates. Do not mix long documentation into templates.

Artifact contract discovery:

| Skill | Markdown intermediate | Artifact contract |
|-------|-----------------------|-------------------|
| `end-of-term-teaching-materials` | `templates/end-of-term-full.md` | `references/data-contract.md`, `references/workflow-and-artifacts.md` |
| `gongwen` | `templates/gongwen-full.md` | `references/format-and-rendering.md` |
| `school-presentation` | `templates/school-presentation-full.md` | `references/authoring-and-layout.md`, `references/playback-and-export.md`, `references/verification-contract.md` |
| `teaching-design-package` | `templates/teaching-design-package-full.md` | `SKILL.md`, `references/format-and-orchestration.md`, `scripts/teaching-design-package.sh` |
| `tiaokedan` | `templates/tiaokedan.md` | `SKILL.md`, `references/markdown-contract.md`, `references/pdf-workflow.md`, `scripts/tiaokedan.sh` |

Before adding a new skill, copy `templates/skill/SKILL.md` and fill the runtime adapter table for all required runtimes.

Every skill that writes files must also follow `docs/clean-delivery-directory-contract.md`: keep only the current Markdown and current final deliverables at the delivery root, archive previous successful output sets together under `history/`, and clean temporary verification from `.work/`.
