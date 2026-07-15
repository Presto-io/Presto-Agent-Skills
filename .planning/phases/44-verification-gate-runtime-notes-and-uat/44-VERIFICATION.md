---
phase: 44-verification-gate-runtime-notes-and-uat
verified: 2026-07-16T04:55:00+08:00
status: passed
score: "12/12 requirements verified; 7/7 self-tests passed"
---

# Phase 44 验证报告

## 验证结论

Phase 44 的五条 ROADMAP 成功标准、12 项需求、公开 8/6/21 验证链、六 runtime 文档和哈希绑定 WPS UAT 均有 fresh evidence。公开 `verify --workdir` 在计划规定的 Python/PYTHONPATH 环境中退出 0，生成 13 logical → 26 physical 的 fresh canonical deck；UAT lint 返回 `UAT_PASSED`，最终 PPTX 与 UAT evidence 的 SHA-256 一致。

GAP-44-V01 已关闭。foundation 的 stale-PASS 分支不再手工伪造 gate status，而是生成真实完整的 passed candidate，再发布 failed rerun 验证旧 PASS 被替换。修复后 foundation 与其余六个 self-tests 全部通过，fresh public verify、UAT lint 和 artifact hash binding 继续通过。

## ROADMAP 成功标准

| # | 成功标准 | 状态 | Fresh evidence |
|---:|---|---|---|
| 1 | `verify --workdir` 运行 example、template、render 与结构检查 | VERIFIED | fresh public verify exit 0；固定顶层 registry 8/8、顺序一致、唯一、`dynamic_skips=0`。 |
| 2 | 证据覆盖依赖、页数、布局、分页、目录、notes、media、table、code 与整页截图禁令 | VERIFIED | fresh structure 为 13 logical / 26 physical；contents source/reopen 3/3；notes expected/observed 26/26；`whole_slide_picture_count=0`。 |
| 3 | 六个规定负例非零失败 | VERIFIED | fixed registry 6/6、顺序一致、唯一、`dynamic_skips=0`，六项均为 `failed-as-expected`。 |
| 4 | concise canonical `SKILL.md` 与 progressive references | VERIFIED | `docs-entry` 与 `docs-portability` self-tests 均通过；public evidence-integrity gate 通过。 |
| 5 | 仓库可发现性与六 runtime adapter notes | VERIFIED | README、skills index、directory spec、compatibility matrix 均包含 `school-pptx`；Codex、Claude Code、Gemini CLI、OpenCode、OpenClaw、Hermes Agent 六行 adapter 完整。 |

**ROADMAP success criteria：5/5 verified。**

## 需求覆盖

| Requirement | 状态 | Evidence |
|---|---|---|
| VER-04 | SATISFIED | fresh public `verify --workdir` exit 0；example、template、render、structure、Phase 43 regression、negative 与 integrity 全部执行。 |
| VER-05 | SATISFIED | fresh dependency gate 观察 CPython 3.12.13、python-pptx 1.0.2、Pillow 12.2.0、lxml 6.0.2、PyYAML 6.0.3；Pandoc 3.10 为 optional。 |
| VER-06 | SATISFIED | fresh structure 记录 13 logical、26 physical、layout parts、logical-to-physical mapping 和 3 条 source/reopen contents。 |
| VER-07 | SATISFIED | fresh structure gate 检查 notes 26/26、media、native tables、editable code/groups，并确认 `whole_slide_picture_count=0`。 |
| VER-08 | SATISFIED | unknown theme/layout、missing media、unsupported styling、unresolved marker、template/manifest mismatch 六负例全部按预期失败。 |
| VER-09 | SATISFIED | fresh transition evidence 为允许值 `none`，未转成 warning 或 failure。 |
| VER-10 | SATISFIED | `44-UAT.md` lint 返回 `UAT_PASSED`；WPS Presentation 12.1.26035 / macOS 26.5.2 的 UAT-V01..V06、UAT-I01..I04 共 10 项全部 PASS。 |
| SKILL-01 | SATISFIED | canonical `skills/school-pptx/SKILL.md` 包含 use-when、review-before-render、输入输出、安全与 public verify。 |
| SKILL-02 | SATISFIED | Markdown、template、renderer、verification 与 visual UAT 长契约均位于 `references/`。 |
| SKILL-04 | SATISFIED | 单一 adapter table 覆盖六 runtime 的发现、fallback、依赖、外部命令、权限、sandbox 与 workdir。 |
| SKILL-05 | SATISFIED | `README.md`、`skills/README.md`、`docs/directory-spec.md`、`docs/compatibility-matrix.md` 均可发现该技能。 |
| SKILL-06 | SATISFIED | canonical entry 提供学校/课程标题、metadata、theme、media、review markers、finalized state 六类按需澄清问题。 |

