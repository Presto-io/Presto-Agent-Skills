---
phase: 48-deterministic-targeted-rendering-clean-batch-delivery
plan: 02
subsystem: graduate-resume-rendering
tags: [python, markdown-round-trip, typst, deterministic-rendering, embedded-photo, tdd]

requires:
  - phase: 48-deterministic-targeted-rendering-clean-batch-delivery
    plan: 01
    provides: 不可变 VersionProjection、共享 selected_fact_ids、条件摘要与 gap allow
  - phase: 47-controlled-themes-photo-frozen-layout
    provides: 三个登记主题、受控字体、冻结一/两页布局与照片 contain 策略
provides:
  - graduate-resume-delivery/v1 最终 Markdown 发射、重读与篡改绑定
  - 只从重读事实视图生成布局与正式 Typst/PDF 的机械渲染链
  - 413×579 PNG 照片规范化、EXIF/路径剥离与 Typst 内嵌字节
  - generic/target 三主题完整 triple 候选矩阵与安全 stem 碰撞预检
affects: [48-04-public-cli, graduate-resume-delivery, graduate-resume-batch]

tech-stack:
  added: []
  patterns: [reparse-before-compile, self-contained-typst, full-matrix-staging, normalized-stem-preflight]

key-files:
  created:
    - skills/graduate-resume/scripts/graduate_resume_final_markdown.py
    - skills/graduate-resume/scripts/graduate_resume_render.py
    - skills/graduate-resume/scripts/test_render_contract.py
    - skills/graduate-resume/fixtures/render/targeted-photo.md
  modified:
    - skills/graduate-resume/scripts/graduate_resume_layout.py
    - skills/graduate-resume/scripts/graduate_resume_typst.py

key-decisions:
  - "最终 Markdown 用精确 YAML 字段集、确定性正文事实 JSON 块、body SHA-256 与 binding SHA-256 形成可重读编译检查点。"
  - "正式 Typst 内联受控主题模板并内嵌规范化 PNG bytes，移动 triple 后不依赖模板文件或原始照片路径。"
  - "候选矩阵先在 owned stage 完成三主题九文件全量验证，再暴露 candidate；任一主题失败清除全部 partial files。"
  - "动态 stem 只消费姓名、单位、岗位与登记主题标签，统一 NFKC、受控字符、长度摘要和全矩阵碰撞预检。"

patterns-established:
  - "Final Markdown checkpoint: write -> reopen -> safe_load -> exact schema/body validation -> layout -> Typst -> PDF。"
  - "Public/evidence split: 正式 candidate 精确包含三件套，完整 projection 与 comparison 元数据只进入隐藏 evidence。"

requirements-completed: [TARGET-01, TARGET-03, DELIVERY-01]

duration: 17min
completed: 2026-07-18
---

# Phase 48 Plan 02: 确定性定向渲染与干净批量交付 Summary

**以可重读最终 Markdown 为唯一正式语义检查点，确定生成三主题自包含 Markdown/Typst/PDF 候选矩阵，并将照片规范化字节直接内嵌到可移动 Typst。**

## Performance

- **Duration:** 17 min
- **Started:** 2026-07-18T06:36:33Z
- **Completed:** 2026-07-18T06:53:23Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments

- 新增 `graduate-resume-delivery/v1` 冻结文档模型、确定性 emitter 与 exact-field loader；canonical/policy/version/theme/page/photo/target/trace/conditions/allow 和正文事实均被摘要绑定。
- 布局只消费共享 selected ID 投影；正式 Typst 只从重读后的 `FinalResumeDocument` 及匹配冻结计划发射，不补回 excluded facts、不评分、不重新判断资格。
- 使用锁定 Typst 0.15.0 将 JPEG/PNG 重栅格化为白底 contain 的 413×579 PNG，并以内嵌 bytes 取代照片源路径、URL 与 EXIF。
- 新增 generic/target 安全 stem、三主题固定展开、全矩阵碰撞预检、候选暂存与九文件 exact-set 验证。

## Task Commits

每个 TDD gate 均独立提交：

1. **Task 1 RED：最终 Markdown 失败契约** - `a9f7e4a` (test)
2. **Task 1 GREEN：最终 Markdown 重读检查点** - `1f4ea8e` (feat)
3. **Task 2 RED：布局与照片失败契约** - `0c7816d` (test)
4. **Task 2 GREEN：所选事实布局与自包含 Typst** - `1dd5c27` (feat)
5. **Task 3 RED：三主题矩阵失败契约** - `b9a16eb` (test)
6. **Task 3 GREEN：安全 stem 与完整候选矩阵** - `14bb335` (feat)

## Files Created/Modified

- `skills/graduate-resume/scripts/graduate_resume_final_markdown.py` - final delivery schema、正文事实编码、binding 与 round-trip loader。
- `skills/graduate-resume/scripts/graduate_resume_layout.py` - selected fact view 与真实三主题 layout feedback adapter。
- `skills/graduate-resume/scripts/graduate_resume_typst.py` - 重读文档机械发射、模板内联、照片规范化与 PNG bytes 内嵌。
- `skills/graduate-resume/scripts/graduate_resume_render.py` - safe component/stem、三主题矩阵、暂存编译、exact-set 验证与失败清理。
- `skills/graduate-resume/scripts/test_render_contract.py` - 5 项 round-trip、篡改、照片、命名、矩阵和 partial-failure 回归。
- `skills/graduate-resume/fixtures/render/targeted-photo.md` - 定向照片渲染字面 fixture。

