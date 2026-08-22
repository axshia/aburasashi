# Skills

Each distributable skill lives in its own kebab-case directory and has a
`SKILL.md` entrypoint:

```text
skills/
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

- [OpenAPI ReDoc PR Screenshots](openapi-redoc-pr-screenshots/README.md) creates
  annotated, per-endpoint ReDoc comparisons for GitHub pull requests.
- [Playwright PR QA](playwright-pr-qa/README.md) runs approved multi-user and
  multi-state browser QA with labeled desktop/mobile evidence and append-only PR
  checkpoint comments.
