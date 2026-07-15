# Phase 45：实现模式映射

**映射日期：** 2026-07-16  
**范围：** 全技能干净交付目录标准化改造  
**结论：** 仓库没有现成的“完整多文件版本事务”可直接复用，但已经具备足够强的局部范式：`school-pptx` 提供 held directory descriptor、`O_NOFOLLOW`、inode identity、descriptor-relative `os.replace`、`fsync`、owned-temp cleanup 与故障注入；`teaching-design-package` 提供动态 `1+1+N` candidate producer、模块 registry、merge-order gate 与失败注入；`school-presentation` 提供 caller-owned verify workdir 和离线 HTML gate；`gongwen` 提供 shell-only renderer 与 `cmp` 类比较；`end-of-term-teaching-materials` 和 `tiaokedan` 提供可保留的内容验证/格式生成逻辑。Phase 45 应把这些模式组合成统一协议，但每个 skill folder 保持 self-contained，不增加 sibling skill 或仓库根运行时依赖。

## 1. 预计文件清单、职责与最接近 analog

下表是 planner 应考虑的预计创建/修改面；具体拆 plan 时可以调整 helper 文件名，但职责边界不应合并回 shell dispatcher 或 renderer 主体。

### 1.1 共享验证与清理流程

| 预计文件 | 操作 | 责任 | 输入 → 输出 | 最接近既有实现 |
|---|---|---|---|---|
| `test/clean-delivery/verify_clean_delivery.py` | 新建 | 跨六技能黑盒协议矩阵；只调用 public CLI，不成为生产运行时依赖 | fixture + 临时交付根 + fault env → assertion/PASS | `skills/school-pptx/scripts/verify_markdown_contract.py:39` 的 public subprocess wrapper、`:98` 的 `file_hashes()`、`:106` 的 `tree_snapshot()`；`verify_pptx_renderer.py` 的固定 gate registry 与 fault hooks |
| `test/clean-delivery/fixtures/` | 新建 | 最小 deterministic fixture：首次发布、变更、相同、unknown、symlink、history gap、referenced asset、cleanup audit | 版本化输入 → test-only roots | `skills/school-pptx/fixtures/` 的 canonical fixture ownership；禁止复用 `test/` 中既有巨大生成产物作为新 fixture |
| `docs/agent-output-cleanup-prompt.md` | 修改 | 把现有两阶段提示词收敛为正式、可复用的 audit→confirm→execute 契约；首次运行零 mutation | 授权 roots → 三组计划；确认 token/approved plan → approved operations | 当前文件 `:10-16` 授权范围、`:30-38` 安全禁令、`:40-72` 只读审计、`:74-95` 确认后执行与收尾 |
| `docs/clean-delivery-directory-contract.md` | 修改 | 冻结机器测试所需的协议细节：显式受管集合、unknown gate、同内容定义、history 编号、handled-failure rollback、并发锁与安全路径 | 通用语义 → 六技能实现/测试 authority | 当前文件 `:20-35` allowlist/支持目录与 `:39-62` revision/failure 已是语义源；Phase 45 只补足可执行细节，不引入 agent 私有语法 |

共享 harness 可以集中，生产 helper 不可集中。`test/clean-delivery/verify_clean_delivery.py` 可以知道六个入口，但 `skills/*/scripts/` 不得 import/call 它。

### 1.2 Python 技能

