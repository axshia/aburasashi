# Playwright PR QA

[Back to aburasashi](../../../../README.md)

Run repeatable, evidence-backed web QA for a Draft GitHub pull request when
several users, states, browsers, or form factors make manual verification slow.

## What it does

- Requires explicit owner approval before QA execution or PR publication.
- Freezes ordered completion conditions in a plan comment.
- Uses isolated Playwright browser contexts for every test persona.
- Captures separate desktop and mobile evidence with a top-right identity and
  browser label.
- Posts one append-only PASS or FAIL comment for every checkpoint attempt.
- Publishes images with native `gh` 2.99.0+ `--attach`, with a browser fallback
  when the CLI cannot upload the requested evidence.
- Stops on failure, returns diagnosis evidence to the invoking session, and
  resumes at the failed checkpoint after an authorized fix.
- Publishes a final completion comment only when every frozen condition passes.

## Evidence flow

```text
Draft PR
  -> owner approval
  -> frozen QA plan comment
  -> checkpoint result comments
  -> failure decision and retry, when needed
  -> completed ledger comment
```

The QA approval covers the disclosed execution and publication. It does not by
itself authorize product-code fixes, production actions, or newly discovered
destructive side effects.

## Invoke it

```text
Use $playwright-pr-qa to verify this Draft PR with requester and responder test
users on desktop and mobile, and publish the evidence to the PR.
```

The skill adapts to the target repository's existing Playwright configuration,
fixtures, browser support policy, and PR language. It does not require PR-only
screenshots to be committed to the target repository.

See [PR evidence](references/pr-evidence.md#upload-screenshots-without-committing-them)
for `--body-file` / `--attach` examples and append-only evidence repairs, and
the shared [attachment workflow](../../references/github-attachments.md) for
supported hosts, credentials, media types, and upload verification.
