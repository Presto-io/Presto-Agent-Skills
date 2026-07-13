#!/usr/bin/env python3
"""Repeatable standard-library contract gate for school-pptx Markdown."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PUBLIC_CLI = SCRIPT_DIR / "school-pptx.sh"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(*args: str, expected: int | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([str(PUBLIC_CLI), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if expected is not None:
        require(result.returncode == expected, f"{' '.join(args)}: expected {expected}, got {result.returncode}\n{result.stdout}\n{result.stderr}")
    require("Traceback" not in result.stdout + result.stderr, f"stack trace leaked for {' '.join(args)}")
    return result


def validate(path: Path, out: Path | None = None) -> tuple[subprocess.CompletedProcess[str], dict]:
    args = ["validate", "--input", str(path)]
    if out:
        args += ["--out-json", str(out)]
    result = run(*args)
    model = json.loads(out.read_text(encoding="utf-8")) if out and out.is_file() else {}
    return result, model


def codes(model: dict) -> set[str]:
    return {item["code"] for item in model.get("errors", [])}


def assert_diagnostics(model: dict) -> None:
    errors = model["errors"]
    require(errors, "expected populated errors")
    order = [(item["line"], item["column"], item["code"]) for item in errors if item["code"] != "RESOURCE_DIAGNOSTIC_LIMIT"]
    require(order == sorted(order), "diagnostics are not deterministic/source ordered")
    for item in errors:
        require(item["path"] and item["line"] >= 1 and item["column"] >= 1, "diagnostic location invalid")
        require(all(key in item for key in ("code", "slide", "layout", "fix")), "diagnostic shape incomplete")


def write_case(directory: Path, name: str, text: str) -> Path:
    path = directory / name
    path.write_text(text, encoding="utf-8")
    return path


def positive_gate(work: Path) -> None:
    relative = work / "relative.png"
    absolute = work / "absolute.png"
    relative.write_bytes(b"relative-media")
    absolute.write_bytes(b"absolute-media")
    source = write_case(work, "positive.md", f'''---
subtitle: "可选副标题"
theme: standard-school
---
# 文档回退标题

::: slide {{layout="cover"}}
:::

::: slide {{layout="contents"}}
:::

::: slide {{layout="title-content"}}
## 第一章

### 目标

一段含 **bold** 和 ==highlight== 的正文。

![相对图片](relative.png)

::: notes
独立演讲者备注。
:::
:::

::: slide {{layout="section"}}
## 第二章
:::

::: slide {{layout="two-column"}}
## 双栏比较

左栏内容。

右栏内容。
:::

::: slide {{layout="image-text"}}
## 图文说明

稳定正文。

![相对图片](relative.png)
![绝对图片]({absolute})
:::

::: slide {{layout="table"}}
## 数据表

### 指标表

| 指标 | 数值 |
|---|---|
| 完成率 | 100% |
:::

::: slide {{layout="timeline"}}
## 建设进度

| 时间 | 标题 | 说明 |
|---|---|---|
| 7月 | 启动 | 完成契约 |
:::

::: slide {{layout="gallery"}}
## 成果图集

![相对图片](relative.png)
![绝对图片]({absolute})
:::

::: slide {{layout="code"}}
## 示例代码

```html
<div style="color:red">fenced code</div>
```
:::
''')
    output = work / "positive.json"
    result, model = validate(source, output)
    require(result.returncode == 0 and "校验通过" in result.stdout, "positive source did not pass")
    require(model["errors"] == [], "positive JSON contains errors")
    require(model["document_title"] == "文档回退标题", "title fallback failed")
    require(model["contents_entries"] == ["第一章", "第二章", "双栏比较", "图文说明", "数据表", "建设进度", "成果图集", "示例代码"],
            "contents order failed")
    require(len(model["implicit_slides"]) == 1 and model["implicit_slides"][0]["layout"] == "closing", "implicit closing failed")
    require(set(model["coverage"]["explicit_layouts"]) == {"cover", "contents", "section", "title-content", "two-column",
                                                               "image-text", "table", "timeline", "gallery", "code"},
            "ten explicit layouts not covered")
    require(model["coverage"]["summary"] == "10 个显式布局 + 1 个隐式 closing", "coverage summary failed")
    first = model["logical_slides"][2]
    require(first["notes"]["markdown"] == "独立演讲者备注。", "notes missing")
    require(all(block["kind"] != "notes" for block in first["blocks"]), "notes leaked into visible blocks")
    media = [block for slide in model["logical_slides"] for block in slide["blocks"] if block["kind"] == "image"]
    require(any(not item["absolute_authored"] and item["resolved_path"] == str(relative.resolve()) for item in media), "relative media resolution failed")
    require(any(item["absolute_authored"] and item["resolved_path"] == str(absolute.resolve()) for item in media), "absolute media resolution failed")
    first_bytes = output.read_bytes()
    second_output = work / "positive-second.json"
    second_result, second_model = validate(source, second_output)
    require(second_result.returncode == 0 and second_model == model and second_output.read_bytes() == first_bytes,
            "logical JSON is not deterministic")


def aggregate_negative_gate(work: Path) -> None:
    source = write_case(work, "aggregate-invalid.md", '''---
title: "坏输入"
unknown: value
theme: unknown-theme
---
::: slide {id="public-id"}
## 缺少布局
<div style="color:red" x="1">非法 HTML</div>
### 悬空标题
::: notes
备注
:::
备注之后仍有正文
:::
::: slide {layout="unknown-layout"}
## 未知布局
![缺失图片](missing.png)
:::
::: slide {layout="closing"}
:::
::: slide {layout="timeline"}
## 非法时间线
| 时段 | 标题 | 说明 |
|---|---|---|
| 1 | A | B |
:::
## slide 外标题
''')
    output = work / "aggregate-invalid.json"
    result, model = validate(source, output)
    require(result.returncode != 0 and "校验失败" in result.stdout, "aggregate invalid source passed")
    required = {"YAML_UNKNOWN_KEY", "THEME_UNKNOWN", "SLIDE_LAYOUT_REQUIRED", "SLIDE_ATTRIBUTE_UNKNOWN", "RAW_HTML",
                "UNSUPPORTED_STYLE", "HEADING_DANGLING", "NOTES_POSITION", "LAYOUT_UNKNOWN", "MEDIA_MISSING",
                "LAYOUT_CLOSING_EXPLICIT", "TIMELINE_INVALID", "HEADING_OUTSIDE_SLIDE"}
    require(required <= codes(model), f"missing aggregate codes: {required - codes(model)}")
    closing = next(item for item in model["errors"] if item["code"] == "LAYOUT_CLOSING_EXPLICIT")
    require(closing["message"] == "closing 由模板在文稿末尾自动追加，不能在 Markdown 中显式创建或修改。", "closing message changed")
    missing = next(block for slide in model["logical_slides"] for block in slide["blocks"] if block.get("placeholder"))
    require(not missing["exists"] and missing["placeholder"]["safe"], "missing media fallback metadata absent")
    assert_diagnostics(model)


def fence_gate(work: Path) -> None:
    inside = write_case(work, "inside-fence.md", '''---
title: fence
theme: standard-school
---
::: slide {layout="code"}
## Code
```html
<div style="color:red" x="10">code</div>
```
:::
''')
    result, model = validate(inside, work / "inside.json")
    require(result.returncode == 0 and not ({"RAW_HTML", "UNSUPPORTED_STYLE"} & codes(model)), "fenced code false positive")
    outside = write_case(work, "outside-fence.md", '''---
title: outside
theme: standard-school
---
::: slide {layout="title-content"}
## Outside
<div style="color:red">text</div>
:::
''')
    result, model = validate(outside, work / "outside.json")
    require(result.returncode != 0 and {"RAW_HTML", "UNSUPPORTED_STYLE"} <= codes(model), "outside fence syntax accepted")


def collision_gate(work: Path) -> None:
    source = write_case(work, "collision.md", '''---
title: collision
theme: standard-school
---
::: slide {layout="cover"}
:::
''')
    original = source.read_bytes()
    result = run("validate", "--input", str(source), "--out-json", str(source))
    require(result.returncode != 0 and "OUTPUT_COLLISION" in result.stdout and source.read_bytes() == original, "input/output identity unsafe")
    target = work / "json-directory"
    target.mkdir()
    sentinel = target / "sentinel"
    sentinel.write_text("keep", encoding="utf-8")
    result = run("validate", "--input", str(source), "--out-json", str(target))
    require(result.returncode != 0 and "OUTPUT_COLLISION" in result.stdout, "directory collision accepted")
    require(sentinel.read_text(encoding="utf-8") == "keep", "directory collision modified sentinel")


def resource_case(work: Path, name: str, payload: bytes | str, expected_code: str) -> None:
    path = work / name
    if isinstance(payload, bytes):
        path.write_bytes(payload)
    else:
        path.write_text(payload, encoding="utf-8")
    output = work / f"{name}.json"
    result, model = validate(path, output)
    require(result.returncode != 0, f"resource case {expected_code} passed")
    require(expected_code in codes(model), f"resource case missing {expected_code}: {codes(model)}")
    require(len(result.stdout + result.stderr) < 200_000, f"resource diagnostic unbounded: {expected_code}")


def resource_gate(work: Path) -> None:
    resource_case(work, "input-bytes.md", b"x" * (2 * 1024 * 1024 + 1), "RESOURCE_INPUT_BYTES")
    resource_case(work, "frontmatter-bytes.md", "---\ntitle: |\n" + "  x\n" * 22000 + "theme: standard-school\n---\n", "RESOURCE_FRONTMATTER_BYTES")
    resource_case(work, "line-length.md", "---\ntitle: x\ntheme: standard-school\n---\n" + "x" * (32 * 1024 + 1), "RESOURCE_LINE_LENGTH")
    blocks = "\n\n".join(f"paragraph {index}" for index in range(2049))
    resource_case(work, "block-count.md", f'''---
title: blocks
theme: standard-school
---
::: slide {{layout="title-content"}}
## Blocks
{blocks}
:::
''', "RESOURCE_BLOCK_COUNT")
    opens = "\n".join("::: unknown" for _ in range(9))
    closes = "\n".join(":::" for _ in range(9))
    resource_case(work, "nesting-depth.md", f'''---
title: nesting
theme: standard-school
---
::: slide {{layout="title-content"}}
## Nested
{opens}
body
{closes}
:::
''', "RESOURCE_NESTING_DEPTH")
    nodes = "\n".join(f"  - item-{index}" for index in range(260))
    resource_case(work, "yaml-nodes.md", f"---\ntitle:\n{nodes}\ntheme: standard-school\n---\n", "YAML_NODE_LIMIT")
    resource_case(work, "yaml-alias.md", '''---
title: &title Alias
subtitle: *title
theme: standard-school
---
::: slide {layout="cover"}
:::
''', "YAML_ALIAS_FORBIDDEN")
    diagnostics = "\n".join(f"<b>bad-{index}</b>" for index in range(205))
    resource_case(work, "diagnostic-limit.md", f'''---
title: diagnostics
theme: standard-school
---
::: slide {{layout="title-content"}}
## Diagnostics
{diagnostics}
:::
''', "RESOURCE_DIAGNOSTIC_LIMIT")


def regression_gate(work: Path) -> None:
    report_md = work / "template-report.md"
    report_json = work / "template-report.json"
    run("template-report", "--theme", "standard-school", "--out-md", str(report_md), "--out-json", str(report_json), expected=0)
    require(report_md.is_file() and report_json.is_file(), "template-report evidence missing")
    info = run("info", expected=0)
    require("templates/standard-school.pptx" in info.stdout and "templates/standard-school.manifest.yaml" in info.stdout, "info regression")
    help_result = run("--help", expected=0)
    require("school-pptx.sh validate --input <deck.md> [--out-json <logical-document.json>]" in help_result.stdout, "literal validate usage missing")


def contract_command() -> int:
    with tempfile.TemporaryDirectory(prefix="school-pptx-contract-") as temporary:
        work = Path(temporary)
        positive_gate(work)
        aggregate_negative_gate(work)
        fence_gate(work)
        collision_gate(work)
        resource_gate(work)
        regression_gate(work)
    print("PASS school-pptx Markdown contract: positive, aggregate-negative, fence, collision, resources, Phase 41 regression")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="verify_markdown_contract.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    contract = subparsers.add_parser("contract")
    contract.set_defaults(func=contract_command)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func()


if __name__ == "__main__":
    raise SystemExit(main())
