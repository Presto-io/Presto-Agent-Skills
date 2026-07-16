# school-pptx Renderer and Pagination

本 reference 记录 Phase 41–43 已冻结的用户可见行为。Markdown 语法以 [markdown-contract.md](markdown-contract.md) 为准，模板所有权以 [template-contract.md](template-contract.md) 为准；本文件不复制 renderer 实现或重新定义 geometry。

## Logical Slides to Physical Slides

- Markdown 中每个显式 slide 是逻辑页；模板拥有的 `closing` 在末尾隐式追加。
- renderer 在创建 PPTX 对象前完成全部语义拆分，并冻结 logical→physical mapping；emitter 只机械消费冻结计划，不重新分页。
- `contents` 只展示无编号 `section` 标题并使用固定可读字号分页；普通正文按完整段落序列、列表、标题和代码边界分页。
- `table` 使用 `标题和内容` layout，按可用高度拆行，续页重复表头；表头深蓝、表体浅蓝，全部 cell 水平/垂直居中。
- `timeline` 保持绿到蓝主题渐变水平轴并跨物理页拆分，节点圆点按横轴位置使用对应插值色；`gallery` 每页最多四项且跨页时均衡分配；`image-text` 按主图扩页；dedicated `code` 保持可编辑等宽文本并均衡连续代码行的分页负载。
- 普通正文和横排内容页顶部标题使用两端对齐；目录正文额外垂直居中。时间线 time/title 水平垂直居中，description 垂直居中、水平左对齐；表格 cell 居中、代码左对齐、章节标题左下对齐。
- 每张物理页都必须包含非空演讲者备注。作者提供的 notes 随同一逻辑页生成的每张物理页复制；缺少 notes 时生成与标题/版式相关的简短提示，章节页概括直到下一章节前的内容，备注不进入可见画布。

## Editable Native Objects

- 正文、标题、代码、时间线文字和 gallery caption 是原生可编辑文本 shape。
- 表格是原生 PPTX table；时间线和 gallery 项使用可移动、可取消组合并继续编辑的原生组合对象。
- 时间线按 manifest 的 `max_items_per_page: 6` 分页，每页节点在全宽主轴上保持原顺序与均衡数量；time/title/description 为 20/20/16pt，marker 强制正圆且 node group 不做非等比缩放；主轴由 `accent6` 绿渐变到 `accent1` 蓝，marker 使用同位置插值色；gallery 使用 1/2/3/4 项居中 preset。
- renderer 新增的真实图片和图标是保持宽高比、默认不裁剪的 picture object，并统一写入 `a:effectLst/a:outerShdw` 外阴影；母版和 physical layout 自带图片保持第七版人工模板原样，不要求或补写阴影。
- `title-content` 中出现图片时，图片占用独立续页，不能以零高度附着到正文页或覆盖文字。
- bold 与受控 highlight 保留为 run-level 语义；普通 highlight 固定为主题蓝色底、`FFFFFF` 白字和粗体，视觉 token 仍由模板拥有。

## Template Ownership

所有槽位、子区域、文字预算、字体范围、颜色、装饰和 footer 行为来自 `templates/standard-school.manifest.yaml` 与 normalized template。Markdown 不得传入坐标、尺寸、字体、颜色、crop、footer 或动画控制。模板人工编辑后的允许/禁止操作见 [template-editing.md](template-editing.md)。

## Delivery Transaction and Best-effort Boundary

成功 current 的 exact DeliverySpec 包含同 stem reviewed `.md`、通过 `validate_staged_package()` 的 editable `.pptx`，以及 Markdown/PPTX 持续引用并已确认纳管的 `assets/<safe-relative-path>`。输入中的任意其他媒体、`sources/`、manifest、logical model、日志、诊断与 verification evidence 都不属于 current。legacy `media/` 不会被普通 render 静默迁移；只有确认式整理同时迁移文件、更新 Markdown 引用并重跑 renderer/reference gate 后，资源才可进入 `assets/`。

renderer 在 `.work/<run-id>/{candidate,rollback,evidence}` 内完成 pair 和 managed assets 的生成、PPTX package validation 与引用验证。candidate 和 current 的 exact relative path set 及 bytes 都相同才是 no-op，且 current inode/mtime 与 history 不变。changed publication 把旧 Markdown、旧 PPTX 和全部旧 managed assets 写入同一个 `history/<max+1>/`；归档 Markdown 的 `assets/...` 引用在该 sequence 内解析。

七类 handled fault 与 `INT`/`TERM` 在任一 artifact/assets replace 后恢复旧完整 bundle，删除本次 sequence/run，并保持既有 history 不变。单路径 `replace` 是原子的，但 whole bundle 不承诺跨路径硬原子、`SIGKILL` 或断电恢复。

无效输入或缺失媒体仍可在本次 owned work 内生成结构有效、可编辑且无警告页/水印的 best-effort deck，用于 bounded diagnostic；parser、plan 或 runtime diagnostics 非零时它绝不替换 current，并在收尾时清理。完整 public verification 与证据字段见 [verification-contract.md](verification-contract.md)，真实 PowerPoint/WPS 行为见 [visual-uat.md](visual-uat.md)，自动目录验证不得签署人工 UAT。