| 预计文件 | 操作 | 责任 | 输入 → 输出 | 最接近既有实现 |
|---|---|---|---|---|
| `skills/end-of-term-teaching-materials/scripts/end_of_term/delivery.py` | 新建 | skill-local fixed four-file transaction：安全 root、`.work/<run-id>`、lock、current discovery、candidate equality、history、rollback、cleanup | `DeliverySpec` + candidate paths → `first/identical/changed` result | `skills/school-pptx/scripts/pptx_render.py:44-56` capability check、`:59-74` safe stem、`:77-267` held-descriptor publisher |
| `skills/end-of-term-teaching-materials/scripts/end_of_term/_engine.py` | 修改 | 保留解析/计分/XLSX/Typst/PDF 生成；把 `deliver()` 改为向 candidate 生成并调用 publisher | reviewed Markdown → candidate four-file set → transaction | `:1367-1413` 是当前适配点；保留 `:1368-1373` content gate、`:1389-1396` calculated-score gate、`:1316-1354` deterministic XLSX writer、`:1357-1364` Typst compile |
| `skills/tiaokedan/scripts/delivery_transaction.py` | 新建 | skill-local two/three-file transaction；显式 optional PDF set、bounded mismatch evidence、同 stem/root 检查 | reviewed Markdown + candidate Typst/PDF → publish/history/no-op | 同上 `SecureRenderDestination`；`tiaokedan_renderer.py:404-449` 当前 render orchestration |
| `skills/tiaokedan/scripts/tiaokedan_renderer.py` | 修改 | parser/Typst renderer 保持；不再先删 PDF、不再直写 current；expected diff 留在 `.work` evidence，公开输出 bounded | `--input --typ [--pdf] [--expected-typ]` → candidate → publisher | 保留 `:420-425` contract parsing、`:430-447` expected/PDF gates、`:452-474` Typst compile/non-empty gate；替换 `:414-418` stale PDF unlink 与 `:427-428` direct write |
| `skills/school-pptx/scripts/pptx_render.py` | 修改或拆出 `delivery_transaction.py` | 把现有 pair publisher 扩为 lock/history/equality/rollback；parser/plan/runtime error 只保留 work evidence，不发布 current | Markdown bytes + staged validated PPTX → pair transaction | 本文件本身是 authority：`:89-115` held root、`:127-153` identity/collision、`:155-212` owned temp、`:214-244` replace/fault window、`:246-267` owned cleanup |
| `skills/school-presentation/scripts/school_presentation/delivery.py` | 新建 | Markdown+HTML bundle transaction；manifest 只进 evidence/explicit verify workdir；验证 asset reference 与 root allowlist | reviewed Markdown + rendered HTML + ephemeral manifest → pair transaction | `school-pptx` secure publisher；`school_presentation/_engine.py:4237-4264` 现有 render data 与 size evidence |
| `skills/school-presentation/scripts/school_presentation/_engine.py` | 修改 | 将 `render_deck()` 保持为 in-memory renderer；`cmd_render()` 改为 candidate-first；`cmd_verify()` 继续 caller-workdir 语义 | public render argv → candidate renderer → transaction；verify argv → explicit evidence tree | `:4237-4264` 适配点；`:4267` 起 verify workdir；`:4535-4655` offline/size/structure evidence |

Python helper 可以在各 skill 内采用相同接口和测试断言，但不能运行时跨 skill import。最小公共概念建议为 `DeliverySpec`、`DeliverySession` 和 `PublishResult`，而不是共享仓库根 module。

### 1.3 Shell / Node 技能

| 预计文件 | 操作 | 责任 | 输入 → 输出 | 最接近既有实现 |
|---|---|---|---|---|
| `skills/gongwen/scripts/gongwen_lib/delivery.sh` | 新建 | Bash-only transaction adapter：安全 root/stem、exclusive lock、candidate/rollback/history、`cmp -s`、trap rollback、fixed-name cleanup | `md/typ[/pdf]` explicit names → first/no-op/revision | `gongwen_lib/common.sh:42-48` shell copy、`:50-61` byte-line comparison；`commands.sh:33-60` public arg contract |
| `skills/gongwen/scripts/gongwen.sh` | 修改 | 只 source 新 library；仍保持薄 dispatcher | argv → `cmd_render` | 当前 `:11-18` responsibility-based sourcing 与 `:20-31` dispatch |
| `skills/gongwen/scripts/gongwen_lib/commands.sh` | 修改 | 将 reviewed Markdown、Typst、optional PDF 全部生成到 candidate；expected gate 先于 publish；强制 `--typ`/`--pdf` 同 root 同 stem | unchanged public flags → candidate → shell publisher | 当前 `:33-60`；保留 shell-only `render_markdown_to_typst`，替换 `:48` 直写、`:52` post-write compare、`:58` direct PDF compile |
| `skills/teaching-design-package/scripts/delivery-transaction.js` | 新建 | Node skill-local dynamic bundle publisher；从 model 的 explicit filename list 发现 candidate/current；拒绝 ambiguous prefix；history/rollback/cleanup | `public_delivery.expected_public_filenames` + candidate root → transaction result | `package-model.js:75-117` filename safety与完整集合；`school-pptx` 的 path/identity语义是安全目标，不照搬 Python API |
| `skills/teaching-design-package/scripts/package-model.js` | 修改 | 把 hidden work paths 从 `.teaching-design-package/` 相对语义改为 run-root 相对语义；保留 registry/public delivery authority | finalized Markdown → model including explicit public set | `:9-28` module registry、`:94-117` `buildPublicDelivery()`、`:1042-1056` model registry/public delivery |
| `skills/teaching-design-package/scripts/teaching-design-package.sh` | 修改 | `.work/<run-id>` orchestration、candidate generation/validation、调用 Node publisher；删除 normal/failure destructive cleanup；diagnostic commands写 explicit workdir | unchanged commands/flags → candidate/evidence → Node publisher | 保留 `:649-688` module compile/status producer、`:690-823` merge gate/fault injection、`:837-962` orchestration；删除/替换 `:204-242` broad cleanup 与 `:914-943` sequential root copy |

