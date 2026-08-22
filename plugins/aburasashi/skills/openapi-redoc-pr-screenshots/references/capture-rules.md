# Capture rules

Apply these rules to every OpenAPI pull request visual. The generated plan is a
starting point; the final acceptance condition is a visually inspected image and
a verified pull request body.

## Comparison source

Compare the actual pull request merge base with the current head. Resolve the
base branch from pull request metadata when possible. To read the base without
changing the working tree, archive it to a temporary directory:

```bash
base_sha="$(git merge-base HEAD origin/main)"
before_dir="$(mktemp -d)"
git archive "${base_sha}" | tar -x -C "${before_dir}"
```

Replace `origin/main` with the resolved pull request base. If the OpenAPI file is
generated, run the same generation command and compatible environment in both
trees. Do not compare a generated base file with an ungenerated head file.

Identify an endpoint by its HTTP method and path. An `operationId` change does
not create a new endpoint; it is a modification of the same method and path.

## Acceptance matrix

| Change | Before cell | After cell | Expansion | Annotation |
| --- | --- | --- | --- | --- |
| Added endpoint | `EMPTY` | ReDoc image | All request and non-error response properties | None required |
| Modified endpoint or property | ReDoc image | ReDoc image | Changed ancestors only | `CHANGE` on both relevant views |
| Removed property | ReDoc image | ReDoc image | Changed ancestors only | `REMOVED` at the original row and a removal marker after |
| Removed endpoint | ReDoc image | `EMPTY REMOVED` | Only what identifies the operation | `REMOVED` around the original operation |

Treat `default`, `4xx`, and `5xx` responses as errors. Keep their response and
property accordions closed when capturing an added endpoint. Expand nested
objects recursively for request bodies and successful or informational
responses. Scalar properties do not require an accordion; their visible rows
must remain in the capture.

Use an amber border and a visible `CHANGE` badge for modifications. Use a red
border and a visible `REMOVED` badge for removals. A border without a text badge
is not sufficient because color alone must not carry the meaning.

## Rendering

Run the pinned helper rather than relying on a globally installed ReDoc or
browser package. It installs Redocly CLI and Playwright into an external cache,
builds self-contained ReDoc pages, and captures them headlessly. It first tries
an installed Google Chrome executable and otherwise downloads a Playwright
Chromium build into the same cache.

Use the same viewport and device scale for every before/after pair. Do not resize
one side merely to hide unchanged content. If automated accordion selection or
annotation is ambiguous, correct the capture deliberately and document the
manual adjustment.

## Pull request layout

Create one section per changed endpoint and one table per section:

```markdown
### `PATCH /widgets/{widgetId}`

| Before | After |
| --- | --- |
| ![Before ReDoc for PATCH /widgets/{widgetId}](BEFORE_URL) | ![After ReDoc for PATCH /widgets/{widgetId}](AFTER_URL) |
```

Use `EMPTY` or `EMPTY REMOVED` inside the missing cell. Never combine multiple
endpoints into a single screenshot or a single comparison row.

Pull-request-only screenshots belong in GitHub user attachments, not in the
repository. Versioned sample images used by this skill's documentation are the
only intended exception.
