#!/usr/bin/env python3
"""Repeatable standard-library contract gate for school-pptx Markdown."""

from __future__ import annotations

import argparse
import contextlib
import hashlib
import importlib.util
import inspect
import io
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
PUBLIC_CLI = SCRIPT_DIR / "school-pptx.sh"
FIXTURE = SKILL_DIR / "fixtures" / "school-pptx-full.md"
OWNED_PATHS = {
    "school-pptx-full.md",
    "media/equipment-cell.png",
    "media/plc-line.png",
    "media/robot-arm.png",
    "media/curriculum-map.png",
}
CORE_PATH = SCRIPT_DIR / "markdown_contract.py"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def run(*args: str, expected: int | None = None) -> subprocess.CompletedProcess[str]:
    result = subprocess.run([str(PUBLIC_CLI), *args], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if expected is not None:
        require(result.returncode == expected, f"{' '.join(args)}: expected {expected}, got {result.returncode}\n{result.stdout}\n{result.stderr}")
    require("Traceback" not in result.stdout + result.stderr, f"stack trace leaked for {' '.join(args)}")
    return result


def run_core(skill_dir: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(CORE_PATH), str(skill_dir), *args], text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)


def load_core():
    spec = importlib.util.spec_from_file_location("school_pptx_markdown_contract_gate", CORE_PATH)
    require(spec is not None and spec.loader is not None, "cannot load markdown contract core")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def invoke_example(core, output: Path) -> tuple[int, str, str]:
    stdout, stderr = io.StringIO(), io.StringIO()
    args = argparse.Namespace(out_dir=str(output), skill_dir=str(SKILL_DIR))
    with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
        result = core.example_command(args)
    return result, stdout.getvalue(), stderr.getvalue()


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


def file_hashes(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file() and not path.is_symlink()
    }


def tree_snapshot(root: Path) -> dict[str, tuple[str, str]]:
    snapshot: dict[str, tuple[str, str]] = {}
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            snapshot[relative] = ("symlink", os.readlink(path))
        elif path.is_dir():
            snapshot[relative] = ("directory", "")
        elif path.is_file():
            snapshot[relative] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
    return snapshot


