# 可选单页视觉样式

先使用主工作流校验 canonical 资料并生成最终 Markdown，再将该最终 Markdown 交给选样入口。脚本校验最终 Markdown 的内容散列、绑定与字段契约，不接受任意 JSON 或未经确认的简历事实。

```sh
python3 scripts/graduate_resume_styles.py --list
python3 scripts/graduate_resume_styles.py --input /path/to/final.md --style bauhaus --output /path/to/new-sample.pdf --typst /path/to/typst
```

完整目录为 `templates/visual-styles/catalog.json`，共 44 个唯一模板：基础三主题、风格合集 33 款、美图参考复刻 8 款。`--list` 列出全部目录；基础三主题沿用 `graduate-resume.sh render`，其余 41 款通过本入口生成单页选样。

`bauhaus`（包豪斯几何）、`network-topology`（弱电网络拓扑）、`timeline-copper`（铜色时间轴）采用已确认改版。`power-substation`（强电一次系统）、`signal-wave`（信号测量）、`pcb-traces`（弱电 PCB 走线）、`industrial-safety`（工业铭牌）、`brutalist`（先锋海报）保持原始排版；工业铭牌仅修正警示三角形内闪电居中。其余沿用现有样式。

八款参考复刻使用不含个人照片的背景图；照片由调用者显式提供并在运行时叠加，使用 contain 保持比例。该可移植照片适配与原先将特定人物嵌入背景的效果存在区别，不保证人物抠图或原背景逐像素一致。

包豪斯几何和网络拓扑用固定尺寸圆形、明确的文字高度度量及水平垂直对齐。默认保持已确认的位置；`--number-lift-pt 0.55` 可试用数字上移微调，范围 0–1 pt，只移动圆内数字。铜色时间轴保持圆点在上、编号在下，两者共用中线；不要将它误改成圆内编号。

照片模式须显式提供本地 `--photo`，无照片模式禁止额外照片。处理时去除 EXIF，仅在临时目录保存规范化照片。依赖 Python、PyYAML、Pillow、Typst 0.15.1 与 Poppler。字体使用技能内 Noto 字体和思源黑体／宋体，思源字体分别附带 SIL OFL 许可，来源为 Adobe Source Han Sans / Source Han Serif 项目。部分样式还需要合法安装的 Courier、Didot、Songti SC、Noteworthy、American Typewriter、Helvetica Neue 等系统字体，使用可重复的 `--font-path` 指定；系统字体不打包或重新分发。

输出只支持 A4 单页，检查文字内容、电话邮箱唯一性、12 mm 文字安全区和字体嵌入。无法容纳时失败，不降级删减内容。生成在临时目录，成功后以独占方式创建新 PDF；现有文件不会覆盖。不要把 PDF、照片或真实资料输出到技能仓库。选样 PDF 不携带三主题的自包含 Typst/Markdown triple，也不宣称兼容任意长度或多页资料。

用户审核选中某些页面或样式后，只修改明确指出的问题。保留前一版，另存改版与对照；不要因共用组件而改变已接受样式。放大检查所有编号的可见字形中心与圆形或方框中心，并检查标题、圆点、横线及正文起点；不能只凭编译成功判断居中。
