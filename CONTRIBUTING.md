# Contributing

## Add a skill

Create one kebab-case directory per skill under `plugins/aburasashi/skills/`.
Every skill must have a `SKILL.md` with at least `name` and `description` in
YAML frontmatter.

```markdown
---
name: example-skill
description: Explain what the skill does and when the model should use it.
---

# Example skill

Write the workflow as direct, testable instructions.
```

The directory name and frontmatter `name` must match. Put optional executable
helpers, detailed documentation, and reusable files in `scripts/`,
`references/`, and `assets/` inside that skill directory.

## Compatibility rules

- Write provider-neutral instructions by default so the same `SKILL.md` works
  in Claude Code and Codex.
- Do not set `disable-model-invocation: true`; OpenAI skills must remain
  available for model invocation.
- Name exact products only when the workflow genuinely depends on them.
- Do not reference files outside the plugin directory. Marketplace installers
  copy plugins into isolated caches.
- Never include credentials, local absolute paths, private URLs, or personal
  data in a skill or fixture.
- Document network access, destructive actions, and required user approvals.

## Validate a change

```bash
make validate
make validate-claude  # when Claude Code CLI is available
```

Before publishing a version, update both plugin manifests to the same semantic
version, update `CHANGELOG.md`, and run:

```bash
make validate-release
```

See [docs/publishing.md](docs/publishing.md) for the complete release checklist.
