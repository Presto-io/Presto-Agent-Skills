---
phase: 42
slug: markdown-contract-and-full-fixture
status: verified
threats_open: 0
asvs_level: 1
created: 2026-07-14
---

# Phase 42 — Security

> Per-phase security contract: threat register, accepted risks, and audit trail.

---

## Trust Boundaries

| Boundary | Description | Data Crossing |
|----------|-------------|---------------|
| Untrusted Markdown/YAML -> logical model | Teacher- or agent-authored input may be malformed, oversized, misleading, or contain forbidden executable/styling constructs. | Frontmatter, slide containers, fenced code, tables, notes, and media references |
| Manifest bytes -> validator state | The human-editable manifest is trusted only after bounded YAML parsing and structural validation. | Theme, layout, authorability, and budget configuration |
| Media references -> filesystem | Authored paths may traverse, resolve to missing/non-file targets, or expose machine-specific locations. | Relative and absolute local media paths and metadata |
| Logical model/diagnostics -> JSON and terminal | Validation output must remain truthful, deterministic, bounded, and free of traceback/source disclosure. | Diagnostics, locations, logical JSON, and exit status |
| Caller-controlled output -> filesystem | Output paths and parents may collide, traverse, or be exchanged with symlinks during publication. | One logical JSON file or five fixed example-owned files |
| Regression harness -> completion claim | A security closure claim is trusted only when every registered reproduction and prior regression gate executes. | Test registry, process result, and audit evidence |

---

## Threat Register

| Threat ID | Category | Component | Disposition | Mitigation | Status |
|-----------|----------|-----------|-------------|------------|--------|
| T-42-01 | Tampering | Markdown/YAML state machine | mitigate | Strict allowlists, safe YAML composition, explicit parser states, aggregate validation, and non-zero invalid exits; covered by `fixture-example`. | closed |
| T-42-02 | Elevation of Privilege | Raw HTML/style/coordinate/font/color syntax | mitigate | Reject forbidden syntax outside opaque fenced code and never execute HTML; covered by aggregate-negative and fence gates. | closed |
| T-42-03 | Information Disclosure | Media resolution | mitigate | Resolve only from the input parent or explicit absolute path, perform local file checks, and omit media bytes/source dumps from diagnostics. | closed |
| T-42-04 | Tampering | Path traversal and output collision | mitigate | Normalize paths, keep media read-only, require explicit JSON output, and reject identity/directory collisions; covered by collision gates. | closed |
| T-42-05 | Information Disclosure | Diagnostics and internal exceptions | mitigate | Emit bounded structured diagnostics without traceback or source dumps and keep deterministic output fields. | closed |
| T-42-06 | Denial of Service | Oversized or malformed input | mitigate | Enforce byte, line, YAML-node, nesting, block, and diagnostic limits; covered by resource gates. | closed |
| T-42-07 | Repudiation | Validation outcome | mitigate | Preserve deterministic sorted errors and return success only when the error list is empty. | closed |
| T-42-08 | Spoofing | Controlled theme/layout identifiers | mitigate | Derive theme/layout truth from the manifest and reject explicit template-owned `closing`. | closed |
| T-42-09 | Tampering | Fixed example copier | mitigate | Restrict ownership to one Markdown plus four media files, validate after copy, and assert exact paths and byte determinism. | closed |
| T-42-10 | Elevation of Privilege | Traversal/symlink escape | mitigate | Use normalized fixed destinations and no-follow directory-descriptor operations; covered by root/media exchange gates. | closed |
| T-42-11 | Denial of Service | Destructive output replacement | mitigate | Forbid recursive/glob deletion and preserve caller sentinels and unrelated paths on success and failure. | closed |
| T-42-12 | Tampering | Copied Markdown/YAML injection | mitigate | Revalidate copied source through the same parser and retain raw-HTML/style/fence negative regressions. | closed |
| T-42-13 | Information Disclosure | Canonical media paths | mitigate | Keep canonical media relative and skill-local, never copy external media, and exclude machine paths from examples. | closed |
| T-42-14 | Information Disclosure | Example diagnostics | mitigate | Bound collision/failure output and suppress traceback, source contents, and machine-sensitive paths. | closed |
| T-42-15 | Repudiation | Fixture completeness claim | mitigate | Assert layouts, contents order, notes isolation, media existence, overflow evidence, hashes, and canonical JSON. | closed |
| T-42-16 | Spoofing | Command-owned files | mitigate | Define a fixed ownership manifest; no glob, discovery, caller filename, or authored path expands write authority. | closed |
| T-42-17 | Tampering | YAML metadata | mitigate | Accept only composed string scalars and reject implicit typed values with `YAML_VALUE_TYPE` in plain and JSON modes. | closed |
| T-42-18 | Tampering | Slide container state | mitigate | Track matching fence markers before interpreting directives/headings and preserve directive-like code as opaque payload. | closed |
| T-42-19 | Tampering | Table/timeline model | mitigate | Require a valid separator and equal row widths before emitting accepted logical table semantics. | closed |
| T-42-20 | Information Disclosure | Manifest/internal failures | mitigate | Initialize safe state and map unreadable, malformed, and invalid-root manifests to bounded diagnostics without traceback. | closed |
| T-42-21 | Elevation of Privilege | Output root/parent exchange | mitigate | Fail closed without required descriptor capabilities, hold no-follow parent descriptors, publish relative to them, and verify pathname/inode identity. | closed |
| T-42-22 | Repudiation | Gap closure claim | mitigate | Register all five reproduced gaps plus the secure-I/O capability companion under the authoritative aggregate command. | closed |
| T-42-23 | Denial of Service | Malformed input/failure output | mitigate | Retain input limits and require bounded output for manifest, type, table, and race failures. | closed |
| T-42-SC | Tampering | Package installation | mitigate | Phase 42 adds no package-manager dependency; any future install requires legitimacy research and a blocking human check. | closed |

*Status: open · closed*
*Disposition: mitigate (implementation required) · accept (documented risk) · transfer (third-party)*

---

## Accepted Risks Log

No accepted risks.

---

## Security Audit Trail

| Audit Date | Threats Total | Closed | Open | Run By |
|------------|---------------|--------|------|--------|
| 2026-07-14 | 24 | 24 | 0 | Codex secure-phase workflow |

Verification evidence: `python3 -m py_compile skills/school-pptx/scripts/markdown_contract.py skills/school-pptx/scripts/verify_markdown_contract.py` and `python3 skills/school-pptx/scripts/verify_markdown_contract.py fixture-example` both exited 0 on 2026-07-14. The aggregate explicitly passed YAML type checks, fence opacity, table structure, manifest failures, descriptor capability fail-closed behavior, output-root exchange, media-parent exchange, full coverage, determinism, ownership, variants, collisions, and Phase 41 regressions.

---

## Sign-Off

- [x] All threats have a disposition (mitigate / accept / transfer)
- [x] Accepted risks documented in Accepted Risks Log
- [x] `threats_open: 0` confirmed
- [x] `status: verified` set in frontmatter

**Approval:** verified 2026-07-14
