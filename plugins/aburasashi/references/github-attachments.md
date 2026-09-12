# GitHub PR attachments with `gh`

Use this reference when publishing ReDoc or Playwright evidence. It covers
upload and publication; keep each skill's capture workflow and existing
publication authorization. An attachment command writes to GitHub immediately.

## Check support before publishing

Native attachments shipped in `gh` 2.99.0 on 2026-09-01. Check `gh --version`
and the intended command's `--help` for `--attach`. The flag is available on
`gh pr` and `gh issue` create, edit, and comment commands. See the
[release notes](https://github.com/cli/cli/releases/tag/v2.99.0).

Use the native CLI path when these conditions hold:

- The target is GitHub.com or GitHub Enterprise Cloud, including GHE.com.
  GitHub Enterprise Server is unsupported.
- The active credential is an OAuth token, classic PAT, or fine-grained PAT,
  and the account has `WRITE`, `MAINTAIN`, or `ADMIN` repository permission.
  GitHub App tokens, including an Actions `GITHUB_TOKEN`, are unsupported.
  Do not infer upload permission from the ability to post text comments.
- Files are PNG, JPG/JPEG, GIF, WebP, SVG, MP4, MOV, or WebM. The CLI feature
  does not cover arbitrary assets such as ZIP, PDF, JSON, or Playwright traces.
- Each invocation has at most 50 distinct attachments. Images/GIFs are limited
  to 10 MB; videos to 10 MB on Free plans or 100 MB on paid plans.

The [versioned CLI guidance](https://github.com/cli/cli/blob/v2.99.0/skills/gh/SKILL.md#attaching-images-and-videos)
documents token, host, and flag restrictions. The
[launch announcement](https://github.blog/changelog/2026-09-01-github-cli-media-in-issues-pull-requests-and-comments/)
documents media sizes. Recheck current support when a host or credential differs
from these conditions. Keep credentials out of command output and logs.

## Prepare the intended body

Store inspected evidence in a temporary or ignored directory. If an image only
exists as in-memory bytes, save those bytes as a local image without logging
Base64. Keep PR-only images out of Git history.

Write the complete body to a UTF-8 Markdown file and use `--body-file`. Put a
normal local image reference in each intended table cell, for example
`![Before: login error](./before.png)`, and pass that file once with
`--attach ./before.png`. Both paths resolve against the directory where `gh`
runs, **not the body file's directory**. Use the same path spelling on both
sides. See the [path-resolution change](https://github.com/cli/cli/pull/14262).

`gh` replaces matching references with uploaded URLs while keeping the table
position and Markdown alt text. Unreferenced files are appended to the body;
an unexpected appended image means the intended reference was not matched.
For appended images only, `--attach './before.png#Before: login error'` supplies
alt text. Videos do not accept flag alt text; a standalone `![](./walkthrough.mp4)`
paragraph becomes a video player. See
[Attaching files with GitHub CLI](https://docs.github.com/en/github-cli/github-cli/attaching-files-with-github-cli).

Resolve the target explicitly with `--repo OWNER/REPO` and the PR number,
especially when running from an evidence directory outside the checkout.
For `gh pr edit --body-file`, first fetch the current body, merge the evidence
sections locally, and preserve unrelated text and existing attachment URLs.
Immediately before writing, reconcile any intervening body changes. Without a
body flag, `gh pr edit --attach` retains the existing body and adds attachments.
See [`gh pr edit`](https://cli.github.com/manual/gh_pr_edit).

Do not combine `--attach` with `--web`, or with `gh pr create --dry-run`.
Use version/help checks and local body inspection for preflight; there is no
attachment dry run through `gh pr create`.

## Verify and recover without duplicate publication

Record stdout, stderr, and the exit status, including output from failed
commands. A PR or comment URL alone does not establish that all images arrived.
Uploads stop at the first failure, but earlier successful uploads can still be
written to the body before the command exits non-zero. See the
[CLI attachment guidance](https://github.com/cli/cli/blob/v2.99.0/skills/gh/SKILL.md#attaching-images-and-videos).

Before retrying, read the saved PR body or exact comment and compare every
expected file with its published reference. Preserve successful URLs, identify
the failed and not-yet-attempted files, and retry only the missing attachments
after resolving the cause. Honor a returned retry interval. Do not blindly
repeat `gh pr create`, `gh pr comment`, or the original full attachment list.
If the body write failed too, retain any reported successful asset URLs for
recovery rather than treating those uploads as rolled back.

For a PR body with more than 50 images, use successive batches of at most 50
files, reading the saved body between batches and retaining the uploaded URLs.
For append-only QA comments, use the evidence-repair procedure in that skill;
do not overwrite an earlier result to fix publication.

Read back the saved Markdown and reopen the PR or exact result comment. On
GitHub.com expect final `https://github.com/user-attachments/assets/...` URLs.
Verify every image renders in its intended cell, checkpoint, and attempt, with
no unresolved local references or unintended duplicates. A zero exit code,
local preview, or successful API read does not replace this visual check.

## Browser fallback

Use GitHub's browser attachment editor when the installed CLI lacks the flag,
the host/authentication is unsupported, or a requested file type is only
supported by the web uploader. Check the web uploader's own
[supported types and limits](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/attaching-files).
If neither path supports the requested evidence, report the specific blocker.

Prefer the signed-in Chrome session and `chrome-devtools` MCP when available.
Keep GitHub tabs separate from isolated Playwright application contexts. Paste
into the intended editor and wait for the final attachment URL. For in-memory
bytes that cannot be saved locally, create a browser `File`, put it in a
`DataTransfer`, and dispatch a paste event without logging the bytes or
credentials. The event's return value is not upload proof.

If a separate comment draft is used to obtain URLs, move the final URLs to the
intended body and discard the staging draft. Never post an upload-only comment.
After saving the intended body, perform the same read-back and visual checks.

Research checked on 2026-09-12; the linked official sources are the basis for
future updates to this shared workflow.
