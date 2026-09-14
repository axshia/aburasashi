---
name: using-aburasashi
description: Use when starting any conversation and before every response or action, including clarifying questions, code exploration, and precondition checks. Establishes the 1% rule for invoking aburasashi skills.
---

# Using Aburasashi

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, ignore this skill.
</SUBAGENT-STOP>

<EXTREMELY-IMPORTANT>
If there is even a 1% chance that an aburasashi skill applies to what you are doing, you MUST invoke that skill.

If a skill applies, you do not have a choice. Invoke it. This is not negotiable, and you cannot rationalize your way out of it.
</EXTREMELY-IMPORTANT>

## The Rule

**Invoke the skill BEFORE any response or action**: before clarifying questions, before exploring the codebase, and before checking whether the skill's inputs exist.

Then announce "Using aburasashi:<skill> to <purpose>" and follow the skill exactly. If the skill turns out to be wrong for the situation, it tells you how to stop; you do not have to finish it.

## Preconditions are checked inside the skill, not before it

Several aburasashi descriptions say "use only when Figma data is available" or "require both images". Those sentences describe the entry check the skill performs after it starts. They are not permission to postpone the invocation until you have confirmed the inputs yourself.

Invoke first. The skill then verifies its inputs and tells you what to ask for when something is missing.

## Trigger cues

| Cue in the request or context | Invoke |
| --- | --- |
| A pull request title, body, review reply, or validation report in Japanese; reviewers who read Japanese | `japanese-pr-writing` |
| An OpenAPI file changed and a pull request is being prepared; reviewers need to see API changes | `openapi-redoc-pr-screenshots` |
| A Draft pull request needs browser QA; multi-user or multi-state web flows; desktop and mobile evidence | `playwright-pr-qa` |
| A web screen should match a design; "the design", "the mockup", a Figma link or node | `figma-web-parity` |
| An iOS screen should match a design; SwiftUI, UIKit, or the iOS Simulator with a design reference | `figma-ios-simulator-parity` |
| A website or landing-page mockup; a brand image plus a wireframe image; visual design exploration | `web-design-from-references` |

A cue that might refer to one of these is enough. "The design" might be a Figma frame. "Make the PR easy to review" might mean Japanese copy or API screenshots.

## Red Flags

These thoughts mean STOP. You are rationalizing.

| Thought | Reality |
| --- | --- |
| "The description says use only when X is available, and I don't know whether X exists" | Invoke. The skill checks X. |
| "I'll locate the Figma node first, then invoke" | Invoke first. The skill tells you how to locate it. |
| "I'll invoke it once it is clearly needed" | By then you have already done the work the skill shapes. |
| "This is a small change" | Small changes drift from designs and templates too. Invoke. |
| "I can write the PR body myself" | That is what the skill is for. Invoke. |
| "The user did not name the skill" | Skills trigger on the task, not on their name. |
| "I remember what that skill says" | Skills change. Read the current version. |

## User Instructions

User instructions (CLAUDE.md, AGENTS.md, direct requests) take precedence over skills, and skills override default behavior. Skip a skill only when the user has explicitly told you to.
