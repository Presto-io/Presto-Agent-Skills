# Skills

Canonical skills live here.

Current skills:

- `end-of-term-teaching-materials`: 期末教学提交材料和表格的 Markdown intermediate 到固定模板 Typst/PDF、deterministic table artifacts 和 workbook 的工作流。
- `gongwen`: 类公文 Markdown intermediate 到 Presto gongwen Typst/PDF 的工作流。
- `jiaoan-jihua`: 授课进度计划 Markdown intermediate 到 Presto jiaoan-jihua Typst/PDF 的工作流。
- `jiaoan-shicao`: 实操教案 Markdown intermediate 到 Presto jiaoan-shicao Typst/PDF 的工作流。

Expected layout:

```text
skills/
└── <skill-name>/
    ├── SKILL.md
    ├── references/
    ├── scripts/
    └── templates/
```

Only `SKILL.md` is required. Add supporting folders only when the skill needs them. Keep reusable support files like calendars, schemas, and long format notes under `references/`.

Before adding a new skill, copy `templates/skill/SKILL.md` and fill the runtime adapter table for all required runtimes.
