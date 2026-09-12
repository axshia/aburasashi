# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.5.1] - 2026-09-12

### Fixed

- Prefer native `gh` 2.99.0+ image and video attachments in the ReDoc and
  Playwright PR evidence workflows, with documented support checks and a
  browser fallback.
- Generate normal relative image references in ReDoc comparison Markdown so
  `gh --attach` can publish images in their intended table cells.
- Recover partial uploads without duplicating successful attachments or
  overwriting Playwright result history, and distinguish saved attachment URLs
  from signed browser image sources during verification.

## [0.5.0] - 2026-09-07

### Added

- Web Design from References skill for section-by-section web mockups from
  required concept and content-wireframe images, with explicit input roles,
  shared visual direction, exact copy, and targeted correction guidance.

## [0.4.0] - 2026-08-22

### Added

- Figma iOS Simulator Parity skill for checking and correcting SwiftUI or
  UIKit screens against exact Figma nodes on pinned devices, runtimes, traits,
  and capture boundaries while preserving native platform behavior.
- Figma Web Parity skill for checking and correcting an in-progress web
  implementation against an exact Figma node with normalized render conditions,
  root-cause-driven visual diffs, and an explicit no-Figma non-trigger gate.

## [0.3.0] - 2026-08-22

### Added

- Playwright PR QA skill with an explicit owner-approval gate, isolated
  multi-user sessions, labeled desktop/mobile evidence, append-only checkpoint
  comments, and failure-to-retry handoff rules.
- Automatic GitHub tag and Release creation after a validated plugin version
  change is merged into `main`.

## [0.2.0] - 2026-08-22

### Added

- OpenAPI ReDoc PR Screenshots skill with transient headless rendering,
  per-endpoint comparison tables, change and removal annotations, and versioned
  sample specifications and captures.

## [0.1.0] - 2026-08-22

### Added

- Cross-compatible Claude Code and Codex plugin manifests.
- Repository marketplace catalogs for both plugin hosts.
- Dependency-free validation, release checks, and GitHub Actions CI.
- Contribution and publishing documentation.

[Unreleased]: https://github.com/axshia/aburasashi/compare/v0.5.1...HEAD
[0.5.1]: https://github.com/axshia/aburasashi/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/axshia/aburasashi/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/axshia/aburasashi/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/axshia/aburasashi/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/axshia/aburasashi/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/axshia/aburasashi/releases/tag/v0.1.0