Node helper应使用 `fs.lstatSync`、`fs.openSync(..., O_NOFOLLOW)`（平台支持时）、`fs.renameSync`/`fs.copyFileSync` 的显式列表、`fs.fsyncSync`、`realpath`/inode dev+ino复核；缺少安全能力时 fail closed。不要用 `fs.rmSync(root, {recursive:true})`、glob、`find -delete` 或 `readdir` 结果直接作为 mutation 列表。

### 1.4 Skill 契约与仓库文档

| 文件 | 操作 | 责任 | 最接近既有实现 |
|---|---|---|---|
| 六个 `skills/<name>/SKILL.md` | 修改 | 每技能 exact root allowlist、受管集合、`sources/assets/history/.work` 生命周期、revision/no-op/failure、最小验证、六 runtime notes | `skills/school-pptx/SKILL.md:84-102` 是最完整 runtime 表；`templates/skill/SKILL.md:67-101` 已有 clean delivery/safety 骨架 |
| `skills/end-of-term-teaching-materials/references/workflow-and-artifacts.md` | 修改 | 固定四件套 artifact contract、minimal validators、history bundle | 当前文件既有 review/rendering contract |
| `skills/gongwen/references/format-and-rendering.md` | 修改 | md+typ 与 md+typ+pdf 两种 exact set、同 root/stem、安全发布 | `gongwen/SKILL.md:72-84` 当前公开三件套说明 |
| `skills/school-pptx/references/renderer-and-pagination.md`、`verification-contract.md` | 修改 | pair transaction、best-effort只在 work evidence、verify root非delivery、assets语义 | `renderer-and-pagination.md:32` 已区分 delivery/evidence；`verification-contract.md:8-20` 已定义 caller workdir |
| `skills/school-presentation/references/verification-contract.md`、`authoring-and-layout.md` | 修改 | Markdown+HTML current set、manifest evidence、assets替代media、offline/size gate | verification contract 当前 `verify --workdir` 与 manifest schema |
| `skills/teaching-design-package/references/format-and-orchestration.md` | 修改 | dynamic `1+1+N`、`.work` evidence、module/merge validation、移除 hidden-root exception | `package-model.js:94-117` 是机器文件名 authority |
| `skills/tiaokedan/references/pdf-workflow.md`、`markdown-contract.md` | 修改 | two/three-file set、expected/PDF gate先于发布、移除 `.tiaokedan/` 长期例外 | `tiaokedan/SKILL.md:90-105` 当前输出/验证说明 |
| `README.md`、`skills/README.md`、`docs/directory-spec.md` | 修改 | 六技能覆盖、统一目录协议、新技能继承点；删除旧 hidden诊断表述 | `README.md:132-157` contributor/shared contract；`skills/README.md:45-47` 新技能继承；`directory-spec.md:51-79` document workflow/ownership |
| `docs/compatibility-matrix.md` | 修改 | 六 runtime 通用写入安全边界 + 六技能具体依赖/fallback；OpenClaw/Hermes installation-time verification | 当前 `:5-35` recommended pattern/matrix、`:36-55` skill notes、`:90-106` OpenClaw/Hermes conservative wording |
| `templates/skill/SKILL.md` | 修改 | 新写文件技能默认要求 explicit managed set、candidate、history、failure cleanup、runtime permissions | 当前 `:67-101` 已有目录树和安全 checklist，Phase 45 应补 unknown gate/验证/显式 fallback |

