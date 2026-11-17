# 可选单页视觉样式

先使用主工作流校验 canonical 资料并生成最终 Markdown，再将该最终 Markdown 交给选样入口。脚本校验最终 Markdown 的内容散列、绑定与字段契约，不接受任意 JSON 或未经确认的简历事实。

```sh
python3 scripts/graduate_resume_styles.py --list
python3 scripts/graduate_resume_styles.py --input /path/to/final.md --style bauhaus --output /path/to/new-sample.pdf --typst /path/to/typst
```

完整目录为 `templates/visual-styles/catalog.json`，共 44 个唯一模板：基础三主题、风格合集 33 款、美图参考复刻 8 款。`--list` 列出全部目录；基础三主题沿用 `graduate-resume.sh render`，其余 41 款通过本入口生成单页选样。

`bauhaus`（包豪斯几何）、`network-topology`（弱电网络拓扑）、`timeline-copper`（铜色时间轴）采用已确认改版。`power-substation`（强电一次系统）、`signal-wave`（信号测量）、`pcb-traces`（弱电 PCB 走线）、`industrial-safety`（工业铭牌）、`brutalist`（先锋海报）保持原始排版；工业铭牌仅修正警示三角形内闪电居中。其余沿用现有样式。

八款参考复刻使用不含个人照片的背景图；有照片时由 `graduate_resume_portrait.py` 在运行时生成透明抠图、黑白网点、相纸及各款装饰组合，保持人物比例。接收经透明度验证的 PNG、浅色纯背景或可可靠分离的均匀蓝/绿背景照片，无法可靠分离背景时明确失败，不能静默改成原始矩形照片。所有含人像的背景仅保存在临时目录，不进入技能资源。

包豪斯几何和网络拓扑用固定尺寸圆形、明确的文字高度度量及水平垂直对齐。默认保持已确认的位置；`--number-lift-pt 0.55` 可试用数字上移微调，范围 0–1 pt，只移动圆内数字。铜色时间轴保持圆点在上、编号在下，两者共用中线；不要将它误改成圆内编号。

照片模式须显式提供本地 `--photo`，无照片模式禁止额外照片。处理时去除 EXIF，仅在临时目录保存规范化照片。依赖 Python、PyYAML、Pillow、NumPy、Typst 0.15.1 与 Poppler。字体使用技能内 Noto 字体和思源黑体／宋体，思源字体分别附带 SIL OFL 许可，来源为 Adobe Source Han Sans / Source Han Serif 项目。装饰字体按顺序使用本机字体、Liberation 或技能内思源／Noto 字体回退。需要特定系统字体时使用可重复的 `--font-path` 指定；系统字体不打包或重新分发。

输出只支持 A4 单页，检查文字内容、电话邮箱唯一性、12 mm 文字安全区和字体嵌入。无法容纳时失败，不降级删减内容。生成在临时目录，成功后以独占方式创建新 PDF；现有文件不会覆盖。不要把 PDF、照片或真实资料输出到技能仓库。选样 PDF 不携带三主题的自包含 Typst/Markdown triple，也不宣称兼容任意长度或多页资料。

用户审核选中某些页面或样式后，只修改明确指出的问题。保留前一版，另存改版与对照；不要因共用组件而改变已接受样式。放大检查所有编号的可见字形中心与圆形或方框中心，并检查标题、圆点、横线及正文起点；不能只凭编译成功判断居中。

正式选样还检查每页至少 300 个非空白字符、文字纵向跨度至少 78%、文字占用行比例至少 30%。这些是空洞拦截下限，不代表通过即有良好视觉效果，仍须逐页检查内容分布。`STYLE_CONTENT_TOO_SPARSE` 时核对遗漏的已确认事实，调整字号与模块分配；不得虚构内容。`--allow-sparse-preview` 只用于诊断预览。

## 有限轮次的正文与字号策略（0.6.0）

