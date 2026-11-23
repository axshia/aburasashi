# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Japanese PR Writing explains when readers need product-specific context to
  understand a change, why related actions behave differently, and what the
  change means for operators. A worked invoice example shows how to keep the
  PR template and add a subsection for that context.

## [0.14.3] - 2026-11-19

### Changed

- Japanese Doc Writing names a ticket by its kind: a ticket under a story
  keeps the story's form (what the user can do), and a ticket outside a story
  is named as work to do ("〜を追加する"), with a before-and-after example in
  `references/tickets.md`.
- Japanese Doc Writing adds optional ticket sections to
  `references/tickets.md`: ゴール written as "〜のとき、〜になる", PR と依存 with
  an estimate and its basis per pull request, and 実装の参考になる資料 that
  points to where to look without proposing code, file lists, or names. It
  also adds how to split a story into tickets and agree on the split before
  writing them.
- Japanese Doc Writing and Using Aburasashi add the cues "タスク化して",
  "サブタスクの本文を書いて", and "チケットを具体化して".

## [0.14.2] - 2026-11-19

### Changed

- Japanese Doc Writing changes the thin ticket form to "概要 → このチケットで
  解決したい課題 → 中身が分かる見出しの節 → 確認すること → やること・やらない
  こと・依存するチケット → 付録". The 概要 starts with what the ticket does, not
  with "このチケットで、", and the current behavior and the diagram move into
  the 課題 section. A new reference, `references/tickets.md`, holds the form,
  what to check before writing, and before-and-after examples.
