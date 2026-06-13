# Phase 20: Jiaoan Shicao 教案 1:1 Typst Conversion - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-14
**Phase:** 20-Jiaoan Shicao 教案 1:1 Typst Conversion
**Areas discussed:** 转换范围, 公共接口兼容, 目标 Typst 形态, 验证方式

---

## 转换范围

| Option | Description | Selected |
|--------|-------------|----------|
| 严格 fixture 1:1 | 只要求 `test/1.10/电气设备控制线路安装与调试教案.md` 生成严格匹配目标 `.typ` 的结果。 | ✓ |
| 泛化任意教案 Markdown | 将任意第三方教案 Markdown 都转换为同类 Typst 模板。 | |
| 依赖外部 renderer | 通过技能目录外的 Presto renderer 或模板二进制生成结果。 | |

**User's choice:** 用户在 Phase 20 命令中已锁定严格 fixture 1:1，并要求仅通过 `skills/jiaoan-shicao/scripts/` 内部脚本生成。
**Notes:** 泛化能力和共享 jiaoan 基础设施都留到后续阶段，不进入 Phase 20。

---

## 公共接口兼容

| Option | Description | Selected |
|--------|-------------|----------|
| 保持现有入口 | 保留 `jiaoan-shicao.sh render --input --typ --expected-typ` 等现有命令面。 | ✓ |
| 新增替代入口并弃用旧入口 | 用新的命令替代当前 render 工作流。 | |
| 只生成目标 fixture | 牺牲旧示例和 manifest/info/version 行为以最快匹配 fixture。 | |

**User's choice:** 由仓库要求和 Phase 20 验收推导为保持公共 workflow，除非在 `SKILL.md` 或 `references/` 中写窄兼容说明。
**Notes:** Planner 可设计 skill-local helper，但调用面应仍由 `skills/jiaoan-shicao/scripts/jiaoan-shicao.sh` 承担。

---

## 目标 Typst 形态

| Option | Description | Selected |
|--------|-------------|----------|
| 以目标 `.typ` 为固定合同 | 导入、字体、封面、表格、分页、评价表都必须按目标输出。 | ✓ |
| 只保证视觉近似 | 允许 Typst 源文本不同，只追求 PDF 看起来接近。 | |
| 沿用当前通用 Markdown 渲染 | 继续输出标题、段落、简单表格为主的通用 Typst。 | |

**User's choice:** Phase 20 目标要求严格匹配目标 `.typ`，因此目标 Typst 文件本身就是合同。
**Notes:** 当前脚本的 `--expected-typ` 基线检查失败，差异集中在文档 prelude、封面、表格、分页和节布局。

---

## 验证方式

| Option | Description | Selected |
|--------|-------------|----------|
| 严格文本比较 | 生成到临时或独立输出路径后，用 `--expected-typ`、`diff` 或 hash 证明与目标一致。 | ✓ |
| 仅编译 PDF | 只要 Typst 能编译成 PDF 即算通过。 | |
| 人工肉眼检查 | 人工查看输出即可。 | |

**User's choice:** 用户要求严格匹配目标 Typst；ROADMAP/REQUIREMENTS 允许 diff、hash 或 documented equivalence。
**Notes:** PDF 编译或视觉检查可作为补充，但不能替代 `.typ` 严格等价证据。

---

## Claude's Discretion

- 由 planner/executor 决定脚本是否继续单文件 Bash，或拆分为 `skills/jiaoan-shicao/scripts/` 内的 helper。
- 由 planner/executor 决定 fixture 版式常量放在脚本函数、数据表、reference 或 template 中，但最终转换命令必须只调用 skill-local script code。

## Deferred Ideas

- 泛化任意教案 Markdown。
- 在两个 jiaoan 技能之间抽取共享 renderer 基础设施。
- 将 PDF 视觉验收提升为 Phase 20 的主验收门槛。
