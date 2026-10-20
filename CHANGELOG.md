# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `Format_Standard/` tooling and audit artifacts for the instance-format unification:
  - `统一格式规范.md` — the agreed normalization spec (lowercased tags, `number of mated-stations` consolidation, single `<end>` terminator; precedence relations and task-time columns unchanged).
  - `normalize_instances.py` — the reusable normalizer (skips RALSP, writes to `normalized_output/`, never overwrites sources).
  - `update_project_docs.py` — bumps VERSION/CHANGELOG/README across the 12 ALBP repos.
  - `normalized_sample/` — 8 representative before/after examples for audit.

## [1.1.0] - 2026-10-21

### Changed
- Unified the instance file format across the entire dataset:
  - All `<tag>` header labels are now lowercased (e.g., `Precedence relations` -> `precedence relations`).
  - `number of mated-station` and `mated-station number` are consolidated to `number of mated-stations`; `number of stations` is left unchanged.
  - Every file now ends with exactly one `<end>` tag; trailing blank lines are removed while internal blank lines are preserved.
- Precedence relations (both the `i,j` and `i j 1` forms) and the task-time column layouts are intentionally left unchanged to keep downstream parsers compatible.


## [1.0.0] - 2026-10-12

### Added
- Unified project documentation: add CHANGELOG.md (this file) and a single-line VERSION, and append a documentation index to README.
