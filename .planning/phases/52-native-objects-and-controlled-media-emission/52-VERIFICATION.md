---
phase: 52-native-objects-and-controlled-media-emission
verified: 2026-07-24
status: complete
requirements: [OBJ-01, MEDIA-01]
---

# Phase 52 验证记录

四种新增构图均由冻结计划驱动原生形状、文本、连接线与 payload-only 图片生成。发射器拒绝 schema、mapping、variant 与媒体 hash 漂移；重开 PPTX 后未发现整页位图。

兼容运行时验证：

```text
PYTHONPATH=/tmp/presto-yaml-compat:skills/school-pptx/scripts \
  /Users/mrered/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3 \
  skills/school-pptx/scripts/verify_pptx_renderer.py phase-52
```

结果：四页、48 个形状、2,495,048 bytes；`hero-evidence`、`annotated-image`、`process-overlay` 与 `kpi-evidence` 均在重开后保留原生信息层，`whole_page_pictures=0`。

未覆盖：Phase 53 完整 fixture、公开 verification registry、runtime 文档与 hash-bound 真人 UAT。
