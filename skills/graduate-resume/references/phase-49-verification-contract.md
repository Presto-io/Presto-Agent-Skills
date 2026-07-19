# Phase 49 验收契约

公开入口只有：

```text
graduate-resume.sh verify --workdir <caller-owned-dir>
graduate-resume.sh verify --workdir <caller-owned-dir> --resume <active_run_id>
```

`--workdir` 是调用方明确授权的证据根。首次调用只会创建 `runs/<active_run_id>/` 和根级
`active-run.json`；根已存在 locator 时必须提供完全一致的 `--resume`。不会选择 latest、创建
第二个 run 或消费另一 run 的 runtime/UAT 记录。JSON、Markdown、PNG、raw logs 和验收记录都只能
写在该 run；正式 delivery root 仍只允许同 stem 的 Markdown、Typst、PDF 三件套。

## 固定 Gate

以下顺序、ID 和分母固定，不能由目录、运行时或缺失的外部记录动态删减：

1. `P49-G01-release-prerequisites`
2. `P49-G02-schema-baseline`
3. `P49-G03-normal-photo`
4. `P49-G04-no-photo`
5. `P49-G05-multi-target`
6. `P49-G06-qualification-gap`
7. `P49-G07-content-pressure`
8. `P49-G08-publication-faults`
9. `P49-G09-pdf-png-physical`
10. `P49-G10-triple-metadata-name`
11. `P49-G11-six-runtime-install`
12. `P49-G12-canonical-docs`
13. `P49-G13-human-uat`
14. `P49-G14-evidence-mutation-guards`

聚合器必须保留每个 gate 的原始 exit code、stdout/stderr hash、重开产物观察、fixture、Typst
`0.15.0` 快照、受控字体清单及文件 hash。它独立重新计算 `required == called`、顺序、唯一性和
`dynamic_skips == []`；不信任生产者写入的 passed/count/hash/page/theme/photo 字段。

`P49-G01-release-prerequisites` 必须重新读取 Phase 48 的 review 和 security 报告：review 只能是
hash-fresh `clean` 或带批准依据的 `skipped`，九个既有 finding 均须处置；security 必须通过、
`threats_open: 0` 且报告列出的当前 source SHA-256 全部匹配。`48-VERIFICATION.md` 的历史 PASS
不能替代此 gate。

状态仅为 `passed`、`human_needed` 或 `failed`。在 Phase 49-01 中，缺少 six-runtime 或人工 UAT
记录是结构化失败，不能伪造为 `human_needed`；49-02 只能在所有其他 gate 已通过且合法 UAT
PENDING 是唯一未决项时给出 `human_needed`。