`README.md`、matrix、template 和中央 harness 是 shared files，应由 foundation/finalization plan 单点拥有；并行 skill plans 只改自己的 folder，避免冲突。

## 2. 建议统一数据流

六个技能共同采用下面的数据流，差异只在 `candidate producer` 和 `minimal validators`：

```text
public CLI + reviewed Markdown
  -> derive explicit DeliverySpec
       root
       exact candidate managed names
       current-set discovery rule
       managed referenced assets
       allowed support dirs
       format validators
  -> open/hold safe delivery root
  -> acquire same-root .work lock
  -> create owned .work/<run-id>/{candidate,rollback,evidence}
  -> existing renderer writes candidate only
  -> existing content gate + format readability gate
  -> inspect current root without following symlinks
       unknown => bounded failure, zero current/history mutation
  -> compare exact relative-name set + bytes
       first => publish candidate
       identical => cleanup run, preserve current inode/mtime, no history
       changed => snapshot current, reserve next history, publish candidate
  -> post-publish exact-set + readability + reference check
  -> commit history and cleanup own run/empty .work
  -> release lock

handled failure / INT / TERM before commit
  -> restore exact old set from rollback
  -> remove only names created by this run
  -> remove newly reserved history sequence
  -> verify prior root/history hashes
  -> cleanup own run/lock
  -> non-zero bounded diagnostic
```

`sources/` 从不进入 normal publication mutation list。`assets/` 只有被当前 Markdown/最终产物明确持续引用、且由技能声明为 managed 的相对路径才进入 candidate equality/history；unknown assets 不能因“看起来像媒体”被自动归属。

## 3. Python 发布 helper：应复用的实现骨架

### 3.1 Capability 与安全文件名

直接 analog 是 `skills/school-pptx/scripts/pptx_render.py:44-74`：

```python
def secure_io_capabilities() -> tuple[str, ...]:
    # 检查 O_DIRECTORY / O_NOFOLLOW / dir_fd / replace src_dir_fd,dst_dir_fd

def validate_stem(stem: str) -> str:
    # 拒绝空值、.、..、NUL、/、\\、过长和目录部分
```

Phase 45 helper应把 `validate_stem` 推广为 `validate_relative_name`：允许显式多级 managed asset path，但每个 component 都必须满足同样约束；public artifact仍只允许单组件 root name。不要用 `Path.resolve()` 结果作为唯一防护，因为它会在检查后重新按路径查找，存在交换窗口。

### 3.2 Held root descriptor 与 identity

直接复用 `SecureRenderDestination.__enter__()`、`assert_root_identity()` 与 `assert_final_paths()` 的模式（`pptx_render.py:89-153`）：

- `lstat/stat(..., follow_symlinks=False)` 确认 root/entry 类型；
- `os.open(root, O_RDONLY|O_DIRECTORY|O_NOFOLLOW)` 持有 root；
- 保存 `(st_dev, st_ino)`；
- 每个关键阶段比较 path identity 与 held fd identity；
- 对所有 current/candidate/history/work component 使用 descriptor-relative 操作；
- 非 regular current、symlink、device、socket、duplicate group 均作为 unknown/collision fail closed。

这里应新增 held `.work`、run、candidate、rollback、history descriptor，而不是在进入 root 后继续用裸绝对路径进行 mutation。

### 3.3 Owned temp inode 与 replace

`pptx_render.py:155-212` 的 `_create_temporary()` / `assert_temporary()` 和 `:214-244` 的 descriptor-relative `os.replace` 可直接抽象：

