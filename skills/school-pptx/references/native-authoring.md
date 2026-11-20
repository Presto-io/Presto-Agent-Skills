# 原生制作接口

依赖Python、python-pptx、Pillow、lxml。`SchoolDeck`专用于随技能提供的五页学校模板，第1–5页依次是封面、目录、章节、正文、尾页。工具路径相对于技能根，项目脚本可将其`scripts/`加入导入路径。

```python
import sys
sys.path.insert(0, "<skill-root>/scripts")
from school_native import SchoolDeck, text

deck = SchoolDeck()
deck.cover("课程建设汇报", "汇报人 · 日期")
deck.contents(["建设目标", "实施路径", "评价方式"])
deck.section(1, "建设目标")
slide = deck.content("把学习成果变成可验证的能力")
text(slide, "真实任务", 0.9, 2.3, 4.9, 0.7, size=28, bold=True)
text(slide, "明确动作、过程和验收依据。", 0.9, 3.2, 11.5, 1.2, size=26)
deck.closing()
deck.save("<project>/exports/课程建设汇报.pptx")
```

坐标单位英寸，字号pt。正文从y=2.15开始、在6.10之前结束。`content(..., kicker=...)`的可选提示位于正文顶部，使用时自行为其后的内容留空间。

- `text(slide, value, x, y, width, height, size=24, fill=INK, bold=False, align="left", name="text", family=FONT)`创建关闭隐式自动缩字并设置东亚字体的原生文本框。
- `rect(slide, x, y, width, height, fill=PALE, name="panel", rounded=False)`创建色块。
- `line(slide, x1, y1, x2, y2, fill=BLUE, width=2)`创建原生连接线。
- `picture(slide, path, x, y, width, height, fit="contain")`等比完整放置照片；`fit="cover"`等比裁剪填满区域，需复查关键内容。
- `cover`、`contents`、`section`、`content`、`closing`应用本技能统一页族；`section`的number用于调用语义，页面只显示标题。
- `closing()`生成固定尾页，附加内容写在`notes`中。
- `deck.presentation`和返回的`slide`均为python-pptx对象，可以直接添加原生表格、图表和组合。新增内容对象使用`school:`名前缀供检查识别。
- `save(path)`删除五张种子页、保留模板资产，拒绝覆盖已有文件；调用方安排目录和尾页。

使用用户自带模板时先盘点和预览，再编辑项目副本；不能把任意PPTX交给五页默认新建器并假定语义匹配。跨文稿复制、SmartArt、OLE、动画、视频需单独验证关系和行为。

检查调用`school_pptx.py check <file> --school-template`，预览调用`preview <file> --out-dir <empty-dir>`。用户自带模板时不加`--school-template`。预览可通过`--font-dir`加载本机字体，不修改系统字体配置。所有交付、脚本和检查证据写在项目目录。
