# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