```python
fd = os.open(name, os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
             0o600, dir_fd=directory_fd)
identity = (os.fstat(fd).st_dev, os.fstat(fd).st_ino)
# write, flush, fsync, re-stat without symlink
os.replace(temp_name, final_name,
           src_dir_fd=directory_fd, dst_dir_fd=root_fd)
os.fsync(root_fd)
```

Phase 45不能照搬当前 `publish()` 的“两次 replace 后无恢复”语义。每次 replace 后记录 completed name；任何后续 handled failure 都从 verified rollback snapshot 恢复全部旧 names，并删除 candidate-only names。

### 3.4 Owned cleanup

`pptx_render.py:246-267` 是正确下限：只删除记录过的 temp name，删除前复核 regular inode identity。Phase 45 同样只能删除：

- 本次成功创建且 identity 仍匹配的 run tree component；
- 本次新发布但 rollback明确证明旧集合没有的 name；
- 本次预留的 history sequence；
- 空且由当前协议拥有的 `.work/`。

不得删除 stale unrelated `.work` entry，也不得因为名字匹配前缀就清理。

### 3.5 Equality 与 history

`verify_markdown_contract.py:98-114` 的 `file_hashes()` / `tree_snapshot()` 是测试 analog，生产实现应使用同样的“relative path + bytes”语义，但 hash 只在内存/evidence：

```python
candidate_names == current_names
and all(stream_equal(candidate/name, current/name) for name in names)
```

history scan只接受 non-symlink directory 且名称匹配 `^[0-9]{3,}$`，next=`max+1`，至少三位，不复用 gap。`history/<seq>/` 必须包含旧 Markdown、全部旧 final artifact 和旧 Markdown持续引用的 managed `assets/`；`sources/` 永不自动进入 history。

## 4. Shell-only `gongwen` 适配模式

### 4.1 保留 renderer，自 candidate 路径调用

`gongwen_lib/body.sh:330-351` 的 `render_markdown_to_typst(input, output)` 已经接受任意 output path，因此无需重写转换器。`commands.sh:33-60` 只需把 `typ/pdf` final path改为 `.work/<run-id>/candidate/<stem>.*`，并复制输入 Markdown到同一 candidate。

### 4.2 比较与验证

现有 `common.sh:50-61` `same_file_shell` 是 byte-line compare analog；生产 no-op 推荐优先 `cmp -s`，不可用时回退该函数。expected Typst也在 candidate上比较，失败前 root current不变。

Shell transaction建议：

```bash
set -euo pipefail
trap 'rollback_owned_run "$?"' EXIT INT TERM
mkdir "$work_root/lock"          # exclusive lock；失败即并发冲突
mkdir "$run_root" "$candidate" "$rollback"
# 所有 rm/mv/cp 只接受预先验证的 quoted fixed names array
```

安全限制：

- 不把 Python/Node加入 Markdown→Typst 转换依赖；
- `--typ` 决定 delivery root/stem；`--pdf` 必须同 root同 stem；
- 用 `test -L`/`lstat` 等价检查拒绝 symlink；
- 要求 `.work`、root、history同 device；
- 不用 `find -delete`、`rm "$root"/*`、glob cleanup；
- trap只回滚当前命令记录的文件，不能把 unknown当作残留物。

## 5. Node `teaching-design-package` 适配模式

### 5.1 Model 是 dynamic managed-set authority

`package-model.js:94-117` 已经提供：

- `safeCourseFilenamePrefix()` 的路径穿越/hostile character拒绝；
- `public_markdown_filename`；
- merged PDF；
- registry-derived module PDFs；
- `expected_public_filenames` 完整 explicit list。

publisher必须消费该 list，不再通过 glob或文件后缀猜测 candidate。course name变化时，current discovery可以只读识别一个结构完整的旧 `1+1+N` group；发现多个 prefix group时必须报告 ambiguous unknown，不能按mtime选“最新”。

### 5.2 保留 candidate producer 与失败注入

`teaching-design-package.sh:649-688` 已按 registry生成/验证模块 PDF status；`:690-823` 已按 registry顺序生成 merge plan，并提供 `TDPKG_FORCE_MERGE_FAILURE`；`:868-899` 还有 missing/empty module fault。这些是 Phase 45 harness 的直接 fault sources，不应删除。