1. 先读取目录中的每款 `content_policy`。`body_characters` 按最终 Markdown 的可见正文事实计算非空白 Unicode 字符，排除姓名、联系方式、ID、状态和模板标题；英文也逐字符计数。默认区间是单页启发式推荐值，双页基础主题的上限按页数扩展，实际结果由布局检测决定，不承诺只凭总字数就适配。字号上下限只针对正文，姓名、标题、联系方式和装饰不跟着放大。
2. 用已确认事实准备一次正文，不同模板可共享同一份完整正文。运行 `--recommend`。未满足推荐区间时，在不改变事实、熟练度或必留内容的前提下最多重组一次正文，再经 canonical validate/render 生成合法最终 Markdown；不能修改已签名的最终 Markdown。仍不满足时排除该模板，不要无休止扩写或压缩。离线脚本不调用模型、不代编事实，这一步由使用技能的 agent 完成。
3. `graduate_resume_styles.py` 对每款先用默认字号编译一次。Typst 实测栏/槽的自然高度、可用高度、模块间隔和未用高度；结合 PDF 的密度、安全区与页数。合格即采用。未铺满时字号增加 12%，溢出时减少 10%，均限制在该模板范围内，只再编译及复检一次。编译内部的 `measure` 是同次布局计算，不是额外生成正文或轮番试字号。字号不会通过无限增加行距或卡片内边距来补偿；矩阵内边距最多 8mm。
4. 第二次仍失败即 `STYLE_EXCLUDED_AFTER_ONE_ADJUSTMENT`，无正式 PDF 输出；后续不再重新调用同款重置预算。每个区域的模块间隔不得超过 18mm、尾部未用高度比例不得超过 22%；PDF 仍需满足原有每页 300 字、纵向跨度 78%、占用行 30% 下限。图片/页眉装饰区域不算正文空隙。固定槽的分栏分布差异也可能造成排除，这是预期结果。
5. `graduate_resume_style_collection.py` 消费准备好的最终 Markdown，先按推荐范围筛选，然后逐款执行上述两次上限。只合并通过者，输出 `qualified-styles.pdf` 和 `selection-report.json`，记录每次字号、Typst 测量、PDF 审计、排除原因及实际交付数量。无合格款则只输出报告，不生成空 PDF。目录中的 44 款保持不变，不能把“目录有 44 款”写成“交付一定 44 款”。

```sh
python3 scripts/graduate_resume_style_collection.py --input /path/to/final.md --recommend
python3 scripts/graduate_resume_style_collection.py --input /path/to/final.md --output /path/to/new-collection --photo /path/to/photo.png
# 可选加入已由原事务入口生成的基础主题；plan.json 是该主题 plan 命令的 JSON 输出。
python3 scripts/graduate_resume_style_collection.py --input /path/to/final.md --output /path/to/new-collection --canonical /path/to/conservative.md /path/to/plan.json
```

无照片稿省略 `--photo`。有照片稿必须显式提供。新输出目录必须不存在，防止覆盖旧版。合集需要 `pypdf`，其余依赖不变。基础主题的 `.pdf` 必须与 `FINAL_MD` 同名；检查同源完整事实、页面密度、字体安全区以及 `PLAN_JSON.frozen_layout` 的主题、页数与逐栏铺满。未提供或未通过的基础主题不会自动混入合集。

Hermes、OpenClaw、Codex 和其他 agent 共用此入口与停止条件。不要为了满足历史示例的 44/44 再循环调整；最后人工只检查合格款的重叠、裁切、编号居中和人像比例，发现问题可以排除，不能自动开启第三轮字号修正。纯总字数无法反映栏间分布，推荐区间应随合成回归样例逐步校准，不能用真实学生资料入仓。

批量交付与照片修复遵循 `revision-quality-contract.md`。明确请求套数时使用 `--expected-count N`，不要将目录数量、合格套数、个人数量和合订页数混为一谈。
