#!/usr/bin/env bash
set -euo pipefail

TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$TEST_DIR/.." && pwd)"
RENDERER="$SKILL_DIR/scripts/gongwen.sh"
INPUT_TEMPLATE="$SKILL_DIR/templates/gongwen.md"
TMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/gongwen-clean-delivery.XXXXXX")"
BIN_DIR="$TMP_DIR/bin"
mkdir "$BIN_DIR"
trap 'rm -rf "$TMP_DIR"' EXIT

fail() {
  printf 'FAIL: %s\n' "$*" >&2
  exit 1
}

write_fake_typst() {
  local mode="$1"
  case "$mode" in
    success)
      cat > "$BIN_DIR/typst" <<'SH'
#!/bin/sh
printf '%%PDF-1.7\n' > "$3"
cat "$2" >> "$3"
printf '%%%%EOF\n' >> "$3"
SH
      ;;
    invalid)
      cat > "$BIN_DIR/typst" <<'SH'
#!/bin/sh
printf 'not-a-pdf\n' > "$3"
SH
      ;;
    failure)
      cat > "$BIN_DIR/typst" <<'SH'
#!/bin/sh
printf 'forced compile failure\n' >&2
exit 7
SH
      ;;
    *) fail "unknown fake typst mode: $mode" ;;
  esac
  chmod +x "$BIN_DIR/typst"
}

new_input() {
  local path="$1" marker="$2"
  cp "$INPUT_TEMPLATE" "$path"
  printf '\n%s\n' "$marker" >> "$path"
}

run_render() {
  local root="$1" input="$2" pdf_mode="$3"
  shift 3
  local args=(render --input "$input" --typ "$root/notice.typ")
  if [[ "$pdf_mode" == pdf ]]; then
    args+=(--pdf "$root/notice.pdf")
  fi
  PATH="$BIN_DIR:$PATH" "$RENDERER" "${args[@]}" "$@"
}

snapshot() {
  local root="$1"
  if [[ ! -e "$root" ]]; then
    printf '<missing>\n'
    return
  fi
  (
    cd "$root"
    find . -type d -print | LC_ALL=C sort
    find . -type f -exec cksum {} \; | LC_ALL=C sort
    find . -type l -exec sh -c 'for path do printf "%s -> %s\n" "$path" "$(readlink "$path")"; done' sh {} + | LC_ALL=C sort
  )
}

assert_clean_work() {
  local root="$1"
  [[ ! -e "$root/.work" ]] || fail "owned .work was not cleaned: $root"
}

write_fake_typst success

input_v1="$TMP_DIR/v1.md"
input_v2="$TMP_DIR/v2.md"
input_v3="$TMP_DIR/v3.md"
new_input "$input_v1" '版本一'
new_input "$input_v2" '版本二'
new_input "$input_v3" '版本三'

root="$TMP_DIR/main"
mkdir "$root"
run_render "$root" "$input_v1" no_pdf >/dev/null
[[ -f "$root/notice.md" && -f "$root/notice.typ" ]] || fail 'pair first publish missing files'
[[ ! -e "$root/notice.pdf" && ! -e "$root/history" ]] || fail 'pair first publish polluted root'
assert_clean_work "$root"

before_inode="$(stat -f '%i:%m' "$root/notice.typ" 2>/dev/null || stat -c '%i:%Y' "$root/notice.typ")"
run_render "$root" "$input_v1" no_pdf >/dev/null
after_inode="$(stat -f '%i:%m' "$root/notice.typ" 2>/dev/null || stat -c '%i:%Y' "$root/notice.typ")"
[[ "$before_inode" == "$after_inode" && ! -e "$root/history" ]] || fail 'identical pair was not an exact no-op'

