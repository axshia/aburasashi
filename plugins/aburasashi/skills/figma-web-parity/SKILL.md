---
name: figma-web-parity
description: Verify and correct an in-progress web UI against an exact, accessible Figma frame by combining design metadata with normalized screenshots and visual diffs. Use only when Figma design data and the target node are available; do not invoke for screenshot-only references, prose-only specifications, or tasks with no Figma source.
---

# Figma Web Parity

Align the implementation to the selected Figma state without replacing product
behavior or repository conventions with generated markup. Read
[references/correction-playbook.md](references/correction-playbook.md) before
capturing or correcting the implementation.

## Applicability gate

Proceed only when all of the following are true:

- an accessible Figma Design file is identified;
- the exact frame or component node for the requested screen and state can be
  resolved; and
- the implementation can be rendered in a comparable local, development, or
  preview environment.

A screenshot, exported PNG, written description, or approximate neighboring
frame is not a substitute for the Figma design data. If the file or node is
missing, inaccessible, ambiguous, or not the requested state, stop using this
skill and report the missing prerequisite. Do not infer parity from a related
frame. If only one responsive or interactive state exists in Figma, limit the
claim to that state.

Treat the selected Figma node as the visual source of truth for its represented
state. Keep requirements, application behavior, accessibility, and real data
contracts authoritative where Figma is silent. Surface conflicts instead of
copying placeholder data into production behavior. Do not edit Figma unless the
user separately authorizes a design change.

## Workflow

### 1. Freeze the comparison contract

Before editing code, record:

- Figma file URL, node ID, file version or last-modified value when available,
  frame dimensions, and the represented variant or state;
- implementation route or component, checkout or revision, and runtime URL;
- browser engine, viewport in CSS pixels, device pixel ratio or screenshot
  scale, theme, locale, data fixture, permissions, scroll position, and any
  relevant pseudo-state; and
- the exact capture boundary: viewport, full page, or named component.

Use Figma's connected inspection tools when available. Retrieve the target
node's metadata, design context, screenshot, variables or styles, component
mapping, annotations, and source assets as relevant. For a large frame, inspect
its structure first and request detailed context for bounded child nodes. Record
the design version so a mid-run design update cannot silently change the
baseline.

### 2. Inspect the implementation before changing it

Trace the rendered regions to their source files, shared components, variants,
tokens, fonts, and assets. Prefer an existing code component or token that maps
to the Figma component over new one-off markup or literal values. Treat
generated design code as context, not as a replacement for the repository's
architecture.

If the user requested diagnosis or review only, stop after producing an
evidence-backed diff ledger. Make source changes only when correction is in
scope.

### 3. Capture a deterministic baseline

Render the exact Figma state at the frozen viewport. Wait for fonts, images,
and required data to settle; disable animation and hide the caret; stabilize
time, randomized content, and network-backed fixtures where possible. Do not
mask a visible mismatch merely to improve a diff score.

Use the repository's existing browser and visual-test tooling when suitable.
Use an existing-browser DevTools connection when the check depends on a
signed-in Chrome session, and use an isolated automation context when
repeatability matters. Default to local or preview environments and do not
exercise production side effects without separate authorization.

Export or capture the Figma node and the implementation at matching dimensions
and scale. Keep temporary parity images outside the target repository unless
the project already has an approved visual-baseline policy.

### 4. Diagnose before correcting

Compare design metadata and computed browser values as well as pixels. Review
the pair side by side, with an opacity overlay, and with a pixel-diff image when
the available tooling supports them. Maintain a diff ledger with a stable ID,
region or Figma node, expected value, observed value, evidence, likely root
cause, fix, and status.

Classify each mismatch before editing it:

- comparison environment or capture boundary;
- content, application state, or Figma variant;
- missing font, icon, image, or other asset;
- wrong shared component, variant, or design token;
- viewport, container, grid, flex, spacing, or alignment geometry;
- typography and text wrapping;
- color, border, radius, shadow, opacity, or other finish; or
- browser rasterization or subpixel noise.

Do not use a single changed-pixel percentage as the only acceptance signal.
Browser, operating-system, font, and rendering differences can create noise;
material geometry or state errors can also occupy few pixels.

### 5. Correct from roots to leaves

Fix invalid comparison conditions before product code. Then correct the highest
shared cause first: component mapping and tokens, fonts and assets, outer frame
and parent layout, component geometry, typography, then decorative effects and
state-specific details. Prefer the smallest coherent source change that fixes
the cause. Avoid screenshot-as-UI replacements, unexplained pixel offsets,
duplicate components, and broad global overrides.

After each coherent correction batch:

1. render the same frozen state again;
2. regenerate the side-by-side, overlay, or pixel diff;
3. update the ledger with what changed and what remains;
4. run the relevant type, lint, unit, component, or end-to-end checks; and
5. inspect other states and breakpoints affected by shared code.

If the Figma version changes during the loop, reacquire its context and ask the
user which version is authoritative when the change affects the target.

### 6. Close with bounded evidence

Claim parity only for the exact nodes, states, viewports, and browser conditions
actually checked. The completion report must include:

- the Figma URL, node ID, version or observation time, and implementation
  revision;
- the comparison contract and capture method;
- corrected differences and source files changed;
- remaining differences, exclusions, and whether they are material;
- validation commands and results; and
- locations of the expected, actual, and diff artifacts when they may be
  shared safely.

Do not claim exact parity when the Figma node was inaccessible, dimensions were
not normalized, required fonts or assets were missing, only visual spot-checking
was performed, the design changed without re-baselining, or a material ledger
item remains open. If pixel diffing was unavailable, say that explicitly.
