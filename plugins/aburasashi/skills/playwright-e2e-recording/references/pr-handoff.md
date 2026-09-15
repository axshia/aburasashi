# Hand recorded E2E evidence to a PR workflow

The interface is files, so it works with an installed PR creation skill, an
invoking agent, or an existing Playwright suite. It does not assume a particular
provider, named PR creation plugin, existing PR, or permission to publish.

## Producer: recording workflow

Return the run directory and these files:

| File | Contract |
| --- | --- |
| `result.json` | Versioned result and artifact manifest described below |
| `pr-evidence.md` | Local Markdown section, using paths relative to the run directory |
| `scenario.py` | Exact scenario executed by the helper |
| `page-NN.webm` / optional `.mp4` | One recording per page, including popups |
| `<checkpoint>-<status>.png` | Assertion/failure screenshots |
| Optional `trace.zip` | Local debugging trace; not a media attachment |

`result.json` schema version 1 contains:

- `run_id`, `scenario`, `status` (`PASS`, `FAIL`, `BLOCKED`), UTC start/end times.
- `target.url` and `target.deployment_revision` (null until established).
- `workspace.head` and `workspace.dirty`: checkout metadata, not deployment proof.
- Actual `browser` engine/channel/version/headless/viewport, `persona`, `surface`.
- Ordered `checkpoints`: `id`, `expected`, `status`, optional non-sensitive
  `observed`, `start_seconds`, `end_seconds`, `page_id`, screenshot, error.
  Unexecuted checkpoints stay `NOT_RUN`.
- `artifacts`: relative `path`, `kind`, `bytes`, `sha256`; videos identify their
  page, screenshots their checkpoint. Optional video decode/duration/dimensions
  describe measured results. Times are relative to the run, not frame-exact
  timestamps into every separate video.
- `artifact_errors` and `review.visual` / `review.publication`. The runner starts
  these review fields at `NOT_REVIEWED` and `NOT_PUBLISHED`.

PASS means the assertions and required capture operations completed. It is not
publication readiness. After visual inspection, write `review.json` alongside
the result with the `run_id`, inspected artifact paths and SHA-256 values,
visual findings, private-data review, and any deployment verification evidence.
Keep the original run result and prior failed attempts. Do not mark uninspected
files reviewed. Update the local Markdown's review/provenance lines from this
evidence before handing it to the publisher.

## Consumer: PR creation or editing workflow

1. Read the result and review files. Check the intended environment and PR head
   against what actually ran. A dirty checkout, changed head, or unknown deployed
   revision needs an impact assessment or rerun before claiming coverage of that
   PR. A public-site demonstration may intentionally have no application SHA;
   label it as such rather than treating the tool checkout as the application.
2. Preserve actual PASS/FAIL/BLOCKED/NOT_RUN states and links to relevant earlier
   attempts. Missing video, failed decode, missing expected capture, or absent
   visual inspection is incomplete evidence. Passing E2E cannot imply broader
   device, production, or release validation.
3. Incorporate `pr-evidence.md` into the existing PR template without removing
   unrelated content. For Japanese copy, use
   [japanese-pr-writing](../../japanese-pr-writing/SKILL.md). A writing-only
   request consumes supplied evidence; it does not start new tests or upload.
4. Publish only within the user's existing PR/evidence publication authorization.
   Follow the shared [GitHub attachment workflow](../../../references/github-attachments.md).
   Use MP4/WebM as a standalone video paragraph, outside screenshot table cells.
   Inspect size/support first. Reduce bitrate or split clips with disclosed
   coverage when necessary; keep the original and do not conceal failed actions.
5. Run attachment commands from the run directory, matching the Markdown paths
   and `--attach` arguments exactly. Merge the section into the full PR body and
   use `--body-file`. Media files stay out of Git. Do not send JSON, Python, or
   traces through the media uploader; they remain local unless another artifact
   destination is explicitly authorized.
6. Read back the saved body and confirm every image renders and every video
   plays under the correct run/attempt. Record final attachment URLs and the
   target PR/comment URL in `publication.json`. Retry only missing uploads after
   partial success; never create duplicate PRs/comments as a retry strategy.

For [playwright-pr-qa](../../playwright-pr-qa/SKILL.md), preserve its approved
plan and append-only comment ledger. Add recordings to the relevant result or
completion evidence without replacing checkpoint screenshots. Include run ID,
page/persona, checkpoint range, and attempt. The runner saves complete videos
when contexts close; do not defer required checkpoint comments while waiting
for a whole-run movie. A later evidence comment can attach finalized recordings
and link the earlier checkpoints. This does not create a new test attempt.
