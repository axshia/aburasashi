---
name: playwright-pr-qa
description: Run and publish owner-approved Playwright QA for a Draft GitHub pull request when multi-user or multi-state web flows need repeatable desktop and mobile evidence. Use to isolate actor sessions, execute ordered checkpoints, capture labeled screenshots, append pass, fail, and retry comments, and resume after authorized fixes until every planned condition passes.
---

# Playwright PR QA

Turn a Draft pull request's acceptance criteria into an append-only, reviewable
QA record. Adapt the automation to the target repository; do not impose a new
test structure when the project already has Playwright conventions.

Read [references/playwright-patterns.md](references/playwright-patterns.md)
before creating or adapting the browser automation. Read
[references/pr-evidence.md](references/pr-evidence.md) before requesting
approval or writing any pull request comment.

## Invariants

- Require an existing Draft pull request and explicit owner approval for both
  running the automated QA and publishing every success, failure, retry, test
  identity, and screenshot to that pull request.
- Treat QA approval as permission to execute and publish the disclosed checks.
  It does not authorize product-code fixes, production use, new destructive
  effects, or broader repository changes.
- Bind the run to the exact pull request head SHA and named development or
  preview environment. Never silently test a different checkout or deployment.
- Keep the initial plan, PASS results, FAIL results, and retries as append-only
  comments. Never erase or overwrite an earlier outcome.
- Do not declare completion until every frozen completion condition has a PASS
  result and all required evidence renders on the pull request.

## Workflow

### 1. Preflight without running QA

Confirm that implementation is complete and the pull request is still Draft.
Resolve the pull request number, head SHA, target environment, acceptance
criteria, supported browser matrix, test personas, starting states, and any
external side effects. Inspect the repository's existing Playwright version,
configuration, fixtures, authentication helpers, and artifact rules.

Draft ordered checkpoints from the ticket, design, pull request, and current
implementation. Give each checkpoint a stable ID such as `QA-01`. For every
checkpoint define:

- actors and starting state;
- exact operations in execution order;
- observable expected result;
- capture points for each actor involved;
- desktop and mobile browser projects; and
- cleanup or intentionally retained test data.

Default to both desktop and mobile evidence. A surface may be omitted only when
it is genuinely out of scope and the omission is disclosed before approval.
Do not launch Playwright or write to the pull request during this step.

### 2. Obtain the owner approval gate

Ask the owner whether the proposed automated QA may run and state that all
PASS, FAIL, and retry results will be posted as pull request comments with
labeled desktop and mobile screenshots. Include the Draft pull request,
environment, head SHA, persona labels, browser projects, and material side
effects in the request.

Proceed only after an affirmative approval covering that publication. Record
where and when approval was given. Narrow approval narrows the plan; silence or
an ambiguous response is not approval.

### 3. Publish and freeze the ordered plan

After approval, post one plan comment before executing the first checkpoint.
List completion conditions in actual flow order, including prerequisites,
actions, expected results, capture points, actors, browsers, and surfaces. Add a
run ID, approval reference, environment, and head SHA.

Treat this comment as the frozen baseline. If a new condition or wider side
effect becomes necessary, stop and append a clearly versioned plan revision.
Obtain renewed approval when the revision broadens the approved scope.

### 4. Execute isolated Playwright sessions

Use one fresh `BrowserContext` for every combination of test persona, browser
project, surface, and attempt. Do not represent different users with pages that
share one context. Namespace generated records with the run ID so concurrent
or retried QA cannot consume another run's state.

For multi-user flows, choreograph the actors in one explicit sequence. Assert
the prerequisite before each action and wait on observable UI, network, or
persisted state rather than arbitrary sleeps. Recreate the required starting
state before a retry.

At each planned capture point, take separate desktop and mobile screenshots.
Every image must show a legible top-right evidence label containing at least:

```text
user: <public test identity> | browser: <actual engine/project> | surface: <desktop|mobile> | checkpoint: <QA-ID> | attempt: <N>
```

Use only non-sensitive test identities in labels. Inspect screenshots for
secrets, personal information, unrelated tabs, clipping, hidden expected
state, and misleading browser names before upload.

### 5. Append one result comment per checkpoint attempt

Immediately after a checkpoint attempt, publish a new result comment. State
what was verified, the ordered operations, the expected result, the observed
result, the assertion outcome, head SHA, environment, actors, browser projects,
and attempt number. Attach every applicable desktop and mobile capture.

Use `PASS` only when all planned assertions and captures for that checkpoint
have succeeded. Otherwise use `FAIL`; missing or non-rendering evidence keeps
the checkpoint incomplete. A sequence with several checkpoints gets several
result comments, not one combined summary.

### 6. Stop, escalate, fix, and resume on failure

On failure, preserve the failing UI before cleanup, publish the FAIL comment,
and stop downstream actions that depend on it. Return to the invoking or main
session with the expected and observed behavior, shortest reproduction,
screenshots, console or network evidence when relevant, current head SHA, and a
classification hypothesis. Ask that session to decide whether the defect is in
the product, QA code, data, environment, or expectation.

Do not infer repair permission from QA approval. After the responsible session
authorizes or supplies a fix, resolve the new head SHA, assess whether earlier
PASS checkpoints were affected, restore the failed checkpoint's prerequisites,
and resume from that checkpoint. Increment the attempt number and append a new
result comment even when the retry succeeds. Rerun an earlier checkpoint only
when the fix or state reset invalidated its prior result, and record why.

Repeat this failure-decision-fix-retry loop until every frozen condition passes.
If approval is withdrawn, the environment cannot safely reproduce the flow, or
progress requires an undisclosed destructive or production action, stop without
claiming completion and report the exact blocker.

### 7. Publish completion

Re-read the plan and result comments. Post the completion comment only when the
ledger contains a valid PASS for every checkpoint, every planned desktop and
mobile attachment renders, no failure remains unresolved, and any head changes
have an explicit impact assessment.

The completion comment must include the final run ID, current head SHA,
environment, ordered checklist, successful attempt for each checkpoint, browser
and surface coverage, and links to the result comments. State any pre-approved
out-of-scope surface; do not hide it as completed coverage.

## Artifact handling

Keep pull-request-only captures outside the repository or in an already ignored
temporary directory. Do not commit them. Prefer native `gh` 2.99.0+
`gh pr comment --body-file ... --attach ...` for approved evidence publication.
Follow [references/pr-evidence.md](references/pr-evidence.md#upload-screenshots-without-committing-them)
for local Markdown references, the shared support checks and browser fallback,
and append-only recovery after partial uploads. Read back the saved comment and
reopen it to confirm every planned image renders under the correct attempt.
