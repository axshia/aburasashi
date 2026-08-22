---
name: openapi-redoc-pr-screenshots
description: Capture and publish per-endpoint before-and-after ReDoc screenshots when an OpenAPI change needs visual evidence in a GitHub pull request. Use for added, modified, or removed OpenAPI operations and schema properties, including annotated CHANGE and REMOVED states, expanded non-error properties, and PR-ready comparison tables.
---

# OpenAPI ReDoc PR Screenshots

Create reviewable visual evidence for changed OpenAPI operations. Use the same
base and head definitions, ReDoc runtime, viewport, and capture rules on both
sides of every comparison.

Read [references/capture-rules.md](references/capture-rules.md) before capturing.
Use [scripts/redoc-pr-visuals.sh](scripts/redoc-pr-visuals.sh) for deterministic
diff detection, transient Redocly provisioning, headless rendering, annotation,
and PR Markdown generation.

## Workflow

1. Resolve the pull request base SHA and the current head content. Do not assume
   that the local default branch is the pull request base. Preserve the user's
   current checkout when obtaining the before specification.
2. Generate the before and after OpenAPI files with the same project command and
   environment when the repository does not store the final specification.
3. Run the helper:

   ```bash
   plugins/aburasashi/skills/openapi-redoc-pr-screenshots/scripts/redoc-pr-visuals.sh \
     --before /absolute/path/to/before.yaml \
     --after /absolute/path/to/after.yaml \
     --output-dir /absolute/path/to/openapi-pr-visuals
   ```

4. Inspect `capture-plan.json`. Treat each changed `METHOD /path` as a separate
   review unit. Produce exactly one before/after comparison and one pull request
   section for every changed endpoint.
5. Inspect every generated PNG against these rules:
   - For an added endpoint, use `EMPTY` for Before. In After, expand every
     request and non-error response property, including nested object
     properties. Keep error responses closed.
   - For a modified endpoint, outline each changed property or its nearest
     stable section and show a `CHANGE` label in both relevant images. Keep
     unrelated property accordions closed.
   - For a removed property, mark its original row with `REMOVED` in Before and
     show the generated removal marker in After.
   - For a removed endpoint, frame the original operation with `REMOVED` in
     Before and use `EMPTY REMOVED` for After.
6. Check the images for secrets, personal information, unrelated application
   state, clipping, unreadable labels, and incorrect accordion state.
7. Upload pull-request screenshots through the GitHub editor. Prefer the
   signed-in Chrome session and the `chrome-devtools` MCP when available. Wait
   until GitHub inserts the final `https://github.com/user-attachments/assets/…`
   URL, then replace every `{{UPLOAD:file.png}}` placeholder in `pr-section.md`.
8. Insert the generated sections into the pull request body. If a comment editor
   was used only to upload files, discard that draft. Reopen the pull request and
   verify that every image renders in its intended table cell.

Stop and report the blocker if the pull request base is uncertain, a changed
endpoint cannot be rendered, an annotation cannot be placed reliably, or the
final pull request cannot be visually verified.
