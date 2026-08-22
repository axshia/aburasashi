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
before upload.

Prefer the signed-in Chrome session with the `chrome-devtools` MCP for GitHub
attachment upload when available. Paste each image into the intended pull
request comment editor and wait until the editor contains its final
`https://github.com/user-attachments/assets/...` URL. The event-dispatch return
value is not proof of success.

When an image exists only as bytes in memory, create a browser `File`, place it
in a `DataTransfer`, and deliver it with a paste event without logging the
Base64 or credentials. If a separate editor is used only as an upload staging
area, transfer the final URLs to the intended result comment and discard the
staging draft instead of posting an upload-only comment.

After submitting, reopen the pull request and verify every image renders under
the correct checkpoint and attempt. A local screenshot path or an editor-only
preview is not published evidence.