当前 `.teaching-design-package/work|staging|debug` 应机械映射到：

```text
.work/<run-id>/candidate/   # 最终公开集合
.work/<run-id>/evidence/    # model/status/diagnostics/log/merge plan/module Typst
.work/<run-id>/rollback/    # 旧成功集合
```

`package-model.js:14-25` 的 `work_markdown/work_typst` 不应继续硬编码 legacy hidden root；可改为逻辑相对名，由 shell orchestration在run root下解析。

### 5.3 必须删除的危险 analog

以下不是可复用模式，而是必须替换的反例：

- `teaching-design-package.sh:204-225` `cleanup_public_root()` 用广泛 filename pattern删除；
- `:227-242` `record_failure()` 失败时再次清空 public root；
- `:843` candidate生成前清空旧成功版本；
- `:914-926` 逐文件直接 `copyFileSync` 到 root；
- `:957-959` final-ready失败再删除 public set。

Node publisher应先验证完整 candidate，再 snapshot old set；publish中断后恢复，不允许“失败即清空”。

## 6. Presentation 技能的现有模式

### 6.1 `school-pptx`：安全 I/O authority 与 best-effort边界

`pptx_render.py:342-358` 已完成正确的 candidate generation顺序：

1. stage Markdown bytes；
2. reserve PPTX descriptor；
3. `emit_deck()`；
4. frozen plan mutation check；
5. `validate_staged_package()`；
6. publish。

Phase 45 保留1-5，只替换6。`pptx_emit.py:401-470` 的 bounded ZIP/XML/relationship/reopen gate继续是 PPTX minimal validator。

当前 `pptx_render.py:359-384` 在 parser/plan/runtime errors后仍发布“异常 PPTX”并返回1。新规则要求：该 pair只存在于run evidence/candidate，不能成为root current；公开 current只在无 errors且 staged package通过时发布。真实PowerPoint/WPS UAT仍是人工边界，directory transaction不得自动签署。

### 6.2 `school-presentation`：in-memory render + caller verify workdir

`school_presentation/_engine.py:4237-4264` 已经返回 `html_doc, manifest`，因此可以在写root前完成：

- UTF-8/non-empty；
- size cap（当前`:4249-4260`应从post-write移到candidate gate）；
- offline single-file/required DOM tokens；
- required persistent asset reference；
- manifest只作为evidence。

`cmd_verify()` 从`:4267`起使用调用方 `--workdir`，这是正确 ownership。不要把 verify workdir重新定义为delivery root，也不要把 `verification-manifest.json` 纳入 current artifact。

`resolve_asset()` 当前 `:52-72` 允许 `input_dir/media` 与skill identity assets；Phase 45需要把用户持久资源语义改为`assets/`，但不能在普通render中静默移动legacy `media/`。legacy migration属于确认式cleanup流程，必须同步改Markdown引用并验证。

## 7. 验证模式映射

### 7.1 Harness结构

直接复用 `verify_markdown_contract.py` 的风格：

```python
def run(*args, expected=None):
    result = subprocess.run([PUBLIC_CLI, *args], capture_output=True, text=True)
    require("Traceback" not in result.stdout + result.stderr, ...)
    require(len((result.stdout + result.stderr).encode()) < LIMIT, ...)
    return result
```

每个测试使用 `tempfile.TemporaryDirectory`；公开CLI黑盒为主，skill-local纯helper可白盒补充。固定gate registry应至少覆盖：

1. `self_contained_installation_gate`
2. `first_publish_gate`
3. `changed_bundle_history_gate`
4. `identical_noop_gate`
5. `generation_failure_gate`
6. `validation_failure_gate`
7. `publish_rollback_gate`
8. `history_sequence_gate`
9. `unknown_and_symlink_gate`
10. `work_cleanup_and_lock_gate`
11. `assets_sources_history_reference_gate`
12. `cleanup_audit_confirmation_gate`
13. `documentation_runtime_contract_gate`
14. `existing_renderer_regression_gate`

### 7.2 必须逐技能证明的矩阵

每个技能都要运行真实public final-delivery命令，并证明：

