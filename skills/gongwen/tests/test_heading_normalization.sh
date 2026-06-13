#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$TEST_DIR/.." && pwd)"
FIXTURE_DIR="$SKILL_DIR/references/fixtures"
RENDERER="$SKILL_DIR/scripts/gongwen.sh"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/gongwen-heading-test.XXXXXX")"
trap 'rm -rf "$TMP_DIR"' EXIT

"$RENDERER" render \
  --input "$FIXTURE_DIR/heading-normalization-clean.md" \
  --typ "$TMP_DIR/clean.typ" >/dev/null
"$RENDERER" render \
  --input "$FIXTURE_DIR/heading-normalization-numbered.md" \
  --typ "$TMP_DIR/numbered.typ" >/dev/null

cmp -s "$TMP_DIR/clean.typ" "$TMP_DIR/numbered.typ" || {
  printf '带手写序号和不带序号的标题渲染结果不一致。\n' >&2
  diff -u "$TMP_DIR/clean.typ" "$TMP_DIR/numbered.typ" >&2 || true
  exit 1
}

grep -Fq '#let FONT_HEI = ("SimHei", "STHeiti", "Heiti SC", "Noto Sans CJK SC", "Source Han Sans SC", "思源黑体", "Microsoft YaHei")' "$TMP_DIR/clean.typ"
grep -Fq '#let FONT_SONG = ("SimSun", "NSimSun", "Songti SC", "STSong", "Noto Serif CJK SC", "Source Han Serif SC", "思源宋体")' "$TMP_DIR/clean.typ"
grep -Fq '#let FONT_XBS = ("FZXiaoBiaoSong-B05", "FZXiaoBiaoSong-B05S", "FZXiaoBiaoSongS-B-GB", "方正小标宋简体", "方正小标宋_GBK")' "$TMP_DIR/clean.typ"

if grep '^#let FONT_HEI' "$TMP_DIR/clean.typ" | grep -Eq 'SimSun|STSong|Serif|宋体'; then
  printf '黑体 fallback 中出现了宋体类字体。\n' >&2
  exit 1
fi

if grep '^#let FONT_SONG' "$TMP_DIR/clean.typ" | grep -Eq 'SimHei|STHeiti|Sans|黑体'; then
  printf '宋体 fallback 中出现了黑体类字体。\n' >&2
  exit 1
fi

if grep '^#let FONT_XBS' "$TMP_DIR/clean.typ" | grep -Eq 'SimSun|STSong|Songti|Serif|宋体'; then
  printf '小标宋 fallback 中出现了宋体类字体。\n' >&2
  exit 1
fi

printf 'gongwen 标题归一化与字体 fallback 测试通过。\n'
