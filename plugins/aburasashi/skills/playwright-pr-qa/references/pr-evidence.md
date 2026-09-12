# Pull request approval and evidence

Use the pull request's established language while preserving every field below.
All comments are append-only. Hidden markers make the ledger discoverable
without changing the visible content.

## Approval request

Ask before launching Playwright or writing the plan comment:

```markdown
Draft PR {{PR}}（head: `{{SHA}}`）について、自動QAを実行してよいですか？

- 対象環境: {{DEVELOPMENT_OR_PREVIEW_ENVIRONMENT}}
- テストユーザー: {{PUBLIC_PERSONA_LABELS}}
- ブラウザ: {{ACTUAL_PROJECTS}}
- 画面: desktop / mobile
- 確認フロー: {{SHORT_ORDERED_FLOW}}
- 副作用: {{CREATED_DATA_NOTIFICATIONS_OR_NONE}}

QA結果は成功・失敗・再試行を含め、ユーザー名と実ブラウザ名を右上に表示したキャプチャとともに、このPRのコメントへ掲載します。実行・掲載してよい場合は明示的に承諾してください。
```

Record the approval message URL or session reference and timestamp. If the
owner changes the environment, personas, matrix, or side effects, update the
proposed plan before treating the response as approval.

## Frozen plan comment

Post this only after approval and before `QA-01` starts:

```markdown
<!-- playwright-pr-qa:plan run={{RUN_ID}} revision=1 -->
## Automated QA plan — `{{RUN_ID}}`

- Draft PR: {{PR_URL}}
- Approved by: {{OWNER_AND_APPROVAL_REFERENCE}}
- Head SHA: `{{SHA}}`
- Environment: {{ENVIRONMENT}}
- Browser projects: {{PROJECTS}}
- Surfaces: desktop / mobile

### Completion conditions in flow order

- [ ] `QA-01` — {{CONDITION}}
  - Actors / starting state: {{ACTORS_AND_STATE}}
  - Operations: {{ORDERED_ACTIONS}}
  - Expected: {{OBSERVABLE_EXPECTATION}}
  - Captures: {{ACTOR_AND_MOMENT_PER_SURFACE}}
- [ ] `QA-02` — {{CONDITION}}
  - Actors / starting state: {{ACTORS_AND_STATE}}
  - Operations: {{ORDERED_ACTIONS}}
  - Expected: {{OBSERVABLE_EXPECTATION}}
  - Captures: {{ACTOR_AND_MOMENT_PER_SURFACE}}

### Data and cleanup

{{RUN_NAMESPACE_SIDE_EFFECTS_AND_CLEANUP}}
```

Do not edit this comment to check boxes or add newly discovered scope. Append a
`revision=2` plan comment describing the delta and approval when revision is
required.

## Checkpoint result comment

Post exactly one new comment for each checkpoint attempt. Publish FAIL before
trying a workaround or fix.

```markdown
<!-- playwright-pr-qa:result run={{RUN_ID}} checkpoint={{QA_ID}} attempt={{N}} status={{PASS_OR_FAIL}} sha={{SHA}} -->
## `{{QA_ID}}` attempt {{N}} — {{PASS_OR_FAIL}}

- Verified: {{COMPLETION_CONDITION}}
- Head SHA / environment: `{{SHA}}` / {{ENVIRONMENT}}
- Actors and starting state: {{ACTORS_AND_STATE}}
- Browser projects: {{PROJECTS}}

### Operations

1. {{ACTION_1}}
2. {{ACTION_2}}

### Expected / observed

- Expected: {{EXPECTED}}
- Observed: {{OBSERVED}}
- Assertion: {{ASSERTION_RESULT}}

### Evidence

| Persona | Browser / project | Desktop | Mobile |
| --- | --- | --- | --- |
| {{PERSONA}} | {{BROWSER}} | {{DESKTOP_ATTACHMENT}} | {{MOBILE_ATTACHMENT}} |

### Side effects and next action

- Created or changed data: {{DATA}}
- Cleanup: {{CLEANUP_STATUS}}
- Next: {{NEXT_CHECKPOINT_OR_ESCALATION}}
```

Add rows for every persona and browser required by the frozen plan. Each image
must have meaningful alt text and its own visible evidence badge. If one planned
surface fails, the whole checkpoint attempt is FAIL even if another surface
passes.