## Decisions Made

- 正文事实采用每事实一个确定性 JSON fenced block；YAML 只公开索引、计数和 digest，不复制逐事实理由或完整 condition matrix。
- Phase 47 的 `__verified__` emitter 调用保留为相邻回归兼容入口；Phase 48 正式 render service 始终执行 Markdown write/reopen 后的 `FinalResumeDocument` 路径。
- comparison 页数只记录在 `.render-evidence`，每个版本与主题仅生成一个正式主页面 triple。
- 正式 `.typ` 内联 `resume-themes.typ` 的受控视觉定义，避免移动 current/history triple 后出现模板相对路径依赖。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] 保留 Phase 47 已验证 emitter 测试兼容入口**
- **Found during:** Task 2（收紧布局与 Typst）
- **Issue:** 计划级验证明确要求既有 Phase 47 layout/theme tests 继续通过，而旧测试通过 `__verified__` dict 调用 emitter。
- **Fix:** 正式 Phase 48 render 仅使用重读 `FinalResumeDocument`；同时保留受标记旧测试入口，未标记 canonical dict 仍稳定拒绝。
- **Files modified:** `skills/graduate-resume/scripts/graduate_resume_typst.py`
- **Verification:** 17 项指定布局/渲染测试与 47 项 graduate-resume 全量测试通过。
- **Committed in:** `1dd5c27`

---

**Total deviations:** 1 auto-fixed（1 blocking compatibility）
**Impact on plan:** 不改变正式渲染链或公开交付语义，仅保持 Phase 47 回归可执行。

## Issues Encountered

- 首个 1×1 手写 PNG 测试样本未被 Typst 解码；测试改用仓库已审阅照片 fixture bytes，规范化仍完全在临时目录完成且未新增依赖。
- 照片移动重编译检查的首次临时脚本存在 `str(...).resolve()` 调用错误；修正验证脚本后通过，不涉及仓库代码。

## Known Stubs

None. 扫描命中的空列表和空映射仅为内部构建容器，不流向正式输出或 UI。

## Threat Review

- T-48-05：YAML 精确字段集、safe_load、正文重建、selected ID 顺序与 binding SHA-256 阻断元字符和单点篡改。
- T-48-06：正式照片使用受控输入 bytes 重栅格化，输出验证 PNG IHDR 且扫描 EXIF、路径和 URL；`.typ` 只含 PNG bytes。
- T-48-07：stem 使用 NFKC、受控字符、长度限制与全矩阵碰撞预检，不接受联系方式、身份证或 source URL。
- T-48-08/T-48-09：三主题在 owned stage 全部成功后才进入 candidate；正式 exact set 拒绝 preview/evidence 和 partial triple。
- 未发现计划威胁模型之外的新网络、认证、外部依赖或持久化 schema trust boundary。

## Verification

- `python3 -m unittest skills/graduate-resume/scripts/test_layout_contract.py skills/graduate-resume/scripts/test_layout_fixtures.py skills/graduate-resume/scripts/test_render_contract.py -v`：17/17 PASS。
- `python3 -m unittest discover -s skills/graduate-resume/scripts -p 'test_*.py' -v`：47/47 PASS。
- `python3 -m py_compile ...graduate_resume_final_markdown.py ...graduate_resume_layout.py ...graduate_resume_typst.py ...graduate_resume_render.py ...test_render_contract.py`：PASS。
- 照片版三主题生成 9 个非空 managed files；复制单个 `.typ` 到无原图/无模板目录后重编译两次 PDF bytes 相同，SHA-256 为 `5e6a5e6644bec8e85e7300c99c9c6350ab1d8fe618570d59627253fd00aa7b53`。
- `git diff --check a9f7e4a^..14bb335`：PASS。

## TDD Gate Compliance

- RED：`a9f7e4a`、`0c7816d`、`b9a16eb` 均在对应实现前稳定失败。
- GREEN：`1f4ea8e`、`1dd5c27`、`14bb335` 分别使对应专项与相邻回归通过。
- 无需额外 REFACTOR 提交。

## User Setup Required

None - no external service configuration or package installation required.

## Next Phase Readiness

- 48-04 可按 `RenderMatrix.managed_files` 与显式 safe stems 将完整候选交给 48-03 `DeliverySession`。
- generic 与单 target 均已具备固定三主题展开；batch coordinator 只需组合全部确认投影并选择 patch/authority 事务。
- 无阻塞项；Phase 47 未提交规划/验证文件保持原样。

## Self-Check: PASSED

- 六个 plan-owned key files 均存在。
- 六个 TDD commits 均可在 git history 中找到。
- 17 项指定测试、47 项全量测试、照片移动重编译与 diff check 全部通过。
- Phase 47 三个脏文件未被修改、暂存或提交。

---
*Phase: 48-deterministic-targeted-rendering-clean-batch-delivery*
*Completed: 2026-07-18*
