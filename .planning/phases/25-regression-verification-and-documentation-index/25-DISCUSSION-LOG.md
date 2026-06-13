# Phase 25: Regression Verification and Documentation Index - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-06-14
**Phase:** 25-Regression Verification and Documentation Index
**Areas discussed:** Public command regression scope, package failure and manifest behavior, runtime adapter coverage, documentation and index discoverability, verification artifact shape

---

## Public Command Regression Scope

| Option | Description | Selected |
|--------|-------------|----------|
| Minimal package-only smoke | Verify only `teaching-design-package` commands and rely on prior phases for standalone skills. | |
| Broad black-box public command regression | Smoke standalone jiaoan and end-of-term commands plus package composer commands from temporary paths. | ✓ |
| Static docs-only verification | Check command names in docs without executing public scripts. | |

**User's choice:** `[auto]` Broad black-box public command regression.
**Notes:** Phase 25 owns TDP-15, so it should prove `jiaoan-jihua`, `jiaoan-shicao`, and `end-of-term-teaching-materials` remain usable after integration. Static checks alone are too weak.

---

## Package Failure and Manifest Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Require full PDF success locally | Treat missing PDF tooling as a verification failure. | |
| Assert honest manifest/status semantics | Verify explicit `not_run`, `failed`, `blocked_review`, `merge_unavailable`, or related statuses when outputs are unavailable. | ✓ |
| Skip unavailable-tool paths | Only test successful Typst paths and leave PDF/merge gaps unverified. | |

**User's choice:** `[auto]` Assert honest manifest/status semantics.
**Notes:** TDP-14 requires explicit evidence instead of false success. The correct regression gate is truthful status behavior, not local availability of every PDF tool.

---

## Runtime Adapter Coverage

| Option | Description | Selected |
|--------|-------------|----------|
| Name-only runtime grep | Check that the six runtime names appear somewhere in each affected `SKILL.md`. | |
| Practical adapter coverage check | Check names plus support-file discovery, script permissions, sandbox/write-path notes, and OpenClaw/Hermes fallback language. | ✓ |
| Defer runtime coverage to future milestone | Do not verify adapters in Phase 25. | |

**User's choice:** `[auto]` Practical adapter coverage check.
**Notes:** OpenClaw and Hermes Agent are required targets. Phase 25 should catch adapter notes that merely name the runtime without useful installation/permission guidance.

---

## Documentation and Index Discoverability

| Option | Description | Selected |
|--------|-------------|----------|
| README only | Verify only top-level README discoverability. | |
| Full index and directory guidance check | Verify README, skills index, directory spec, compatibility matrix, and linked artifact contracts. | ✓ |
| Rewrite docs broadly | Rework repository guidance while verifying. | |

**User's choice:** `[auto]` Full index and directory guidance check.
**Notes:** TDP-16 is about discoverability and guidance preservation. The scope should remain index-focused, not a broad documentation rewrite.

---

## Verification Artifact Shape

| Option | Description | Selected |
|--------|-------------|----------|
| Manual-only command list | Put commands in verification notes with no reusable runner. | |
| Focused rerunnable verification evidence | Prefer a small regression matrix or script if planning finds it useful, plus recorded `25-VERIFICATION.md` results. | ✓ |
| Heavy framework or shared harness | Build a new general regression framework. | |

**User's choice:** `[auto]` Focused rerunnable verification evidence.
**Notes:** A narrow artifact is enough for this phase. Avoid new framework work unless planning shows a concrete need.

---

## Claude's Discretion

- Conservative defaults were selected because the user explicitly authorized `--auto`.
- The discussion did not ask broad direction questions.
- The SDK phase lookup mismatch was recorded instead of blocking context capture, because roadmap and state files clearly define Phase 25.

## Deferred Ideas

- Fixing any discovered regressions belongs to Phase 25 plan/execute.
- Repairing `gsd-sdk query init.phase-op 25` phase lookup belongs to a separate tooling task unless the Phase 25 plan explicitly includes a narrow note.
- Generated runtime wrappers and new adapter packaging remain future scope.
