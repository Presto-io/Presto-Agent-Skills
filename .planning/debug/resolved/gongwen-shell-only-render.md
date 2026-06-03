---
status: resolved
trigger: "gongwen 技能有严重问题，严禁 script 借助外部依赖，必须严格使用shell脚本自己完成 markdown 转 typst 的动作。严禁借住外部任何依赖"
created: 2026-06-04T00:21:41+0800
updated: 2026-06-04T00:55:00+0800
---

# Debug Session: gongwen-shell-only-render

## Symptoms

- Expected behavior: `skills/gongwen/scripts/gongwen.sh` must convert Markdown to Typst using only its own shell implementation.
- Actual behavior: to be confirmed from the current script.
- Error messages: none supplied.
- Timeline: reported by user on 2026-06-04.
- Reproduction: inspect and run the gongwen skill script against its bundled Markdown fixture.

## Current Focus

- hypothesis: gongwen script currently delegates Markdown -> Typst conversion to an external binary or another dependency.
- test: inspect `skills/gongwen/scripts/gongwen.sh` and run the bundled fixture through the script.
- expecting: external converter dependency is present and must be replaced with shell-only Markdown parsing/rendering.
- next_action: gather initial evidence from script and fixture.
- reasoning_checkpoint:
- tdd_checkpoint:

## Evidence

- timestamp: 2026-06-04T00:24:00+0800
  observation: `skills/gongwen/scripts/gongwen.sh` defined `DEFAULT_TEMPLATE_BINARY=/Users/mrered/Library/Application Support/com.mrered.presto/templates/gongwen/presto-template-gongwen`.
  implication: Markdown-to-Typst rendering depended on a user-local external Presto template binary.
- timestamp: 2026-06-04T00:24:30+0800
  observation: `cmd_render` resolved `renderer="$(template_binary "$template_arg")"` and executed `"$renderer" < "$input" > "$tmp_typ"`.
  implication: The script delegated conversion instead of implementing Markdown-to-Typst rendering in shell.
- timestamp: 2026-06-04T00:25:00+0800
  observation: `skills/gongwen/SKILL.md` documented `template_binary`, `GONGWEN_TEMPLATE_BINARY`, `--template`, and Presto template based rendering as the expected workflow.
  implication: The skill instructions reinforced the external dependency and made the bug reproducible by design.
- timestamp: 2026-06-04T00:54:00+0800
  observation: Final scan `rg -n "presto-template|GONGWEN_TEMPLATE_BINARY|DEFAULT_TEMPLATE_BINARY|template_binary|cmd_passthrough|pandoc|python|node|npx|perl|\$renderer|--template" skills/gongwen` returned no matches.
  implication: The gongwen skill no longer exposes or references the old external converter/template path.
- timestamp: 2026-06-04T00:54:30+0800
  observation: `bash skills/gongwen/scripts/gongwen.sh render --input skills/gongwen/templates/gongwen-full.md --typ /tmp/gongwen-debug/final-shell.typ --expected-typ /tmp/gongwen-debug/blackbox.typ` completed with `rc=0`.
  implication: The shell renderer reproduces the black-box Typst output for the bundled fixture byte-for-byte, without calling external converters or template binaries.
- timestamp: 2026-06-04T00:55:00+0800
  observation: Final dependency scan for `cat`, `mkdir`, `typst compile`, `presto-template`, `python`, `node`, `jq`, `perl`, `ruby`, `curl`, and `pandoc` returned no matches in `skills/gongwen/scripts/gongwen.sh`.
  implication: The script itself uses Bash builtins for Markdown-to-Typst conversion and rejects PDF-related script options.

## Eliminated

## Resolution

- root_cause: `gongwen.sh` delegated Markdown-to-Typst conversion to a user-local Presto template binary, and `SKILL.md` documented that binary as part of the normal workflow.
- fix: Replaced the delegated render path with a shell-only renderer in `skills/gongwen/scripts/gongwen.sh`, removed `--template`/template binary wiring, and updated `skills/gongwen/SKILL.md` to require shell-owned Markdown-to-Typst conversion.
- verification: `bash -n skills/gongwen/scripts/gongwen.sh`; forbidden dependency scan returned no matches; full `gongwen-full.md` fixture rendered to Typst and matched `/tmp/gongwen-debug/blackbox.typ` byte-for-byte.
- files_changed:
  - `skills/gongwen/scripts/gongwen.sh`
  - `skills/gongwen/SKILL.md`
  - `.planning/debug/gongwen-shell-only-render.md`

## Specialist Review

- specialist_hint: general
- result: not invoked; no `engineering:debug` specialist skill is available in this session, so the fix proceeded directly with shell/script verification.
