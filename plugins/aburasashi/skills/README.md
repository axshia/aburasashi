# Skills

Each distributable skill lives in its own kebab-case directory and has a
`SKILL.md` entrypoint:

```text
skills/
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
