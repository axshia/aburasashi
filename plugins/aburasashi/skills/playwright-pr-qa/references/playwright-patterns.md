# Playwright execution and capture patterns

Use these patterns as constraints, not as a replacement for the target
repository's fixtures and naming conventions.

## Build the execution matrix

Derive browser projects and viewports from the repository's support policy or
existing `playwright.config`. Do not label Chromium as Google Chrome, or a
simulated viewport as a physical device. Record the actual engine, project, and
surface.

For each attempt, create a fresh context for every tuple:

```text
{run ID, checkpoint, attempt, persona, browser project, surface}
```

Playwright projects are a good fit for browser and form-factor coverage.
Within a project, use separate contexts for actors participating in the same
sequence:

```ts
const requesterContext = await browser.newContext({
  ...projectContextOptions,
  storageState: requesterStorageState,
});
const responderContext = await browser.newContext({
  ...projectContextOptions,
  storageState: responderStorageState,
});

const requesterPage = await requesterContext.newPage();
const responderPage = await responderContext.newPage();
```

Build `projectContextOptions` from the project's context and emulation settings;
do not blindly spread every test-runner option into `browser.newContext()`. Close
each manually created context in a `finally` block after its captures and traces
have been retained.

Never share one context between personas. Generate authentication state from
environment-provided test credentials or an approved fixture; do not commit
credentials or storage-state files containing live secrets.

Use a unique run marker in created content, for example
`qa-<PR>-<run>-<attempt>`. Avoid parallelizing flows that intentionally share
the same record unless the choreography itself controls the ordering.

## Make checkpoints deterministic

- Prefer accessible locators such as `getByRole`, `getByLabel`, and stable test
  IDs over layout selectors.
- Assert each checkpoint's starting state before acting.
- Pair the triggering action with its relevant response, event, or UI wait.
- Use bounded polling for eventual background jobs. Do not substitute a fixed
  sleep for an observable readiness condition.
- Verify persistence after reload when the acceptance criterion is persisted
  state, not merely a transient success message.
- Capture console, failed-request, or trace evidence when it explains a FAIL,
  but do not publish tokens, headers, request bodies, or unrelated logs.
- Take the failure screenshot before closing contexts, resetting data, or
  attempting a workaround.

## Add the evidence label

Prefer an evidence frame added after the raw screenshot when the project's
tooling already supports image composition. Otherwise inject a temporary,
non-interactive badge immediately before capture and remove it immediately
afterward. Confirm that the badge does not hide the state being proved.

The following TypeScript pattern uses only Playwright APIs and safely inserts
the label with `textContent`:

```ts
import type { Page } from "@playwright/test";

type EvidenceMetadata = {
  user: string;
  browser: string;
  surface: "desktop" | "mobile";
  checkpoint: string;
  attempt: number;
};

const BADGE_ID = "__playwright_pr_qa_evidence__";

export async function captureEvidence(
  page: Page,
  path: string,
  metadata: EvidenceMetadata,
): Promise<void> {
  const label = [
    `user: ${metadata.user}`,
    `browser: ${metadata.browser}`,
    `surface: ${metadata.surface}`,
    `checkpoint: ${metadata.checkpoint}`,
    `attempt: ${metadata.attempt}`,
  ].join(" | ");

  await page.evaluate(
    ({ id, text }) => {
      document.getElementById(id)?.remove();
      const badge = document.createElement("div");
      badge.id = id;
      badge.textContent = text;
      Object.assign(badge.style, {
        position: "fixed",
        top: "8px",
        right: "8px",
        zIndex: "2147483647",
        maxWidth: "calc(100vw - 16px)",
        padding: "5px 8px",
        border: "1px solid rgba(255, 255, 255, 0.8)",
        borderRadius: "4px",
        background: "rgba(17, 24, 39, 0.92)",
        boxShadow: "0 1px 4px rgba(0, 0, 0, 0.35)",
        color: "#fff",
        font: "600 11px/1.35 ui-monospace, SFMono-Regular, monospace",
        overflowWrap: "anywhere",
        pointerEvents: "none",
      });
      document.documentElement.appendChild(badge);
    },
    { id: BADGE_ID, text: label },
  );

  try {
    await page.screenshot({
      path,
      animations: "disabled",
      caret: "hide",
    });
  } finally {
    await page.evaluate((id) => document.getElementById(id)?.remove(), BADGE_ID);
  }
}
```

Use a public test identity in `user`, such as an approved test email or stable
persona alias. Build `browser` from the actual Playwright `browserName` and
project name. Keep the raw Base64 or image buffer out of logs.

## Preserve a retryable state

Track at least the following outside the repository and repeat it in pull
request comments so a new session can resume:

- run ID, pull request, environment, and tested head SHA;
- frozen checkpoint order and prerequisites;
- persona-to-context mapping;
- data identifiers created by the run;
- latest attempt and status for every checkpoint; and
- local capture path, uploaded URL, and result-comment URL.

After a fix, start with fresh browser contexts. Reuse server-side test data only
when its state is known and is the exact prerequisite for the failed checkpoint;
otherwise recreate it through the shortest already-proven setup path.

## Upstream references

- [Playwright isolation and multi-user contexts](https://playwright.dev/docs/browser-contexts)
- [Playwright projects for browsers and devices](https://playwright.dev/docs/test-projects)
- [`page.screenshot` API](https://playwright.dev/docs/api/class-page#page-screenshot)
- [Playwright test best practices](https://playwright.dev/docs/best-practices)