run_render "$root" "$input_v1" pdf >/dev/null
[[ -f "$root/notice.pdf" && "$(head -c 5 "$root/notice.pdf")" == '%PDF-' ]] || fail 'optional PDF was not validated and published'
[[ -f "$root/history/001/notice.md" && -f "$root/history/001/notice.typ" && ! -e "$root/history/001/notice.pdf" ]] || fail 'pair was not archived as a whole bundle'
run_render "$root" "$input_v2" pdf >/dev/null
[[ -f "$root/history/002/notice.pdf" ]] || fail 'triple change did not archive the old triple'
run_render "$root" "$input_v3" no_pdf >/dev/null
[[ -f "$root/history/003/notice.pdf" && ! -e "$root/notice.pdf" ]] || fail 'optional PDF removal did not archive the old triple'

gap_root="$TMP_DIR/gap"
mkdir -p "$gap_root/history/001" "$gap_root/history/003"
for sequence in 001 003; do
  printf 'old md %s\n' "$sequence" > "$gap_root/history/$sequence/notice.md"
  printf 'old typ %s\n' "$sequence" > "$gap_root/history/$sequence/notice.typ"
done
run_render "$gap_root" "$input_v1" no_pdf >/dev/null
run_render "$gap_root" "$input_v2" no_pdf >/dev/null
[[ -d "$gap_root/history/004" ]] || fail 'history max+1 did not preserve gaps'

fault_root="$TMP_DIR/faults"
mkdir "$fault_root"
run_render "$fault_root" "$input_v1" pdf >/dev/null
mkdir "$fault_root/sources"
printf 'keep-source\n' > "$fault_root/sources/facts.txt"
faults=(after_candidate_validation after_history_reservation after_archive_snapshot after_publish_file_1 after_publish_middle_file before_post_publish_verify before_work_cleanup)
for fault in "${faults[@]}"; do
  before="$(snapshot "$fault_root")"
  if PRESTO_CLEAN_DELIVERY_FAULT="$fault" run_render "$fault_root" "$input_v2" pdf >"$TMP_DIR/$fault.out" 2>&1; then
    fail "fault unexpectedly succeeded: $fault"
  fi
  [[ "$(snapshot "$fault_root")" == "$before" ]] || fail "fault changed current/history/sources: $fault"
  assert_clean_work "$fault_root"
done

for signal_name in INT TERM; do
  before="$(snapshot "$fault_root")"
  if PRESTO_CLEAN_DELIVERY_SIGNAL="$signal_name" run_render "$fault_root" "$input_v2" pdf >"$TMP_DIR/signal-$signal_name.out" 2>&1; then
    fail "signal injection unexpectedly succeeded: $signal_name"
  fi
  [[ "$(snapshot "$fault_root")" == "$before" ]] || fail "signal changed current/history/sources: $signal_name"
  assert_clean_work "$fault_root"
done

before="$(snapshot "$fault_root")"
expected="$TMP_DIR/expected.typ"
printf 'different\n' > "$expected"
if run_render "$fault_root" "$input_v2" pdf --expected-typ "$expected" >"$TMP_DIR/expected.out" 2>&1; then
  fail 'expected mismatch unexpectedly succeeded'
fi
[[ "$(snapshot "$fault_root")" == "$before" ]] || fail 'expected mismatch mutated delivery'

write_fake_typst failure
if run_render "$fault_root" "$input_v2" pdf >"$TMP_DIR/compile.out" 2>&1; then fail 'compile failure unexpectedly succeeded'; fi
[[ "$(snapshot "$fault_root")" == "$before" ]] || fail 'compile failure mutated delivery'
write_fake_typst invalid
if run_render "$fault_root" "$input_v2" pdf >"$TMP_DIR/invalid.out" 2>&1; then fail 'invalid PDF unexpectedly succeeded'; fi
[[ "$(snapshot "$fault_root")" == "$before" ]] || fail 'invalid PDF mutated delivery'
write_fake_typst success