- 首次发布：exact managed set、无history、无sidecar、`.work`收尾；
- changed：旧完整集合进入单一next history，新集合稳定文件名；
- identical：不新建history，不touch current inode/mtime（可观察时）；
- generation failure和validation failure：current/history hashes不变；
- 每个标准fault point：rollback后无mixed bundle、新history消失；
- existing `001`和`003`时next为`004`；
- unknown、legacy hidden、legacy `media`、duplicate group、symlink、traversal均在mutation前拒绝；
- `sources/` across success/no-op/failure/history始终byte-identical；
- owned empty `.work`可删，unrelated stale run不得删；
- concurrent publisher仅一个取得lock，另一项不发布、不抢history sequence。

标准fault point建议沿用 `school-pptx` hook模式（`pptx_render.py:27-31`、`:220-238`），统一名字：

```text
after_candidate_validation
after_history_reservation
after_archive_snapshot
after_publish_file_1
after_publish_middle_file
before_post_publish_verify
before_work_cleanup
```

fault hook只在环境变量/测试注入路径启用，不改变public CLI shape。`INT`/`TERM`也必须走finally/trap rollback；除非实现并测试recovery journal，不得声称SIGKILL/断电跨文件原子性。

### 7.3 Artifact minimal validators的最近实现

| Artifact | 应复用的位置 | Phase 45补强 |
|---|---|---|
| Markdown | 各skill现有parser/review marker gate；如 end-term `_engine.py:1368-1373`、tiaokedan `:420-425` | regular/non-symlink、non-empty、UTF-8、persistent `assets/` references有效 |
| Typst | gongwen/tiaokedan renderer成功结果 | regular/non-empty/UTF-8；expected compare在candidate；PDF必须从同一candidate Typst编译 |
| PDF | tiaokedan `:452-474` compile exit/non-empty；TDP module/merge status | 增加`%PDF-` header与既有 reader/merge reopen（已有时） |
| XLSX | end-term `_engine.py:1316-1354` deterministic ZIP writer与`:1392-1396` score gates | reopen ZIP、required OOXML members、四列与排序断言 |
| PPTX | `pptx_emit.py:401-470` `validate_staged_package()` | parser/plan/runtime errors为零才允许current publish |
| HTML | school-presentation `_engine.py:4237-4264` 与verify中的offline/size evidence | candidate中验证后发布；manifest不发布 |
| Teaching package | TDP `:649-688` module statuses、`:690-823` merge-order gate | exact model-derived `1+1+N` set、所有PDF readable、merged input order等于registry |

## 8. 文档契约模式

### 8.1 Canonical `SKILL.md`

保持现有 progressive-disclosure 风格：入口只保留 trigger、inputs、high-level process、public commands、outputs、verification、安全边界和 runtime adapter notes；长 filename/discovery/validator/fault说明下沉到 owning reference。

每个 covered skill入口至少出现：

- exact current Markdown/final artifact set；
- optional artifact如何改变exact set；
- `sources/`、`assets/`、`history/`、`.work/` ownership/lifecycle；
- candidate-first、identical no-op、changed whole-bundle history；
- failure rollback与unknown-file refusal；
- minimal verification与人工UAT边界；
- 六runtime的whole-folder support discovery、explicit invocation fallback、dependencies/external commands、execute/read/write、sandbox/allowlist与delivery/workdir boundary。

`skills/school-pptx/SKILL.md:84-102` 的七列runtime表是最具体的analog；其他技能可以采用同结构，尤其不能只写“支持OpenClaw/Hermes”。

### 8.2 Runtime说明

`docs/compatibility-matrix.md:90-106` 已正确采用保守措辞：

- OpenClaw：frontmatter、allowlist、skill root、sandbox、support-file discovery都installation-time verify；
- Hermes：exact local/global path、project/global behavior、support discovery、tool permissions都installation-time verify；
- 两者都保留显式脚本fallback，不假设automatic discovery。

Phase 45 应补充每技能外部依赖（Bash/Python/Node/Typst/PPTX packages/PDF merge）与可写delivery root/`.work`，不要新增runtime-specific wrapper或fork canonical workflow。

### 8.3 Cleanup契约

