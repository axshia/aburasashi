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
  Japanese pull request copy while preserving technical meaning, validation
  status, and Markdown structure.
- [Japanese Native Writing](japanese-native-writing/README.md) writes clear,
  native Japanese replies and documents: conclusion first, explicit done,
  unverified, not-done, unknown, and missing status, options with trade-offs,
  and sparse formatting.
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
