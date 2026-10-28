# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.11.0] - 2026-10-28

### Changed

- Japanese PR Writing writes new PR descriptions and structural rewrites in
  three steps: outline the conclusion, section roles, and one point per
  paragraph; compose the Japanese directly from the outline instead of writing
  in English and translating; then revise with the existing naturalness checks.
  Editing-only requests keep the existing structure.
- Japanese PR Writing now orders new PR descriptions as background, approach,
  changes, review points, validation, and out-of-scope items, requires a
  change-type prefix in titles, and adds guidance for plain wording, quoted UI
  labels, conditions, and one sentence per line.
- Japanese PR Writing drafts inline review comments, including numbered
  `メイントピック` headings for the main changes.

### Added

- When Japanese PR Writing runs in Claude Code, it asks Codex
  `gpt-6.1-terra` to draft PR titles and descriptions through the codex plugin
  or the codex CLI, then checks the draft against the facts. It does not
  substitute another model when Terra 6.1 is unavailable.

## [0.10.1] - 2026-10-11

### Changed

- Japanese Article Writing chooses the opening by article type: how-to,
  comparison, and proposal articles may open with a short, topic-specific scene
  as long as the conclusion or key points come before the first heading, while
  tech blogs and important announcements still open with the conclusion. It
  separates such scenes from generic hooks and forbids presenting imagined
  scenes as real experiences, quotes, or trends.
- Add pacing rules, a calm and friendly default voice that avoids both stiff and
  childish narration, and comparison-table rules: state the conditions first,
  ask one question per item, use five status labels, and never turn "not
  stated" into "not supported". Revise the conclusion-first, lead-order, and
  AI-pattern rules that conflicted with these changes.

## [0.10.0] - 2026-10-11

### Added

- Japanese Article Writing skill for Japanese articles published to outside
  readers: conclusion-first leads, paragraphs that open with their point,
  first-hand facts at the center, article-type templates, and rewrites of
  common AI-sounding patterns. It asks for missing first-hand facts or marks
  where they belong instead of padding to a word count.

### Changed

- Add point-first paragraphs and one point per sentence to Japanese Native
  Writing, and known-to-new sentence order, one point per sentence, and
  double-negative rewrites to Japanese PR Writing, limited to failures seen in
  before-and-after evaluations; route article bodies to Japanese Article
  Writing.

## [0.9.0] - 2026-09-15

### Added

- Playwright E2E Recording skill for immediately runnable browser scenarios,
  video of every attempt, checkpoint screenshots, and structured PR evidence.
- A standalone recording runner, a note.com walkthrough example, and local
  browser checks covering success, closed popups, failure, blockers, and
  incomplete scenarios.

### Changed

- Connect recorded E2E artifacts to Japanese PR Writing and Playwright PR QA,
  preserving validation status, media review, and publication boundaries.

## [0.8.1] - 2026-09-14

### Changed

- Invoke `logical-thinking` for specification and requirements formulation,
  UI/UX design, and marketing thinking, including small decisions within other
  tasks; add native-host activation cases and retain settled-task boundaries.

## [0.8.0] - 2026-09-14

### Added

- Logical Thinking skill for evaluating mismatches with expectations, comparing
  approaches, and explaining decisions with explicit evidence and constraints.
  Includes scoped trigger cues, cross-domain examples, and ten behavioral
  evaluation cases with separate inputs and grading criteria.

## [0.7.0] - 2026-09-14

### Added

- Using Aburasashi bootstrap skill that establishes the 1% trigger rule: invoke
  an aburasashi skill before responding whenever there is even a 1% chance it
  applies, and let the skill check its own inputs instead of postponing the
  invocation.
- Claude Code `SessionStart` hook that injects the bootstrap skill at startup,
  after `/clear`, and after compaction, with an empty `hooks` object in the
  Codex manifest so Codex keeps native skill discovery.
- Repository validation for the hook registration, executable hook scripts,
  and the injected session context.
- Japanese Native Writing skill that shapes Japanese replies and documents for
  the user: conclusion and consequence first, explicit done, unverified,
  not-done, unknown, and missing-input status, options with trade-offs and a
  single decision, terms glossed on first use, sparse emphasis, and ASCII
  diagrams only where relationships need them.

## [0.6.0] - 2026-09-13

### Added

- Japanese PR Writing skill for clear, natural Japanese pull request copy,
  with primary-source research and examples that preserve technical meaning,
  validation status, and Markdown structure.

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

[Unreleased]: https://github.com/axshia/aburasashi/compare/v0.11.0...HEAD
[0.11.0]: https://github.com/axshia/aburasashi/compare/v0.10.1...v0.11.0
[0.10.1]: https://github.com/axshia/aburasashi/compare/v0.10.0...v0.10.1
[0.10.0]: https://github.com/axshia/aburasashi/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/axshia/aburasashi/compare/v0.8.1...v0.9.0
[0.8.1]: https://github.com/axshia/aburasashi/compare/v0.8.0...v0.8.1
[0.8.0]: https://github.com/axshia/aburasashi/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/axshia/aburasashi/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/axshia/aburasashi/compare/v0.5.1...v0.6.0
[0.5.1]: https://github.com/axshia/aburasashi/compare/v0.5.0...v0.5.1
[0.5.0]: https://github.com/axshia/aburasashi/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/axshia/aburasashi/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/axshia/aburasashi/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/axshia/aburasashi/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/axshia/aburasashi/releases/tag/v0.1.0
