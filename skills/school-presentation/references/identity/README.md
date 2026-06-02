# School Presentation Identity References

本目录保存 `school-presentation` 技能使用的学校视觉识别资源。资源来自用户本机提供的 PPTX/POTX 模板，已按 skill-local 方式复制到 `images/`，供离线 HTML 渲染器内嵌或引用。

## Source Material

| Source | Type | Notes |
|--------|------|-------|
| `/Users/mrered/Desktop/双校名ppt模板（通用）.pptx` | PPTX | 提取校名组合 logo、英文 slogan、蓝绿色底图和装饰条。 |
| `/Users/mrered/Desktop/学院PPT模板.potx` | POTX | 用于核对同一视觉系统下的 theme palette、校徽/校名和装饰元素。 |

## Palette

主色来自 `学院PPT模板.potx` 的 `ppt/theme/theme1.xml`：

| Token | Hex | Use |
|-------|-----|-----|
| `school-green` | `#579E40` | 左侧渐变、强调块、进度图起点。 |
| `soft-green` | `#5E9768` | 次级绿色背景。 |
| `teal` | `#549183` | 蓝绿色过渡和图表中段。 |
| `blue-teal` | `#498B9E` | 标题装饰与分割线。 |
| `school-blue` | `#3E85B9` | 主要标题、按钮和图表。 |
| `bright-blue` | `#0084CC` | 页脚、链接、当前页标识。 |

`双校名ppt模板（通用）.pptx` 还提供了 `#4874CB`、`#75BD42`、`#30C0B4` 等兼容色，可在需要更强对比时使用。

## Assets

| File | Role |
|------|------|
| `images/logo-combined.png` | 校徽 + 中英双校名组合，适合封面和页脚。 |
| `images/school-icon-color.png` | 彩色校徽 icon（无校名），用于顶栏等紧凑位置。 |
| `images/logo-white.png` | 白色剪影校徽 + 中英双校名组合，渲染器默认用于封面深色背景。 |
| `images/slogan-en.png` | 英文 slogan：`LET EVERY STUDENT BECOME AN EXCELLENT CRAFTSMAN`。 |
| `images/slogan-white-script.png` | 白色手写风格 slogan，用于深色背景。 |
| `images/gradient-cover.png` | 绿到蓝渐变封面背景。 |
| `images/decorative-wave-top.png` | 顶部白底波纹装饰。 |
| `images/body-page-footer.png` | 正文页全宽页脚横幅，渲染器默认用于每个物理页底部。 |
| `images/logo-white.png` | 白色剪影校徽 + 中英双校名组合，渲染器默认叠放在正文页脚左侧。 |
| `images/school-icon-white.png` | 旧版白色校徽 icon，保留作兼容素材。 |
| `images/decorative-footer-band.png` | 旧版蓝绿色页脚/横幅装饰，保留作兼容素材。 |

## Provenance Rules

- 不把源 PPTX/POTX 作为技能运行时依赖；技能只依赖本目录中已提取的资源。
- 如需替换学校视觉，新增资源必须写入本目录并更新 `asset-manifest.json` 与本文件。
- 不得把用户没有提供的校名、校徽、题词或口号虚构为官方素材。
