# Skills

Each distributable skill lives in its own kebab-case directory and has a
`SKILL.md` entrypoint:

```text
skills/
└── example-skill/
    ├── SKILL.md
    ├── scripts/      # optional
    ├── references/   # optional
    └── assets/       # optional
```

This directory intentionally contains no distributable skill during the
initial project bootstrap. `make validate-release` will fail until the first
real skill is added.