`docs/agent-output-cleanup-prompt.md` 已基本满足SAFE-02，正式化时保留三组输出：

1. 安全移动；
2. 需要确认的归档；
3. 需要明确批准的删除。

第一阶段必须只读，normal render/deliver不得自动触发。第二阶段执行前复核audit snapshot；只执行exact approved operations。legacy `.teaching-design-package/`、`.tiaokedan/`、`media/`和unknown user file都走该门，不能借Phase 45 silent migration。

## 9. 不应复用的反模式

| 反模式 | 位置 | 原因 | 替代 |
|---|---|---|---|
| 生成前unlink current set | end-term `_engine.py:1381-1385` | 后续失败摧毁旧成功四件套 | candidate-first + rollback publisher |
| PDF前先删stale PDF | tiaokedan renderer `:414-418` | parse/compile失败使旧bundle不完整 | candidate PDF；成功事务后replace |
| expected gate在直写后 | gongwen `commands.sh:48-53`、tiaokedan `:427-444` | mismatch已污染current | candidate compare后publish |
| HTML写后才size fail | school-presentation `_engine.py:4248-4260` | oversized HTML伪装current | candidate size gate |
| pair两次replace无rollback | school-pptx `pptx_render.py:229-243` | between hook证明mixed pair | snapshot + completed-name tracking + restore |
| non-zero best-effort仍发布 | school-pptx `:359-384` | 与SAFE-01冲突 | 仅work evidence，不成为current |
| broad `find ... rm` | TDP `teaching-design-package.sh:204-225` | 会误删unknown/user file | model-derived explicit names only |
| failure清空public root | TDP `:227-242`、`:957-959` | 不恢复上一套成功版本 | rollback verified snapshot |
| persistent hidden diagnostics | TDP `.teaching-design-package/`、tiaokedan文档`.tiaokedan/` | CLEAN-03只允许临时`.work` | run evidence，收尾删除或explicit verify root |
| 自动处理legacy `media/`/unknown | 当前无实现但易误加 | SAFE-02要求确认 | cleanup audit→confirm workflow |

## 10. 规划依赖顺序

1. **Foundation：** 先冻结`DeliverySpec`语义、fault names、cross-skill fixture/harness、cleanup audit contract和docs shared authority。
2. **Python small bundles：** end-term与tiaokedan先验证fixed/optional set publisher模式。
3. **Presentation：** school-pptx扩展held-descriptor transaction；school-presentation接candidate/manifest evidence/assets边界。
4. **Shell/Node：** gongwen shell-only adapter；TDP dynamic `1+1+N` Node transaction与legacy hidden tree迁移。
5. **Final matrix/docs：** 跑六技能矩阵与原renderer regression后，再同步README、directory spec、matrix、template和六个contract。

步骤2、3、4在foundation稳定后可由不同执行者并行，因为skill folders不重叠；shared harness registry与仓库文档只能由步骤1/5单点修改。

## 11. Planner落地检查

- [ ] 每个plan列出所拥有的shared files，避免并行冲突。
- [ ] 每个生产helper都在skill folder内自包含，无sibling/root runtime import。
- [ ] 每个public命令和既有flags保持；diagnostic/authoring命令与final publication明确区分。
- [ ] 每个plan明确candidate producer、exact managed set、current discovery、minimal validators和fault points。
- [ ] 每个mutation使用显式validated relative names，不用broad glob/delete。
- [ ] 每个rollback验证旧current与pre-existing history hashes不变。
- [ ] 每个no-op证明不创建history且不touch current。
- [ ] assets归档保持archived Markdown引用有效；sources不自动version/move。
- [ ] unknown/legacy/symlink在mutation前失败并路由确认式cleanup，而不是自动整理。
- [ ] OpenClaw/Hermes说明基于installation-time verification与显式fallback，不写推测性支持。
- [ ] 自动验证不替代school-pptx PowerPoint/WPS人工UAT，也不夸大SIGKILL/断电原子性。

本映射用于指导`PLAN.md`拆分，不构成实现承诺。最终文件名可以按executor的skill-local style微调，但上述职责、数据流、安全边界和复用位置应保持。
