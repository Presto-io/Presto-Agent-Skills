---
phase: 47-controlled-themes-photo-frozen-layout
plan: "01"
subsystem: graduate-resume controlled visual inputs
tags: [graduate-resume, typst, fonts, photo-safety, themes]
requires: [phase-46-resume-schema]
provides: [controlled-font-manifest, visual-theme-registry, safe-local-photo-resolution, typst-theme-skeleton]
affects: [graduate-resume-layout, phase-47-plan-02, phase-47-plan-03]
tech-stack:
  added: [Noto Sans Mono CJK SC static OTF, Typst]
  patterns: [frozen-dataclass, hash-verified-assets, no-follow-local-path-resolution, de-identified-projection]
key-files:
  created:
    - skills/graduate-resume/fonts/manifest.json
    - skills/graduate-resume/fixtures/layout/media/student-photo.jpg
    - skills/graduate-resume/scripts/graduate_resume_layout.py
    - skills/graduate-resume/templates/resume-themes.typ
  modified:
    - skills/graduate-resume/scripts/graduate_resume_cli.py
    - skills/graduate-resume/scripts/test_theme_contract.py
decisions:
  - 三个主题只持有视觉字段，事实 schema 与已验证事实投影不参与主题注册表。
  - 照片只以逻辑相对路径进入冻结计划；无照片投影不含路径、字节或元数据。
  - 受控字体在创建布局计划前同时验证清单、哈希和 Typst 可见性。
metrics:
  tasks_completed: 3
  commits: 5
  completed_date: 2026-07-18
---

# Phase 47 Plan 01: 受控主题、字体与照片边界总结

为 graduate-resume 固定三套纯视觉主题、可验证的 Noto Sans Mono CJK SC 资产，以及失败关闭的本地照片输入边界。

## 交付内容

- 新增受控的 Noto Sans Mono CJK SC Regular/Bold 静态 OTF、OFL 许可证、相对路径 SHA-256 清单和无 EXIF 的非敏感 JPEG fixture。
- 以不可变 `ThemeSpec`、`PhotoFitPolicy`、`PhotoAsset` 和 `FrozenResumePlan` 固定 conservative、modern、expressive 的视觉参数、唯一照片槽及无照片补位。
- `plan` 在资料校验后解析主题、页数和照片覆盖；照片路径仅允许受控根内的普通本地图片，所有失败统一为稳定错误码且不暴露绝对路径。
- 新增 A4 Typst 主题骨架，提供 `fact-block`、不可拆的 `list-entry`、三套视觉 token 和受冻结策略控制的照片/无照片分支。

## 验证

- `python3 -m unittest skills/graduate-resume/scripts/test_theme_contract.py -v`：7 项通过。
- `skills/graduate-resume/scripts/graduate-resume.sh verify`：Phase 46 fixture 回归通过。
- `typst fonts --font-path skills/graduate-resume/fonts --ignore-system-fonts --variants`：受控 Regular 和 Bold 均可见。
- JPEG fixture 被 `file` 识别为 JPEG，前 256 字节不包含 EXIF/GPS/Creator/Artist 标记。

## 决策

- 主题可扩展，但新增项只能新增视觉注册信息，不能改写 `graduate-resume/v2` 或已验证事实。
- 默认照片策略为 contain、等比、禁止拉伸和禁止裁切；受控裁切必须由注册项显式声明安全区域契约。
- 字体、照片路径和计划投影均不依赖系统字体、网络资源或不受控的物理路径。

## 与计划的偏差

### 自动修正

**1. [Rule 1 - 资产真实元数据] 保留批准上游 Bold 的物理字重 700**
- **发现于：** Task 1
- **问题：** 计划将 semantic Bold 角色标为 600，但批准且未修改的 `NotoSansMonoCJKsc-Bold.otf` 在 Typst 中报告物理 OpenType 字重 700。
- **处理：** 保持原始 OFL 字体未修改；manifest 继续记录 UI 语义 600，字体门禁严格验证实际的 Regular 400 与 Bold 700 可见性，模板以 600 角色请求该静态 Bold。
- **影响：** 不使用系统回退，不伪造或改写字体元数据。
- **提交：** `0393f79`、`14b4509`

## 已知占位

无。照片 fixture 是故意的单像素非敏感测试资产，不进入用户输出或候选人事实。

## 自检：通过

- 已确认字体清单、JPEG fixture、布局模块和 Typst 模板均存在。
- 已确认 `0393f79`、`a6eddc7`、`14b4509`、`38bc3cd`、`2d43045` 五个任务提交均存在。
