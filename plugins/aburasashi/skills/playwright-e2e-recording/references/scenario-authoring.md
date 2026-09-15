# Write and run a scenario

The bundled runner requires `uv`, Google Chrome (default), and Playwright's video
encoder. If missing, install the encoder with:

```sh
uv run --with playwright==1.62.0 playwright install ffmpeg
```

`--channel chromium` instead requires the corresponding installed Chromium.
`--mp4` requires the system `ffmpeg` command. `ffprobe` adds duration/dimension
metadata; its absence is not a reason to invent those measurements.

Resolve `SKILL_DIR` to this installed skill directory. Run from the target
checkout so workspace revision metadata describes that checkout:

```sh
uv run "$SKILL_DIR/scripts/record_e2e.py" ./scenario.py \
  --base-url https://example.com --output-root /tmp/e2e-evidence --mp4
```

Every invocation makes a new child directory. Omit `--output-root` to use the
system temporary directory, or choose a durable directory for retained evidence.
Omit `--mp4` for WebM alone. Add `--trace` only when the DOM/network trace is useful.
The runner performs no GitHub uploads and no automatic retry.

## Scenario API

Create a trusted local module with `NAME`, ordered `CHECKPOINTS` pairs, and
`run(page, recording)`. Each expectation must be backed by an assertion:

```python
from playwright.sync_api import expect

NAME = "Open the documentation"
CHECKPOINTS = [
    ("open-home", "The home heading is visible"),
    ("open-docs", "The documentation heading is visible"),
]

def run(page, recording):
    with recording.step("open-home", page) as evidence:
        response = page.goto(recording.base_url, wait_until="domcontentloaded")
        assert response and response.ok
        expect(page.get_by_role("heading", name="Welcome", exact=True)).to_be_visible()
        evidence["observed"] = "Welcome heading displayed"
    with recording.step("open-docs", page) as evidence:
        page.get_by_role("link", name="Documentation", exact=True).click()
        expect(page.get_by_role("heading", name="Documentation", exact=True)).to_be_visible()
        evidence["observed"] = "Documentation heading displayed"
```

Read the target page and replace the example labels with actual UI selectors.
`recording.step` captures a screenshot on exit, records timing and page identity,
and preserves FAIL on exception. It rejects repeated/out-of-order checkpoints.
Returning before every checkpoint passes produces FAIL. Put only non-sensitive
observations in `evidence['observed']`; the runner does not sanitize custom data.
Use `recording.block(reason)` for an unmet prerequisite; it exits with BLOCKED.
Exit codes are `0` PASS, `1` FAIL, and `2` BLOCKED.

For a popup, capture its opening using `page.expect_popup()`, then pass the popup
page to subsequent steps. Finish a checkpoint before closing its page. The
runner retains recordings even when a popup closes before the overall run ends.
For multiple actors, use the project's fixture conventions and separate contexts;
the bundled runner is a single-persona helper, not a multi-user test orchestrator.

## Existing Playwright Test projects

Keep the installed version and fixtures. A scoped config can use:

```ts
use: {
  video: { mode: 'on', size: { width: 1440, height: 1000 } },
  viewport: { width: 1440, height: 1000 },
}
```

Preserve explicit user device settings. Store screenshots at assertion points,
and export the same fields described in [PR handoff](pr-handoff.md). Collect all
attempts, not just the last retry. For manually created contexts, await their
closure before reading video paths.

## Verified mechanics

- [Playwright Python videos](https://playwright.dev/python/docs/videos): context
  closure finalizes video, explicit sizes avoid the default downscaling, and
  each page has its own video handle.
- [Playwright Test videos](https://playwright.dev/docs/videos): `on` keeps every
  attempt; failure-only modes discard successful-run evidence.
- [Trace viewer](https://playwright.dev/python/docs/trace-viewer): a trace is an
  optional debugging artifact, separate from a recording.

These API details were checked on 2026-09-15. Recheck installed-version behavior
before using newer options.