## Failure escalation to the invoking session

After the FAIL comment is visible, stop dependent actions and report:

```markdown
`{{QA_ID}}` attempt {{N}} failed on `{{SHA}}`.

- Expected: {{EXPECTED}}
- Observed: {{OBSERVED}}
- Shortest reproduction: {{STEPS}}
- Affected persona/browser/surface: {{MATRIX_CELL}}
- Evidence: {{RESULT_COMMENT_URLS_AND_DIAGNOSTICS}}
- Current hypothesis: {{PRODUCT_QA_DATA_ENVIRONMENT_OR_EXPECTATION}}
- State preserved for retry: {{YES_NO_AND_DETAILS}}

No product fix has been made under the QA approval. Please decide the cause and whether a product, QA, data, environment, or expectation change is authorized.
```

After a fix or decision, append a new attempt comment. Link it to the prior FAIL
comment; never replace the failed evidence.

## Completion comment

Post only after reconciling the full ledger:

```markdown
<!-- playwright-pr-qa:complete run={{RUN_ID}} sha={{FINAL_SHA}} -->
## Automated QA complete — `{{RUN_ID}}`

- Final head SHA: `{{FINAL_SHA}}`
- Environment: {{ENVIRONMENT}}
- Coverage: {{BROWSERS_AND_SURFACES}}

### Completion conditions

- [x] `QA-01` — PASS on attempt {{N}}: {{RESULT_COMMENT_URL}}
- [x] `QA-02` — PASS on attempt {{N}}: {{RESULT_COMMENT_URL}}

### Retry and head-change record

{{FAILURE_RETRY_LINKS_AND_IMPACT_ASSESSMENT_OR_NONE}}

All frozen conditions passed and every planned desktop/mobile capture was reopened and verified on this pull request.
```

Never write `complete` while a condition is missing, its latest applicable
attempt is FAIL, an attachment does not render, or a head change lacks an impact
assessment.

## Upload screenshots without committing them

Store PR-only images in a temporary or ignored location. Inspect each image
before upload. Read the shared
[GitHub attachment workflow](../../../references/github-attachments.md) for
version, host, credential, file-type, and size checks. Prefer native `gh`
2.99.0+ when those checks pass; publication remains covered by the QA approval.

Write the complete checkpoint result to `qa-result.md`, including its run,
checkpoint, attempt, and status marker. Replace the evidence template fields
with local Markdown image references, for example:

```markdown
| Persona | Browser / project | Desktop | Mobile |
| --- | --- | --- | --- |
| requester | chromium | ![Requester desktop at QA-01, attempt 1](./qa-01-requester-desktop.png) | ![Requester mobile at QA-01, attempt 1](./qa-01-requester-mobile.png) |
```

Run from the directory containing those images, specifying the target PR and
repository. Attach every required persona/browser/surface file once:

```bash
gh pr comment 123 --repo OWNER/REPO --body-file qa-result.md \
  --attach ./qa-01-requester-desktop.png \
  --attach ./qa-01-requester-mobile.png
```

`gh` rewrites the image destinations to uploaded URLs in their table cells.
Do not use `--edit-last` or `--delete-last` for this append-only ledger. If a
single checkpoint requires more than 50 images, obtain their URLs through the
shared browser staging workflow and publish one complete result body.

### Repair incomplete evidence

A non-zero exit can still leave a posted result with only some images. Before
retrying, inspect the returned comment URL and locate the run/checkpoint/attempt
marker in the PR comments. If a result exists, keep it and its successful URLs;
do not post the same result again or overwrite it.

Append an evidence-repair comment linking the original result, identifying the
same run/checkpoint/attempt and the missing evidence, and attaching only those
files. Make clear that the original result is incomplete until all repaired
images render, even if its text says PASS. Repairing an upload does not itself
rerun QA or increment the attempt number. If there is no posted result, recover
any successful asset URLs and publish the intended result after fixing the
upload problem.

After publication, read back the saved Markdown and reopen the exact comment
to verify every image under the correct checkpoint and attempt. The completion
ledger must link any repair comments alongside the original result. A local
path, printed comment URL, or editor preview is not verified published evidence.
