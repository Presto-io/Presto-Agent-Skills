# Phase 21 Verification: Jiaoan Jihua 1:1 Typst Conversion

**Verified:** 2026-06-13T17:17:08Z
**Scope:** `skills/jiaoan-jihua/` only

## Commands

```bash
tmpdir="$(mktemp -d)"
generated="$tmpdir/jiaoan-jihua-generated.typ"
target="test/1.10/电气设备控制线路安装与调试授课计划.typ"
source="test/1.10/电气设备控制线路安装与调试授课计划.md"

skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input "$source" \
  --typ "$generated"

diff -u "$target" "$generated"
shasum -a 256 "$target" "$generated"

skills/jiaoan-jihua/scripts/jiaoan-jihua.sh render \
  --input "$source" \
  --typ "$tmpdir/jiaoan-jihua-generated-expected.typ" \
  --expected-typ "$target"

! rg -n '电气设备控制线路安装与调试授课计划\.typ|test/1\.10|copy_file_shell "\$expected_typ"|cp .*expected_typ|cat .*expected_typ' \
  skills/jiaoan-jihua/scripts/jiaoan-jihua.sh
```

## Evidence

```text
tmpdir=/var/folders/kh/3z1m41y56mgd98lxmb9zjjsw0000gn/T/tmp.RC7OKtoysz
wrote /var/folders/kh/3z1m41y56mgd98lxmb9zjjsw0000gn/T/tmp.RC7OKtoysz/jiaoan-jihua-generated.typ
render_without_expected_status=0
diff_status=0
0d681cca76cb7d6edaf7b0c76874f3f8a5b3f49ab5e00904caf9a106690e138b  test/1.10/电气设备控制线路安装与调试授课计划.typ
0d681cca76cb7d6edaf7b0c76874f3f49ab5e00904caf9a106690e138b  /var/folders/kh/3z1m41y56mgd98lxmb9zjjsw0000gn/T/tmp.RC7OKtoysz/jiaoan-jihua-generated.typ
wrote /var/folders/kh/3z1m41y56mgd98lxmb9zjjsw0000gn/T/tmp.RC7OKtoysz/jiaoan-jihua-generated-expected.typ
verified Typst matches test/1.10/电气设备控制线路安装与调试授课计划.typ
render_with_expected_status=0
anti_copy_status=passed_no_forbidden_patterns
```

## Structural Assertions

```text
load_calendar_dates: present
parse_official_jihua_body: present
assign_schedule_cells: present
term_week_for_date: present
weekday_for_date: present
emit_official_jihua_head: present
emit_official_jihua_table: present
emit_official_jihua_typst: present
```

## Scope Note

`git diff --name-only` after Phase 21 verification listed:

```text
skills/jiaoan-shicao/scripts/jiaoan-shicao.sh
```

That file is outside Phase 21 and was already present as a parallel Phase 20 worktree/main-workspace change. Phase 21 did not stage or modify `skills/jiaoan-shicao/`.

## Result

VERIFICATION PASSED
