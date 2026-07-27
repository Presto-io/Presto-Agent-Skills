# Phase 53 真人 UAT 待填写模板

本文件是表单模板，不是 UAT 记录，也不能提交给 `--check-uat`。只有同次 public `verify` 成功产生 `evidence/verification.json`、`delivery/canonical.md` 与 `delivery/canonical.pptx` 后，才复制为 `53-UAT.md` 并用该次 SHA-256 填入。不得修改 artifact、换用其他运行的 evidence，或由 agent 填写真人字段。

## 生成绑定记录

1. 在独立 caller workdir 成功运行 `skills/school-pptx/scripts/school-pptx.sh verify --workdir <workdir>`，并运行 `python3 skills/school-pptx/scripts/verify_pptx_renderer.py phase-53`。任一命令非零即停止，不能生成可签署记录。
2. 只从 `<workdir>/evidence/verification.json` 读取 `delivery/canonical.md` 与 `delivery/canonical.pptx` 的 SHA-256；将对应 PPTX 复制或以 repository-relative 路径交给真人 viewer。记录中的 `evidence_source` 与 `delivery_pptx` 必须是 repository-relative 路径。
3. 复制以下 frontmatter 和表格到 `53-UAT.md`，替换所有 `<...>`。初始 `status` 必须为 `pending`，每项为 `PENDING`，且 viewer、版本、OS、时间、测试者、signoff、objects、observation、reference 全部为空。
4. 由真人在 Microsoft PowerPoint 或 WPS Presentation 中完成十项实际操作。每项填入物理页/对象和观察；截图只能作为辅助 reference。
5. 所有项均为 PASS 后，真人填写 `status: "passed"`、identity、signoff，并运行：

```bash
python3 skills/school-pptx/scripts/verify_school_pptx.py \
  --check-uat .planning/phases/53-complete-verification-runtime-docs-and-human-uat/53-UAT.md \
  --evidence <workdir>/evidence/verification.json
```

成功输出只能是 `UAT_RECORD_LINTED_HUMAN_CLAIM_UNVERIFIED`。它只验证记录与当前机器证据的绑定，不证明真人执行了操作，也绝不能由 CI、agent 或任何自动关闭流程解释为 UAT 通过。完成 lint 后，实际操作 viewer 的人类测试者或用户必须在命令之外明确确认记录真实性；该外部确认与记录共同构成接受依据。任何 `PENDING`、`FAIL`、`BLOCKED`、hash 不匹配或自动验证失败都阻止 Phase 53 接受。

## 可填写记录骨架

```markdown
---
status: "pending"
viewer: ""
viewer_version: ""
operating_system: ""
fixture_sha256: "<canonical-md-sha256>"
pptx_sha256: "<canonical-pptx-sha256>"
tested_at: ""
tester: ""
evidence_source: "<repository-relative-workdir>/evidence/verification.json"
delivery_pptx: "<repository-relative-delivery-pptx>"
signoff: ""
---

| ID | Check | Result | Physical slides / objects | Human observation | Evidence reference |
|---|---|---|---|---|---|
| UAT-V01 | 全套页面与四种新增构图的中文可读性、换行、裁切、重叠、溢出和续页 | PENDING |  |  |  |
| UAT-V02 | 目录条目、顺序、对齐、密度、留白和末页孤项 | PENDING |  |  |  |
| UAT-V03 | timeline 顺序、节点、文字高度、留白、主轴和 marker 对齐 | PENDING |  |  |  |
| UAT-V04 | 旧布局和四种新增构图的主题、字体、背景、footer 与主体样式一致性 | PENDING |  |  |  |
| UAT-V05 | bold/highlight、delimiter 隐藏、字符顺序、换行和连续编辑 | PENDING |  |  |  |
| UAT-V06 | 本地媒体 contain、比例、无拉伸/意外裁切，及适用 placeholder | PENDING |  |  |  |
| UAT-I01 | notes、logical expansion、可编辑性和画布隔离 | PENDING |  |  |  |
| UAT-I02 | 原生 table cell、续表 header/table name 和无关对象稳定 | PENDING |  |  |  |
| UAT-I03 | 原生 code text、编辑/撤销、空白换行与小标题独立编辑 | PENDING |  |  |  |
| UAT-I04 | timeline/gallery/process group 移动和取消组合；标注移动/编辑；hero/KPI 标签、数值、单位编辑/撤销 | PENDING |  |  |  |
```

`hero-evidence`、`annotated-image`、`process-overlay`、`kpi-evidence` 都必须在上表的 `Physical slides / objects` 与 `Human observation` 中出现；不能以一条总评、自动检查、缩略图、截图或 PDF 代替四种构图的真人操作。
