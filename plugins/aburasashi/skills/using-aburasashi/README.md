# Using Aburasashi

[Skill catalog](../README.md)

Bootstrap skill that establishes the trigger rule for every other aburasashi
skill: if there is even a 1% chance a skill applies, the agent invokes it
before responding, exploring the codebase, or checking the skill's inputs.

Skill descriptions such as "use only when Figma data is available" describe the
entry check the skill performs after it starts. They are not a reason to delay
the invocation. The skill verifies its inputs and asks for what is missing.

## How it loads

- **Claude Code**: `hooks/hooks.json` runs `hooks/session-start` at session
  start, after `/clear`, and after compaction. The script injects this
  `SKILL.md` into the session context, so no per-session action is needed.
- **Codex**: skills are surfaced natively from their descriptions. This skill's
  description asks the model to load it at the start of every conversation.
  The Codex manifest declares an empty `hooks` object so Codex does not try to
  run the Claude Code hook.

## Usage

The skill needs no arguments. To confirm it is active, start a new session and
ask which aburasashi skills would apply to a borderline request such as
"make this PR easy to review". The agent should name the matching skill and
invoke it before doing anything else.

```text
/aburasashi:using-aburasashi
```

## Scope

- Applies to: every aburasashi skill listed in the trigger table of
  [SKILL.md](SKILL.md).
- Does not apply to: subagents dispatched to execute a specific task, or
  cases where the user has explicitly told the agent to skip a skill.
- User instructions in CLAUDE.md, AGENTS.md, or the request itself take
  precedence over this rule.