- Japanese Doc Writing adds a form for a document that asks for agreement on a
  plan ("今の動き → 解決したい問題 → やりたいこと → 決めてほしいこと → まだ確か
  めていないこと → 付録") in `references/consultations.md`, with the images to
  pair: a flow diagram and a real screen capture for the current behavior, and
  the same diagram shape and a composite of the same screen for the proposal.
- Japanese Doc Writing links other tickets with "ID and title" instead of the
  ID alone, names the table of a column on first mention, separates what a
  person answered from what the writer verified, rewrites "確認すること" into
  "確認した内容について" once the answer arrives, and asks to check the basis
  of a ticket's premise before writing. "決まらないと何が進められないか" is no
  longer required on every decision item, and how the document was made or
  which examples it followed is no longer written in the document.
- Focused Screen Captures adds "提案のイメージを作る": add the proposed element
  to the DOM of the same real screen by cloning a similar existing part,
  capture it with the same viewport and frame as the current screen, remove
  the element, and state that the image is a composite with an undecided
  design.
- Excalidraw Diagrams leaves out the person icon when every row has the same
  actor, and labels a step outside the current work with whether it is already
  implemented or which work covers it.
- Using Aburasashi adds the cues "チケットを書いて", "合意を取る資料", "相談資料",
  and "提案のイメージ".

## [0.14.1] - 2026-11-18

### Changed

- Using Aburasashi routes HTML pages and mocks that explain something with
  diagrams to Japanese Doc Writing, with the cues "図で見せて" and
  "ブラウザで見せて". Two new red flags stop treating such a page as "not a
  document", and stop replacing identifiers and team terms with metaphors or
  plain words when the user says the text is hard to understand.
- Excalidraw Diagrams and Japanese Native Writing end a reply that reports how
  something currently works across several tables, screens, or systems with
  one offer, such as "Excalidraw の図にして、ブラウザで開けるページで図解しますか？".
  On a yes, the diagrams go one per heading on a local HTML page served and
  opened in the browser, instead of being drawn unasked or left for the user
  to request.
- Japanese Native Writing, Japanese Doc Writing, Japanese PR Writing, and
  Japanese Code Comment Writing add "「列を足す」ではなく「カラムを追加する」"
  to the established katakana term examples, with a note that 足す is for
  numbers and quantities, so a column, field, or element being added is
  追加する.

## [0.14.0] - 2026-11-17

### Added

- Japanese Doc Review reviews a finished Japanese document through a reader
  without the session's context. The reader first says what each image shows
  on its own, then what the page is for, and where words, references, or
  repeated content tripped them. Findings come back as a table of location,
  what happens to the reader, and replacement text, covering headings,
  wording, sentence links, image placement, and references.
- Focused Screen Captures captures a real screen under a fixed viewport, hides
  developer overlays, dims everything except the target, outlines it with
  `scripts/focus-overlay.js`, and places the image after a one-sentence lead
  wherever text points to a place on a screen.

### Changed

- Japanese Doc Writing names headings by their content, carries the opening
  fact through to why the page is needed, shows contents instead of bare
  counts, links cause-and-effect sentences and splits sentences with three or
  more clauses, turns parallel scenes into lists, leads every image with one
  sentence, and puts a focused screen capture before text that points to a
  place on a screen. Tickets are sized so one outcome can be judged done, work
  shared with sibling tickets appears in both, and open questions say who
  decides and how the work proceeds until then. Shared documents finish with
  Japanese Doc Review.
- Excalidraw Diagrams labels with the team's names and the reader's outcome,
  checks whether elements are parallel or sequential before drawing arrows,
  shows states as short-tailed callouts, and keeps labels in the same position
  the same shape across before-and-after diagrams.
- Japanese Native Writing includes how the work proceeds after each choice
  when it asks the user to decide.

## [0.13.2] - 2026-11-17

### Changed

- Japanese Doc Writing chooses the shape by the weight of the problem: a
  ticket with one problem that fits a diagram uses a thin shape (opening,
  problem with a diagram and two or three facts, what to do, a short note,
  appendix), and recommendation and decision sections appear only when the
  reader has something to decide. Tickets for a first-time assignee lead with
  the conclusion and then the reason.
- Japanese Doc Writing keeps approved text unchanged when posting it
  elsewhere unless the difference is confirmed first, leaves what a diagram
  already shows out of the text, and marks a temporary assumption with a point
  in time and a one-line note that links the follow-up task.

## [0.13.1] - 2026-11-17

### Changed

- Japanese Doc Writing leaves incidental work, such as writing tests, out of
  task lists unless adding tests is the goal of the task, so the list shows
  what each task newly adds.

## [0.13.0] - 2026-11-16

### Added

- Excalidraw Diagrams skill for diagrams in documents, tickets, pull requests,
  and inline comments: choose one of four patterns (scenario, problem shown as
  a working and a failing scene, timeline, mechanism with fallback lanes),
  label boxes with names the reader knows and the same words as the body, keep
  colors per role, generate the scene from a Python script, render it to PNG,
  and check it on the page after placing it.

### Changed

- Japanese Doc Writing and Japanese PR Writing draw flows, problems over time,
  failure fallbacks, and before-and-after differences as diagrams with
  Excalidraw Diagrams, and keep text flow diagrams for places that cannot
  show images.

## [0.12.2] - 2026-11-16

### Changed

- Japanese Doc Writing puts the problem statement before the recommendation in
  documents that ask for review, and leaves out decisions where neither option
  has a clear advantage, so the writer decides and states the reason instead.
  Diagrams carry only the flow, structure, and short labels, with explanations
  in the body, and their text follows the same wording rules as the body. The
  body no longer repeats what a diagram or another section already shows.
  Before editing a shared document, the writer presents the copy and where it
  goes for confirmation.

## [0.12.1] - 2026-11-16

### Changed

- Japanese Doc Writing now asks for wording a new team member can read without
  context: meeting shorthand is spelled out, while domain terms and identifiers
  stay as they are. Background is stated as what the feature does, the author
  refers to themselves without their own name, unverified scope names the
  information that was not checked instead of the reason or a guess at where
  it is, and conclusions any reader can infer from the previous sentence are
  left out. The final review also checks that rewording did not drop people,
  organizations, or dates from the source.

## [0.12.0] - 2026-11-13

### Added

- Japanese Doc Writing skill for Japanese documents such as design notes,
  investigation reports, and migration plans: the opening states what the page
  is for, the recommendation, and up to three decisions; the body fits one
  screen; details move to an appendix.
- Japanese Code Comment Writing skill for Japanese code comments and test
  descriptions: background before behavior, identifiers and technical verbs
  instead of everyday wording, and no ticket numbers in place of reasons.
- Japanese PR Writing adds guidance on what to include so a reviewer
  understands the change within ten seconds, body patterns, verification
  captures, review replies, and a rule to present the full title and body for
  confirmation before a pull request is created or edited.
- A maintainer procedure for tuning the Japanese writing skills from the
  owner's edits to AI-written copy (`docs/skill-tuning.md`).

### Changed

- Japanese Native Writing now covers chat replies only and is rewritten around
  a ten-second standard: conclusion first, two or three points, engineering
  terms left as engineers say them, and decisions asked once. The five status
  labels and parenthetical term glosses are removed. Documents move to Japanese
  Doc Writing.
- Japanese PR Writing follows the author's recent pull requests or the
  repository template for section order instead of a fixed order, and uses the
  words engineers use in conversation instead of plain rewording.

### Removed

- Japanese PR Writing no longer delegates drafts to Codex `gpt-6.1-terra`. The
  model that reads the skill writes the copy itself.

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

[Unreleased]: https://github.com/axshia/aburasashi/compare/v0.14.3...HEAD
[0.14.3]: https://github.com/axshia/aburasashi/compare/v0.14.2...v0.14.3
[0.14.2]: https://github.com/axshia/aburasashi/compare/v0.14.1...v0.14.2
[0.14.1]: https://github.com/axshia/aburasashi/compare/v0.14.0...v0.14.1
[0.14.0]: https://github.com/axshia/aburasashi/compare/v0.13.2...v0.14.0
[0.13.2]: https://github.com/axshia/aburasashi/compare/v0.13.1...v0.13.2
[0.13.1]: https://github.com/axshia/aburasashi/compare/v0.13.0...v0.13.1
[0.13.0]: https://github.com/axshia/aburasashi/compare/v0.12.2...v0.13.0
[0.12.2]: https://github.com/axshia/aburasashi/compare/v0.12.1...v0.12.2
[0.12.1]: https://github.com/axshia/aburasashi/compare/v0.12.0...v0.12.1
[0.12.0]: https://github.com/axshia/aburasashi/compare/v0.11.0...v0.12.0
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
