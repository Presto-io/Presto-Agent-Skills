---
phase: 48
slug: deterministic-targeted-rendering-clean-batch-delivery
status: passed
threats_open: 0
asvs_level: 2
created: 2026-07-19
---

# Phase 48 — Security

本审计只核验计划登记的威胁缓解是否存在于当前实现；不以 SUMMARY 或验证报告的声明替代代码证据。

## Threat Register

| Threat ID | Category | Component | Disposition | Status | Evidence |
|---|---|---|---|---|---|
| T-48-01 | Spoofing | condition evaluator | mitigate | closed | `graduate_resume_targeting.py:431-482` 仅受控谓词与 verified 字段产生 meets/gap。 |
| T-48-02 | Tampering | policy/override/projection | mitigate | closed | `graduate_resume_targeting.py:54-273, 237-241` 冻结模型、精确策略和 SHA-256 自校验。 |
| T-48-03 | Information Disclosure | trace/matrix | mitigate | closed | `graduate_resume_targeting.py:165-181` 将公开摘要与隐藏 evidence matrix 分离。 |
| T-48-04 | Repudiation | gap allow | mitigate | closed | `graduate_resume_targeting.py:431-472` allow 只匹配本次 target ID。 |
| T-48-SC | Tampering | package supply chain | accept | closed | 计划 `48-01-PLAN.md` 已声明不新增依赖；见本文件 Accepted Risks Log。 |
| T-48-05 | Tampering | Markdown/YAML/Typst emitters | mitigate | closed | `graduate_resume_final_markdown.py:25,145` 和 `graduate_resume_typst.py` 执行 schema/来源复验及转义。 |
| T-48-06 | Information Disclosure | photo emission | mitigate | closed | `graduate_resume_layout.py:531-579` no-follow 照片快照；`graduate_resume_typst.py` 内嵌规范化 PNG bytes。 |
| T-48-07 | Tampering | safe stem | mitigate | closed | `graduate_resume_render.py:35-36,285-325` 拒绝敏感标识、路径字符并预检 stem。 |
| T-48-08 | Denial of Service | render matrix | mitigate | closed | `graduate_resume_render.py` 的固定主题矩阵、输入限制及编译失败清理；`test_render_contract.py` 矩阵失败用例通过。 |
| T-48-09 | Information Disclosure | evidence/public split | mitigate | closed | `graduate_resume_render.py:200-263` evidence 使用独立 no-follow 根；候选集仅管理 triples。 |
| T-48-SC | Tampering | package supply chain | accept | closed | 计划 `48-02-PLAN.md` 的既有依赖接受声明；见 Accepted Risks Log。 |
| T-48-10 | Tampering | root/current discovery | mitigate | closed | `graduate_resume_delivery.py:255-409` held root、O_NOFOLLOW、exact triple discovery。 |
| T-48-11 | Elevation of Privilege | replace/unlink | mitigate | closed | `graduate_resume_delivery.py:359-409,674-676` 仅受管名称且全部 dir_fd 操作。 |
| T-48-12 | Repudiation | history | mitigate | closed | `graduate_resume_delivery.py:474-488,541-562` approved digest 与完整 history triples。 |
| T-48-13 | Denial of Service | interrupted publication | mitigate | closed | `graduate_resume_delivery.py:614-630` whole-set rollback；事务信号/故障测试通过。 |
| T-48-14 | Information Disclosure | root pollution | mitigate | closed | `graduate_resume_delivery.py:18,359-409` 根只允许 managed、`history`、`.work`。 |
| T-48-SC | Tampering | package supply chain | accept | closed | 计划 `48-03-PLAN.md` 明确 stdlib-only；见 Accepted Risks Log。 |
| T-48-15 | Spoofing | CLI hard conditions | mitigate | closed | `graduate_resume_cli.py:900-918` 只发布 evaluator 的有界状态，target evidence 单独处理。 |
| T-48-16 | Tampering | confirmation snapshot | mitigate | closed | `graduate_resume_cli.py:839-847,973` 与 `graduate_resume_delivery.py:632-641` 重算并比对 digest。 |
| T-48-17 | Information Disclosure | public CLI/root | mitigate | closed | `graduate_resume_cli.py:992` 有界响应；delivery exact-set 拒绝中间文件。 |
| T-48-18 | Denial of Service | batch orchestration | mitigate | closed | `graduate_resume_cli.py:924-974` 先完整生成候选，随后才 publish。 |
| T-48-19 | Elevation of Privilege | CLI delivery paths | mitigate | closed | `graduate_resume_cli.py:909-974` 委托 `DeliverySession`，未直接替换或删除。 |
| T-48-SC | Tampering | package supply chain | accept | closed | 计划 `48-04-PLAN.md` 明确无新增安装；见 Accepted Risks Log。 |
| T-48-G05-01 | Elevation of Privilege | fact ID to Typst | mitigate | closed | `graduate_resume_cli.py:499-505` 稳定 ID 校验；Typst emitter 再转义。 |
| T-48-G05-02 | Information Disclosure | declined facts | mitigate | closed | `test_render_contract.py` 的 declined fact final checkpoint 回归通过。 |
| T-48-G05-03 | Tampering | structured serializer | mitigate | closed | `test_render_contract.py` 的 unsafe structured value 拒绝回归通过，生产 emitter只消费受控字段。 |
| T-48-G05-04 | Spoofing | explicit photo mode | mitigate | closed | `graduate_resume_cli.py:535-540` 受控 photo 状态；CLI photo mode 负例回归通过。 |
| T-48-G05-05 | Tampering | assets/delivery paths | mitigate | closed | `graduate_resume_layout.py:531-579` 与 `graduate_resume_delivery.py:255-409` no-follow/candidate-first。 |
| T-48-G05-SC | Tampering | package supply chain | accept | closed | 计划 `48-05-PLAN.md` 声明仅复用既有依赖；见 Accepted Risks Log。 |
| T-48-G06-01 | Information Disclosure | condition public projection | mitigate | closed | `graduate_resume_targeting.py:165-181` allowlisted public rows；private evidence 另存。 |
| T-48-G06-02 | Tampering | condition evidence | mitigate | closed | `graduate_resume_render.py:230-263` 保存前后按 canonical/projection/condition digest 绑定。 |
| T-48-G06-03 | Elevation of Privilege | evidence/history paths | mitigate | closed | `graduate_resume_render.py:57-228`、`graduate_resume_delivery.py:328-409` held no-follow descriptors。 |
| T-48-G06-04 | Tampering | historical stems | mitigate | closed | `graduate_resume_delivery.py:328-359` history 以安全 grammar/exact triple 检查。 |
| T-48-G06-05 | Tampering | preflight-confirm TOCTOU | mitigate | closed | `graduate_resume_delivery.py:474-488,632-641` 重算 candidate/current/mode/delta digest。 |
| T-48-G06-06 | Denial of Service | removed history | mitigate | closed | `test_delivery_transaction.py` 的 removed history reopen/no-op 回归通过。 |
| T-48-G06-SC | Tampering | package supply chain | accept | closed | 计划 `48-06-PLAN.md` 无新增包或网络依赖；见 Accepted Risks Log。 |
| T-48-G07-01 | Spoofing | parse_metadata | mitigate | closed | `graduate_resume_cli.py` exact metadata/重复字段验证；`test_phase48_cli.py` canonical reader 回归通过。 |
| T-48-G07-02 | Tampering | canonical input | mitigate | closed | `graduate_resume_cli.py:192-268` O_NOFOLLOW 单次 bounded source snapshot 与 SHA-256。 |
| T-48-G07-03 | Repudiation | final/approval metadata | mitigate | closed | `graduate_resume_cli.py:124,238,847,915` 共用 `source_sha256`。 |
| T-48-G07-04 | Denial of Service | canonical reader | mitigate | closed | `graduate_resume_cli.py:192-268` regular-file、UTF-8、长度与 identity 检查。 |
| T-48-G07-SC | Tampering | package supply chain | accept | closed | 计划 `48-07-PLAN.md` 不新增安装/联网；见 Accepted Risks Log。 |
| T-48-G08-01 | Tampering | photo asset | mitigate | closed | `graduate_resume_layout.py:531-579` held root + descriptor-relative O_NOFOLLOW + bounded snapshot。 |
| T-48-G08-02 | Spoofing | Typst source | mitigate | closed | `graduate_resume_typst_runtime.py:38-64,176-247` bounded symlink chain、source fd、exact version。 |
| T-48-G08-03 | Tampering | executable substitution | accept | closed | 用户于 2026-07-20 明确接受同 UID 在本机校验后替换 Typst 快照的风险。`graduate_resume_typst_runtime.py` 仍在启动前验证快照 identity/SHA-256、版本及输出上限，但普通路径执行不承诺关闭该竞态。见 AR-48-07。 |
| T-48-G08-04 | Information Disclosure | final Typst | mitigate | closed | `graduate_resume_typst.py` 只消费 normalized PNG bytes；照片/路径泄露回归通过。 |
| T-48-G08-05 | Denial of Service | photo/tool output | mitigate | closed | `graduate_resume_typst_runtime.py:22-25,141-144` 限制 executable/run output；照片读取有上限。 |
| T-48-G08-06 | Repudiation | cleanup CLI result | mitigate | closed | `graduate_resume_delivery.py:704-795` 聚合 cleanup error；CLI cleanup 回归通过。 |
| T-48-G08-SC | Tampering | package supply chain | accept | closed | 计划 `48-08-PLAN.md` 不安装包，仅锁定本地 Typst；见 Accepted Risks Log。 |
| T-48-G09-01 | Information Disclosure | delivery root | mitigate | closed | `graduate_resume_delivery.py:18,359` `sources/assets` 不在 allowlist。 |
| T-48-G09-02 | Elevation of Privilege | support directories | mitigate | closed | `graduate_resume_delivery.py:18,372-409` 仅 held/no-follow `history` 与 owned `.work`。 |
| T-48-G09-03 | Repudiation | cleanup result | mitigate | closed | `graduate_resume_delivery.py:704-795` 收集阶段/errno 并抛出有界错误。 |
| T-48-G09-04 | Denial of Service | stale work/lock | mitigate | closed | `graduate_resume_delivery.py:372-404,770-795` stale `.work/.lock` fail-closed 且 cleanup 故障可见。 |
| T-48-G09-05 | Tampering | double failure | mitigate | closed | `graduate_resume_delivery.py:614-630,797-803` 先 rollback，再用异常链保留根因。 |
| T-48-G09-SC | Tampering | package supply chain | accept | closed | 计划 `48-09-PLAN.md` 无新增包/网络依赖；见 Accepted Risks Log。 |