**Requirements：12/12 evidenced。**

## Fresh 自动验证

运行环境：

```bash
export SCHOOL_PPTX_PYTHON=/Users/mrered/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3
export PYTHONPATH=/Users/mrered/.cache/uv/archive-v0/I2PFDpRQMCS91p6l
export PYTHONPYCACHEPREFIX=/tmp/presto-pycache
```

公开验证：

```bash
skills/school-pptx/scripts/school-pptx.sh verify \
  --workdir /tmp/presto-phase44-verify-correct-env.EAJWOf
```

结果：`School PPTX verification passed`，exit 0。

| Registry | Required | Called | Unique | Dynamic skips | Result |
|---|---:|---:|---|---:|---|
| Top-level gates | 8 | 8 | true | 0 | PASS |
| Negative cases | 6 | 6 | true | 0 | PASS |
| Phase 43 nested gates | 21 | 21 | true | 0 | PASS |

Fresh canonical evidence：

- Markdown：8,881 bytes，SHA-256 `2a6fcd2dccbba738a3e0ea6681ac4915f013db3d5150e5a151d5dde17a2d257f`。
- PPTX：2,592,317 bytes，SHA-256 `ed99daa1b7a187a2adb57f9769c1ecf282bc48ad950309cfbef3805a8f9af963`。
- Structure：13 logical → 26 physical；contents source/reopen 3/3；notes expected/observed 26/26；transition `none`；whole-slide pictures 0。
- Fresh PPTX hash 与 `test/canonical-待UAT-第八版.pptx`、`test/school-pptx-uat-eighth/delivery/canonical.pptx` 完全一致。

## UAT 验证

```bash
"$SCHOOL_PPTX_PYTHON" skills/school-pptx/scripts/verify_school_pptx.py \
  --check-uat .planning/phases/44-verification-gate-runtime-notes-and-uat/44-UAT.md \
  --evidence test/school-pptx-uat-eighth/evidence/verification.json
```

结果：`UAT_PASSED`，exit 0。fixture 与 PPTX hash 均与 `44-UAT.md` frontmatter 和 evidence 指向的 delivery 匹配；真实 viewer、version、OS、tester、timestamp、10 个唯一检查项、observation 与 signoff 完整。

## Self-test 结果

| Self-test | 状态 |
|---|---|
| `foundation` | PASS |
| `dependencies` | PASS |
| `canonical` | PASS |
| `stable-diagnostics` | PASS |
| `docs-entry` | PASS |
| `docs-portability` | PASS |
| `negatives-integrity` | PASS |

## Gap Closure

### GAP-44-V01：foundation stale-PASS 自测与当前 evidence schema 漂移 — CLOSED

- **原始失败：** synthetic PASS 仅覆盖 gate status，没有提供当前 schema 要求的 structural、negative 与 Phase 43 evidence，因此被 `validate_candidate()` 拒绝。
- **修复：** stale-PASS 分支改用真实 `build_candidate(first_tree)`，先确认 status 为 passed，再发布当前完整 evidence；随后以 dependency fault candidate 发布 failed rerun。
- **关闭证据：** `foundation`、`dependencies`、`canonical`、`stable-diagnostics`、`docs-entry`、`docs-portability`、`negatives-integrity` 共 7/7 self-tests 通过；fresh public 8/6/21、`UAT_PASSED` 与最终 PPTX hash binding 均通过。

## Anti-patterns 与边界

- public verify 未安装依赖、未联网，所有 evidence path 保持相对 workdir；fresh run 未修改 skill source。
- `git diff --check` 对 Phase 44 skill/docs/planning 范围通过。
- 未发现整页截图、动态 gate skip、registry 漏项、UAT 自动填充或 hash 漂移。
- 本报告不把 public automatic PASS 替代为人工 UAT，也不把已通过 UAT 用来掩盖 foundation 自测失败。

## 最终状态

Phase 44 的五条 ROADMAP 成功标准、12 项需求、7 个 self-tests、fresh public 8/6/21、六 runtime 文档和哈希绑定 UAT 全部通过。阶段验证状态为 `passed`，可进入 v1.17 里程碑完成流程。
