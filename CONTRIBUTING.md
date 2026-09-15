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

Add a row for the new skill to the trigger-cue table in
`plugins/aburasashi/skills/using-aburasashi/SKILL.md`. That bootstrap skill is
injected into every Claude Code session, so keep the row to one line of
concrete cues and do not summarize the skill's workflow there.

## Trigger rule

Skills trigger under a 1% rule: the agent invokes a skill before responding
whenever there is even a 1% chance it applies. Write descriptions so the
triggering situations are easy to recognize. Precondition sentences such as
"use only when Figma data is available" are allowed, but the skill body must
then perform that check itself and say what to ask for when an input is
missing, because the agent invokes the skill before confirming inputs.

## Compatibility rules

- Write provider-neutral instructions by default so the same `SKILL.md` works
  in Claude Code and Codex.
- Do not set `disable-model-invocation: true`; OpenAI skills must remain
  available for model invocation.
- Name exact products only when the workflow genuinely depends on them.
- Do not reference files outside the plugin directory. Marketplace installers
  copy plugins into isolated caches.
- Keep `plugins/aburasashi/hooks/session-start` and `run-hook.cmd` executable
  and free of external dependencies; the Codex manifest must keep `"hooks": {}`
  so Codex does not try to run the Claude Code hook.
- Never include credentials, local absolute paths, private URLs, or personal
  data in a skill or fixture.
- Document network access, destructive actions, and required user approvals.

## Validate a change

```bash
make validate
make validate-claude  # when Claude Code CLI is available
```

For changes to the E2E recording helper, run its local browser integration checks:

```bash
uv run --with playwright==1.62.0 python scripts/test-recorded-e2e.py
```

They use a local HTTP fixture and isolated Chrome contexts to check successful
recordings, closed popups, failures, blockers, and incomplete scenarios. Chrome
and Playwright's video encoder are required; FFmpeg enables the MP4 checks.

Before publishing a version, update both plugin manifests to the same semantic
version, update `CHANGELOG.md`, and run:

```bash
make validate-release
```

See [docs/publishing.md](docs/publishing.md) for the complete release checklist.