## Accepted Risks Log

| Risk ID | Threat Ref | Rationale | Accepted By | Date |
|---|---|---|---|---|
| AR-48-01 | T-48-SC | Phase 48 plans declare no package installation, network dependency, or package mutation. | Phase 48 plan threat register | 2026-07-18 |
| AR-48-02 | T-48-G05-SC | Reuses existing Typst, PyMuPDF, Pillow only; no package installation. | Phase 48 plan threat register | 2026-07-18 |
| AR-48-03 | T-48-G06-SC | No package installation or network dependency. | Phase 48 plan threat register | 2026-07-18 |
| AR-48-04 | T-48-G07-SC | No package installation, networking, or external dependency. | Phase 48 plan threat register | 2026-07-18 |
| AR-48-05 | T-48-G08-SC | No package installation; only the declared local Typst 0.15.0 runtime. | Phase 48 plan threat register | 2026-07-18 |
| AR-48-06 | T-48-G09-SC | No package installation or network dependency. | Phase 48 plan threat register | 2026-07-18 |
| AR-48-07 | T-48-G08-03 | 同一登录用户主动篡改本机 Typst 的校验后替换窗口不属于 Phase 48 必须缓解的攻击模型；保持与其他技能一致的普通 Typst 路径调用，避免引入特权 helper 与管理员安装前置条件。 | 用户 | 2026-07-20 |

注：`T-48-SC` 在计划 01-04 中重复登记，以上同一接受决策覆盖四条同 ID 登记项。

## Summary Threat Flags

全部 9 份 `48-*-SUMMARY.md` 均没有 `## Threat Flags` 小节；未发现未映射的 executor threat flag。

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Auditor |
|---|---:|---:|---:|---|
| 2026-07-19 | 54 | 53 | 1 | gsd-security-auditor |
| 2026-07-20 | 54 | 54 | 0 | 用户接受风险后重新审计 |

## Accepted Runtime Risk

`T-48-G08-03` 的技术描述仍成立：私有目录的 `0700/0500` 权限不能消除同 UID 对快照文件的原地替换。用户已将其明确列为 Phase 48 可接受风险，因此本阶段使用普通用户权限下的已验证 Typst 快照路径启动。该决定不削弱 candidate-first、正式文件投递、证据、history 或 rollback 的安全边界。

## Sign-Off

- [x] 每项计划威胁均有 disposition 和审计状态。
- [x] 所有计划声明的接受风险已记录。
- [x] `threats_open: 0`。

**Approval:** passed with accepted risk AR-48-07 — 2026-07-20