def overflow_item(slide: dict, kind: str) -> dict:
    return next(item for item in slide.get("overflow_evidence", []) if item.get("kind") == kind)


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
    require(model["contents_entries"] == ["第二章"],
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


def yaml_value_gate(work: Path) -> None:
    cases = {
        "date": "date: 2026-07-13",
        "bool": "subtitle: true",
        "number": "course: 42",
        "list": "author: [A, B]",
        "mapping": "presenter: {name: A}",
    }
    quoted = write_case(work, "yaml-quoted.md", '''---
title: "YAML 字符串"
date: "2026-07-13"
theme: "standard-school"
---
::: slide {layout="cover"}
:::
''')
    result, model = validate(quoted, work / "yaml-quoted.json")
    require(result.returncode == 0 and model["metadata"]["date"] == "2026-07-13", "quoted date string rejected")

    for name, field in cases.items():
        source = write_case(work, f"yaml-{name}.md", f'''---
title: "YAML 类型"
{field}
theme: "standard-school"
---
::: slide {{layout="cover"}}
:::
''')
        plain = run("validate", "--input", str(source))
        result, model = validate(source, work / f"yaml-{name}.json")
        require(plain.returncode != 0 and result.returncode != 0, f"implicit YAML {name} passed")
        require("YAML_VALUE_TYPE" in plain.stdout and "YAML_VALUE_TYPE" in codes(model), f"implicit YAML {name} missing diagnostic")
        require("Traceback" not in plain.stdout + plain.stderr + result.stdout + result.stderr, f"implicit YAML {name} leaked traceback")
        item = next(item for item in model["errors"] if item["code"] == "YAML_VALUE_TYPE")
        require(item["line"] >= 1 and item["column"] >= 1, f"implicit YAML {name} location invalid")


def fence_opacity_gate(work: Path) -> None:
    payloads = (
        ("backtick", "```", ":::\n::: notes\ninside notes text\n:::\n::: slide {layout=\"table\"}"),
        ("tilde", "~~~~", "::: slide {layout=\"table\"}\n::: notes\n:::\n:::")
    )
    for name, marker, payload in payloads:
        source = write_case(work, f"fence-opacity-{name}.md", f'''---
title: "Fence opacity"
theme: "standard-school"
---
::: slide {{layout="code"}}
## Code
{marker}text
{payload}
{marker}
:::
''')
        result, model = validate(source, work / f"fence-opacity-{name}.json")
        require(result.returncode == 0, f"{name} directive-like code payload rejected: {codes(model)}")
        code = model["logical_slides"][0]["blocks"][0]
        require(code["kind"] == "code" and code["text"] == payload, f"{name} code payload changed")


def table_structure_gate(work: Path) -> None:
    valid_cases = {
        "table": ("table", "| A | B |\n|---|:---:|\n| 1 | 2 |"),
        "timeline": ("timeline", "| 时间 | 标题 | 说明 |\n|---|---|---|\n| 7月 | 启动 | 完成契约 |"),
    }
    for name, (layout, table) in valid_cases.items():
        source = write_case(work, f"table-valid-{name}.md", f'''---
title: "Valid table"
theme: "standard-school"
---
::: slide {{layout="{layout}"}}
## Valid
{table}
:::
''')
        result, model = validate(source, work / f"table-valid-{name}.json")
        require(result.returncode == 0 and not codes(model), f"valid {name} rejected")

    invalid_cases = {
        "missing-separator": ("| A | B |\n| 1 | 2 |", "TABLE_SEPARATOR_INVALID"),
        "malformed-separator": ("| A | B |\n|---|oops|\n| 1 | 2 |", "TABLE_SEPARATOR_INVALID"),
        "short-row": ("| A | B |\n|---|---|\n| 1 |", "TABLE_COLUMN_MISMATCH"),
        "wide-row": ("| A | B |\n|---|---|\n| 1 | 2 | 3 |", "TABLE_COLUMN_MISMATCH"),
    }
    for name, (table, expected_code) in invalid_cases.items():
        source = write_case(work, f"table-invalid-{name}.md", f'''---
title: "Invalid table"
theme: "standard-school"
---
::: slide {{layout="table"}}
## Invalid
{table}
:::
''')
        result, model = validate(source, work / f"table-invalid-{name}.json")
        require(result.returncode != 0 and expected_code in codes(model), f"{name} missing {expected_code}")


def gap_parser_command() -> int:
    with tempfile.TemporaryDirectory(prefix="school-pptx-gap-parser-") as temporary:
        work = Path(temporary)
        yaml_value_gate(work)
        fence_opacity_gate(work)
        table_structure_gate(work)
    print("PASS school-pptx gap-parser: YAML string types, fence opacity, table structure")
    return 0


def manifest_failure_gate(work: Path) -> None:
    source = write_case(work, "manifest-input.md", '''---
title: "Manifest failure"
theme: "standard-school"
---
::: slide {layout="cover"}
:::
''')
    cases = {
        "missing": (None, "MANIFEST_UNREADABLE"),
        "malformed": ("layouts: [", "MANIFEST_MALFORMED"),
        "root-invalid": ("- not\n- a\n- mapping\n", "MANIFEST_ROOT_INVALID"),
        "layouts-invalid": ("theme_id: standard-school\nlayouts: []\n", "MANIFEST_ROOT_INVALID"),
    }
    for name, (manifest_text, expected_code) in cases.items():
        skill_dir = work / f"manifest-{name}"
        templates = skill_dir / "templates"
        templates.mkdir(parents=True)
        if manifest_text is not None:
            (templates / "standard-school.manifest.yaml").write_text(manifest_text, encoding="utf-8")
        output = work / f"manifest-{name}.json"
        result = run_core(skill_dir, "validate", "--input", str(source), "--out-json", str(output))
        combined = result.stdout + result.stderr
        require(result.returncode != 0 and expected_code in combined, f"manifest {name} missing {expected_code}")
        require(len(combined) < 4000 and "Traceback" not in combined and "Error:" not in combined,
                f"manifest {name} failure is unbounded")
        require("主题：-" in result.stdout and "校验通过" not in result.stdout and "Phase 43" not in result.stdout,
                f"manifest {name} printed false state")
        model = json.loads(output.read_text(encoding="utf-8"))
        require(expected_code in codes(model), f"manifest {name} JSON missing diagnostic")


def secure_io_capability_gate(work: Path) -> None:
    core = load_core()
    output = work / "capability-output"
    core.secure_io_capabilities = lambda: ("os.O_NOFOLLOW",)
    result, stdout, stderr = invoke_example(core, output)
    require(result != 0 and "EXAMPLE_SECURE_IO_UNAVAILABLE" in stderr, "missing secure-I/O capability did not fail closed")
    require(not output.exists() and "校验结果：PASS" not in stdout and len(stdout + stderr) < 4000,
            "capability failure mutated output or was unbounded")


def symlink_exchange_gate(work: Path) -> None:
    for exchange in ("root", "media"):
        core = load_core()
        output = work / f"exchange-{exchange}"
        outside = work / f"outside-{exchange}"
        outside.mkdir()
        (outside / "sentinel.txt").write_bytes(f"outside-{exchange}".encode())
        before = tree_snapshot(outside)
        held = work / f"held-{exchange}"

        def hook(root: Path, *, exchange: str = exchange) -> None:
            if exchange == "root":
                root.rename(held)
                root.symlink_to(outside, target_is_directory=True)
            else:
                media = root / "media"
                media.rename(held)
                media.symlink_to(outside, target_is_directory=True)

        core.EXAMPLE_PRE_PUBLISH_HOOK = hook
        result, stdout, stderr = invoke_example(core, output)
        require(result != 0 and "EXAMPLE_DESTINATION_CHANGED" in stderr, f"{exchange} exchange was not detected")
        require("校验结果：PASS" not in stdout and len(stdout + stderr) < 4000, f"{exchange} exchange failure was unbounded")
        require(tree_snapshot(outside) == before, f"{exchange} exchange modified outside target")
        if exchange == "root":
            output.unlink()
            held.rename(output)
            held_parent = output
        else:
            (output / "media").unlink()
            held.rename(output / "media")
            held_parent = output
        require(not any(path.name.startswith(".") and ".tmp-" in path.name for path in held_parent.rglob("*")),
                f"{exchange} exchange left temporary files")


REQUIRED_GAP_GATE_NAMES = (
    "yaml_value_gate",
    "fence_opacity_gate",
    "table_structure_gate",
    "manifest_failure_gate",
    "symlink_exchange_gate",
)
GAP_GATE_REGISTRY = (
    ("yaml_value_gate", yaml_value_gate),
    ("fence_opacity_gate", fence_opacity_gate),
    ("table_structure_gate", table_structure_gate),
    ("manifest_failure_gate", manifest_failure_gate),
    ("symlink_exchange_gate", symlink_exchange_gate),
)


def assert_gap_gate_completeness() -> None:
    names = tuple(name for name, _ in GAP_GATE_REGISTRY)
    require(names == REQUIRED_GAP_GATE_NAMES, f"gap gate registry mismatch: {names}")
    require(len(names) == len(set(names)), "gap gate registry contains duplicate names")
    source = Path(__file__).read_text(encoding="utf-8")
    for name, gate in GAP_GATE_REGISTRY:
        require(callable(gate) and gate.__name__ == name, f"gap gate is not callable: {name}")
        require(f"def {name}(" in source, f"gap gate source definition missing: {name}")
    fixture_source = inspect.getsource(fixture_example_command)
    require("run_gap_gates(gap_work)" in fixture_source, "fixture-example no longer invokes the gap registry")
    require("secure_io_capability_gate(gap_work)" in fixture_source,
            "fixture-example no longer invokes the secure-I/O capability companion")


def run_gap_gates(work: Path) -> None:
    for _, gate in GAP_GATE_REGISTRY:
        gate(work)


def gap_safety_command() -> int:
    with tempfile.TemporaryDirectory(prefix="school-pptx-gap-safety-") as temporary:
        work = Path(temporary)
        manifest_failure_gate(work)
        secure_io_capability_gate(work)
        symlink_exchange_gate(work)
    print("PASS school-pptx gap-safety: manifest failures, descriptor capabilities, root/media exchange")
    return 0


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


def full_fixture_gate(work: Path) -> None:
    output = work / "example"
    output.mkdir()
    sentinel = output / "caller-owned.txt"
    sentinel.write_text("caller-owned\n", encoding="utf-8")
    sentinel_directory = output / "caller-owned-directory"
    sentinel_directory.mkdir()
    (sentinel_directory / "nested.txt").write_text("nested-caller-owned\n", encoding="utf-8")
    initial_sentinels = tree_snapshot(output)

    first = run("example", "--out-dir", str(output), expected=0)
    require("11/11 controlled layout semantics（10 explicit + 1 implicit）" in first.stdout, "example coverage copy missing")
    require("校验结果：PASS" in first.stdout and "已保留输出目录中的其他文件。" in first.stdout, "example success copy incomplete")
    first_hashes = file_hashes(output)
    second = run("example", "--out-dir", str(output), expected=0)
    require(file_hashes(output) == first_hashes, "example output is not byte deterministic")
    require(second.stdout == first.stdout, "example terminal summary is not deterministic")
    require(set(first_hashes) == OWNED_PATHS | {"caller-owned.txt", "caller-owned-directory/nested.txt"}, "example output ownership changed")
    after_sentinels = tree_snapshot(output)
    for path, value in initial_sentinels.items():
        require(after_sentinels.get(path) == value, f"caller-owned path changed: {path}")

    logical_json = work / "full-logical-document.json"
    result, model = validate(output / "school-pptx-full.md", logical_json)
    require(result.returncode == 0 and model.get("errors") == [], "copied full fixture did not validate")
    require(model.get("metadata", {}).get("theme") == "standard-school", "fixture theme changed")
    require(set(model["coverage"]["explicit_layouts"]) == {"cover", "contents", "section", "title-content", "two-column", "image-text", "table", "timeline", "gallery", "code"}, "full fixture explicit coverage incomplete")
    require(model["coverage"]["implicit_layouts"] == ["closing"], "full fixture implicit closing changed")
    slides = model["logical_slides"]
    require(model["contents_entries"] == [
        slide["title"] for slide in slides if slide["layout"] == "section"
    ], "full fixture section-only contents order changed")
    require(any(slide.get("notes") for slide in slides), "full fixture notes missing")
    require(all(all(block.get("kind") != "notes" for block in slide["blocks"]) for slide in slides), "notes leaked into visible blocks")
    media = [block for slide in slides for block in slide["blocks"] if block.get("kind") == "image"]
    require(all(block["exists"] for block in media), "full fixture has missing media")
    require({Path(block["authored_path"]).name for block in media} == {Path(path).name for path in OWNED_PATHS if path.startswith("media/")}, "full fixture media set changed")
    require(any(block["caption"] for block in media) and any(block["caption"] == "" for block in media), "caption or empty-caption evidence missing")
    require(any(overflow_item(slide, "long_text")["exceeds_budget"] for slide in slides if slide["layout"] == "title-content"), "long text evidence missing")
    require(any(overflow_item(slide, "column_pairs")["pairs"][-1][1] is None for slide in slides if slide["layout"] == "two-column"), "odd two-column evidence missing")
    require(any(len(overflow_item(slide, "stable_body_images")["image_indexes"]) > 1 for slide in slides if slide["layout"] == "image-text"), "multi-image evidence missing")
    require(any(overflow_item(slide, "long_table")["exceeds_budget"] for slide in slides if slide["layout"] == "table"), "long table evidence missing")
    require(any(overflow_item(slide, "long_timeline")["exceeds_budget"] for slide in slides if slide["layout"] == "timeline"), "long timeline evidence missing")
    require(any(overflow_item(slide, "gallery_capacity")["exceeds_budget"] for slide in slides if slide["layout"] == "gallery"), "gallery overflow evidence missing")
    require(any(overflow_item(slide, "long_code")["exceeds_budget"] for slide in slides if slide["layout"] == "code"), "long code evidence missing")
    require(not any(path.name.endswith((".json", ".log")) or "manifest" in path.name or "debug" in path.name for path in output.rglob("*") if path.is_file()), "public example contains evidence artifact")


def metadata_and_media_variants_gate(work: Path) -> None:
    relative = work / "variant-relative.png"
    absolute = work / "variant-absolute.png"
    relative.write_bytes(b"relative")
    absolute.write_bytes(b"absolute")
    fallback = write_case(work, "fallback.md", f'''---
theme: standard-school
---
# 回退标题
::: slide {{layout="cover"}}
:::
::: slide {{layout="contents"}}
:::
::: slide {{layout="image-text"}}
## 图文条目
稳定正文。
![相对]({relative.name})
![绝对]({absolute})
:::
''')
    result, model = validate(fallback, work / "fallback.json")
    require(result.returncode == 0, "optional metadata/title fallback variant failed")
    require(model["metadata"] == {"theme": "standard-school"}, "optional metadata placeholders invented")
    require(model["document_title"] == "回退标题" and model["contents_entries"] == [], "# fallback or contents isolation failed")
    media = [block for slide in model["logical_slides"] for block in slide["blocks"] if block["kind"] == "image"]
    require(any(not block["absolute_authored"] and block["resolved_path"] == str(relative.resolve()) for block in media), "relative media variant failed")
    require(any(block["absolute_authored"] and block["resolved_path"] == str(absolute.resolve()) for block in media), "absolute media variant failed")

    yaml_title = write_case(work, "yaml-title.md", '''---
title: YAML 标题
theme: standard-school
---
# 不应覆盖 YAML
::: slide {layout="cover"}
:::
''')
    result, model = validate(yaml_title, work / "yaml-title.json")
    require(result.returncode == 0 and model["document_title"] == "YAML 标题" and model["contents_entries"] == [], "YAML title precedence failed")


def assert_example_failure(output: Path, *protected_roots: Path) -> None:
    before = [tree_snapshot(root) for root in protected_roots]
    result = run("example", "--out-dir", str(output))
    require(result.returncode != 0, f"unsafe example output passed: {output}")
    require("未删除输出目录中的任何无关文件。" in result.stderr, "bounded preservation failure copy missing")
    require(len(result.stdout + result.stderr) < 4000, "example failure diagnostic is unbounded")
    for root, snapshot in zip(protected_roots, before):
        require(tree_snapshot(root) == snapshot, f"example failure changed protected tree: {root}")


def example_safety_gate(work: Path) -> None:
    for relative in sorted(OWNED_PATHS):
        output = work / ("collision-" + relative.replace("/", "-"))
        target = output / relative
        target.mkdir(parents=True)
        (target / "collision-sentinel.txt").write_text("keep\n", encoding="utf-8")
        caller = output / "caller.txt"
        caller.write_text("keep\n", encoding="utf-8")
        assert_example_failure(output, output)

    non_directory_parent = work / "non-directory-parent"
    non_directory_parent.mkdir()
    (non_directory_parent / "media").write_text("not-a-directory\n", encoding="utf-8")
    (non_directory_parent / "caller.txt").write_text("keep\n", encoding="utf-8")
    assert_example_failure(non_directory_parent, non_directory_parent)

    outside_root = work / "outside-root"
    outside_root.mkdir()
    (outside_root / "outside.txt").write_text("outside\n", encoding="utf-8")
    output_link = work / "output-link"
    output_link.symlink_to(outside_root, target_is_directory=True)
    assert_example_failure(output_link, outside_root)

    destination_output = work / "destination-link"
    (destination_output / "media").mkdir(parents=True)
    outside_file = work / "outside-file.png"
    outside_file.write_bytes(b"outside-target")
    (destination_output / "media" / "equipment-cell.png").symlink_to(outside_file)
    (destination_output / "caller.txt").write_text("keep\n", encoding="utf-8")
    assert_example_failure(destination_output, destination_output, work)

    parent_output = work / "parent-link"
    parent_output.mkdir()
    outside_media = work / "outside-media"
    outside_media.mkdir()
    (outside_media / "outside.txt").write_text("outside\n", encoding="utf-8")
    (parent_output / "media").symlink_to(outside_media, target_is_directory=True)
    (parent_output / "caller.txt").write_text("keep\n", encoding="utf-8")
    assert_example_failure(parent_output, parent_output, outside_media)


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


def fixture_example_command() -> int:
    contract_command()
    with tempfile.TemporaryDirectory(prefix="school-pptx-fixture-example-") as temporary:
        work = Path(temporary)
        gap_work = work / "gap-gates"
        gap_work.mkdir()
        assert_gap_gate_completeness()
        run_gap_gates(gap_work)
        secure_io_capability_gate(gap_work)
        full_fixture_gate(work)
        metadata_and_media_variants_gate(work)
        example_safety_gate(work)
        regression_gate(work)
    require(FIXTURE.is_file(), "canonical fixture missing")
    print("PASS school-pptx fixture-example: YAML types, fence opacity, table structure, manifest failures, "
          "descriptor capability fail-closed, output-root exchange, media-parent exchange, full coverage, "
          "determinism, ownership, variants, collisions, Phase 41 regression")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="verify_markdown_contract.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    contract = subparsers.add_parser("contract")
    contract.set_defaults(func=contract_command)
    gap_parser = subparsers.add_parser("gap-parser")
    gap_parser.set_defaults(func=gap_parser_command)
    gap_safety = subparsers.add_parser("gap-safety")
    gap_safety.set_defaults(func=gap_safety_command)
    fixture_example = subparsers.add_parser("fixture-example")
    fixture_example.set_defaults(func=fixture_example_command)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return args.func()


if __name__ == "__main__":
    raise SystemExit(main())