for unsafe in unknown.txt .gongwen media; do
  unsafe_root="$TMP_DIR/unsafe-$unsafe"
  mkdir "$unsafe_root"
  if [[ "$unsafe" == unknown.txt ]]; then printf 'unknown\n' > "$unsafe_root/$unsafe"; else mkdir "$unsafe_root/$unsafe"; fi
  before="$(snapshot "$unsafe_root")"
  if run_render "$unsafe_root" "$input_v1" no_pdf >"$TMP_DIR/unsafe.out" 2>&1; then fail "unsafe root entry accepted: $unsafe"; fi
  [[ "$(snapshot "$unsafe_root")" == "$before" ]] || fail "unsafe root entry was mutated: $unsafe"
done

symlink_root="$TMP_DIR/symlink-root"
outside="$TMP_DIR/outside"
mkdir "$symlink_root" "$outside"
printf 'sentinel\n' > "$outside/sentinel"
ln -s "$outside/sentinel" "$symlink_root/notice.typ"
before="$(snapshot "$symlink_root")"
if run_render "$symlink_root" "$input_v1" no_pdf >"$TMP_DIR/symlink.out" 2>&1; then fail 'symlink current accepted'; fi
[[ "$(snapshot "$symlink_root")" == "$before" && "$(cat "$outside/sentinel")" == sentinel ]] || fail 'symlink target was touched'

if run_render "$TMP_DIR/path-root" "$input_v1" pdf --pdf "$TMP_DIR/other/notice.pdf" >"$TMP_DIR/cross-root.out" 2>&1; then fail 'cross-root PDF accepted'; fi
mkdir -p "$TMP_DIR/path-root"
if PATH="$BIN_DIR:$PATH" "$RENDERER" render --input "$input_v1" --typ "$TMP_DIR/path-root/notice.typ" --pdf "$TMP_DIR/path-root/other.pdf" >"$TMP_DIR/stem.out" 2>&1; then fail 'different-stem PDF accepted'; fi
if PATH="$BIN_DIR:$PATH" "$RENDERER" render --input "$input_v1" --typ "$TMP_DIR/path-root/../escape.typ" >"$TMP_DIR/traversal.out" 2>&1; then fail 'path traversal accepted'; fi

lock_root="$TMP_DIR/lock"
mkdir "$lock_root"
PRESTO_CLEAN_DELIVERY_LOCK_HOLD_SECONDS=2 run_render "$lock_root" "$input_v1" no_pdf >"$TMP_DIR/lock-first.out" 2>&1 &
first_pid=$!
for _ in 1 2 3 4 5 6 7 8 9 10; do
  [[ -d "$lock_root/.work/lock" ]] && break
  sleep 0.1
done
[[ -d "$lock_root/.work/lock" ]] || fail 'first publisher did not acquire lock'
if run_render "$lock_root" "$input_v2" no_pdf >"$TMP_DIR/lock-second.out" 2>&1; then fail 'concurrent publisher acquired lock'; fi
wait "$first_pid"
grep -Fq '版本一' "$lock_root/notice.md" || fail 'lock winner did not publish its candidate'
assert_clean_work "$lock_root"

stale_root="$TMP_DIR/stale"
mkdir -p "$stale_root/.work/unrelated"
printf 'keep\n' > "$stale_root/.work/unrelated/evidence.txt"
before="$(snapshot "$stale_root")"
if run_render "$stale_root" "$input_v1" no_pdf >"$TMP_DIR/stale.out" 2>&1; then fail 'unrelated stale work accepted'; fi
[[ "$(snapshot "$stale_root")" == "$before" ]] || fail 'unrelated stale work was cleaned'

if rg -n 'rm[[:space:]]+(-[^[:space:]]+[[:space:]]+)*"?\$[^[:space:]]*"?/\*|find[^\n]*-delete' "$SKILL_DIR/scripts/gongwen_lib/delivery.sh"; then
  fail 'broad root cleanup found in delivery.sh'
fi
if rg -n 'python|node|test/clean-delivery|skills/[^g]' "$SKILL_DIR/scripts/gongwen_lib/delivery.sh"; then
  fail 'delivery.sh has a forbidden runtime or cross-skill dependency'
fi

printf 'gongwen clean-delivery transaction tests passed.\n'
