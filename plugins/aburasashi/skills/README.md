# Skills

Each distributable skill lives in its own kebab-case directory and has a
`SKILL.md` entrypoint:

```text
skills/
├── using-aburasashi/
│   ├── SKILL.md
│   ├── README.md
│   └── agents/
├── logical-thinking/
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/
│   └── references/
├── japanese-pr-writing/
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/
│   └── references/
├── japanese-native-writing/
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/
│   └── references/
├── japanese-doc-writing/
│   ├── SKILL.md
│   ├── README.md
│   └── agents/
├── japanese-doc-review/
│   ├── SKILL.md
│   ├── README.md
│   └── agents/
├── japanese-code-comment-writing/
│   ├── SKILL.md
│   ├── README.md
│   └── agents/
├── japanese-article-writing/
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/
│   └── references/
├── excalidraw-diagrams/
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/
│   ├── assets/
│   ├── references/
│   └── scripts/
├── focused-screen-captures/
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/
│   └── scripts/
├── web-design-from-references/
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/
│   └── references/
├── figma-ios-simulator-parity/
│   ├── SKILL.md
│   ├── README.md
│   └── references/
├── figma-web-parity/
│   ├── SKILL.md
│   ├── README.md
│   └── references/
├── openapi-redoc-pr-screenshots/
│   ├── SKILL.md
│   ├── README.md
│   ├── scripts/
│   ├── references/
│   └── assets/
├── playwright-e2e-recording/
│   ├── SKILL.md
│   ├── agents/
│   ├── scripts/
│   ├── references/
│   └── assets/
└── playwright-pr-qa/
    ├── SKILL.md
    ├── README.md
    └── references/
```

## Available skills

- [Using Aburasashi](using-aburasashi/README.md) is the bootstrap skill that
  establishes the 1% trigger rule: invoke a skill before responding whenever
  there is even a 1% chance it applies, and let the skill check its own inputs.
- [Logical Thinking](logical-thinking/README.md) applies to specification or
  requirements formulation, UI/UX design, and marketing thinking, even a small
  part of another task. It also evaluates questionable results, compares approaches,
  and explains decisions without expanding the requested scope.
- [Japanese PR Writing](japanese-pr-writing/README.md) drafts and improves
  Japanese pull request titles, descriptions, inline comments, and review
  replies so a reviewer understands what changed within ten seconds, while
  preserving technical meaning, validation status, and Markdown structure. It
  presents the full copy for confirmation before a pull request is created or
  edited.
- [Japanese Native Writing](japanese-native-writing/README.md) writes Japanese
  replies the user understands within ten seconds: conclusion first, two or
  three points, unverified and not-done work stated as plainly as the
  conclusion, engineering terms left as engineers say them, and decisions asked
  once with the recommendation first.
- [Japanese Doc Writing](japanese-doc-writing/README.md) writes Japanese
  documents whose first lines say what the page is for and what the reader must
  decide: context, recommendation, and up to three decisions first, a body that
  fits one screen, and details moved to an appendix.
- [Japanese Doc Review](japanese-doc-review/README.md) reviews a finished
  Japanese document through a reader without the session's context: whether
  each image is understood on its own, whether the purpose and the work are
  clear from the opening, and where headings, wording, sentence links, image
  placement, or references trip a first-time reader. It returns located
  findings with replacement text and does not rewrite unless asked.
- [Japanese Code Comment Writing](japanese-code-comment-writing/README.md)
  writes Japanese code comments and test descriptions for an engineer who lacks
  the author's context: background before behavior, identifiers and technical
  verbs instead of everyday wording, and no ticket numbers in place of reasons.
- [Japanese Article Writing](japanese-article-writing/README.md) writes
  Japanese articles for outside readers, such as tech blog posts, how-to,
  explainer, and comparison articles, and release announcements: an opening
  chosen by article type that reaches the point before the first heading,
  paragraphs that open with their point, pacing and a calm, friendly voice,
  comparison tables with consistent conditions and status labels, first-hand
  facts at the center, and rewrites of common AI-sounding patterns. When first-hand facts
  are missing, it asks for them or marks where they belong instead of padding.
- [Excalidraw Diagrams](excalidraw-diagrams/README.md) draws diagrams for
  documents, tickets, pull requests, and inline comments as Excalidraw scenes,
  renders them to PNG, and checks them on the page.
- [Focused Screen Captures](focused-screen-captures/README.md) captures a real
  screen under fixed viewport conditions, dims everything except the target,
  outlines it, and places the image after a one-sentence lead wherever text
  points to a place on a screen.
- [Web Design from References](web-design-from-references/README.md) creates
  website section mockups from a brand-concept image and a readable content
  wireframe, with no image output when either required input is missing.
- [Figma iOS Simulator Parity](figma-ios-simulator-parity/README.md) verifies
  and corrects a SwiftUI or UIKit screen against an exact Figma node on a pinned
  iOS Simulator configuration.
- [Figma Web Parity](figma-web-parity/README.md) verifies and corrects a web
  implementation against an exact, accessible Figma node with normalized
  screenshots and root-cause-driven visual diffs.
- [OpenAPI ReDoc PR Screenshots](openapi-redoc-pr-screenshots/README.md) creates
  annotated, per-endpoint ReDoc comparisons for GitHub pull requests.
- [Playwright PR QA](playwright-pr-qa/README.md) runs approved multi-user and
  multi-state browser QA with labeled desktop/mobile evidence and append-only PR
  checkpoint comments.
- [Playwright E2E Recording](playwright-e2e-recording/SKILL.md) creates and runs
  instant Playwright scenarios, records successful and failed attempts, and
  hands video, screenshots, and a result manifest to PR creation workflows.
