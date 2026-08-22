# Figma-to-web correction playbook

Use this reference to make the visual comparison repeatable and to turn each
visible mismatch into a source-level correction. The order is deliberate:
capture mistakes and upstream layout errors create cascades of misleading
pixel differences.

## Comparison contract

Record a contract before the first capture. A compact form is:

```text
Design: <Figma URL> / node <ID> / version or observed-at <value>
Implementation: <route or component> / revision <SHA or working tree>
State: <variant, fixture, permissions, theme, locale, pseudo-state>
Render: <browser and version> / viewport <W x H CSS px> / DPR <N>
Boundary: <viewport | full page | component selector>
Stabilization: <fonts, images, animation, time, network data>
```

The frame's width and height are not enough to identify a responsive state.
Also match the theme or variable mode, content length, component variant,
permission state, scroll position, and open, hover, focus, or disabled state
shown by the design. When Figma does not contain a requested state, mark that
state out of scope rather than inventing its expected appearance.

## Acquire two kinds of Figma evidence

Use both structured design context and a rendered image:

- Metadata establishes node identity, hierarchy, position, dimensions, and the
  frame boundary.
- Design context exposes layout, text, component and variant relationships,
  styles, variables, and annotations.
- A Figma screenshot or PNG export establishes the composed visual result.
- Variable definitions and Code Connect mappings identify reusable code tokens
  and components.
- Source asset exports prevent tracing an icon or image from pixels when the
  original asset is available.

Figma's MCP documentation exposes separate tools for metadata, design context,
screenshots, variable definitions, Code Connect mappings, and asset downloads.
That separation is useful: a screenshot alone communicates composition but not
the design-system intent behind it. If MCP access is unavailable, use Figma Dev
Mode or the REST file, node, and image endpoints to gather the equivalent
evidence. Never log access tokens or temporary asset URLs.

For very large frames, obtain a sparse outline first, identify the target child
nodes, and fetch detailed context in bounded calls. Do not compare a whole page
when the implemented change is one component unless the component's parent
layout materially controls its result.

## Normalize the browser capture

Eliminate environmental differences before editing CSS:

1. Match the frame width and intended height in CSS pixels. Record DPR
   separately; do not confuse physical screenshot pixels with CSS pixels.
2. Match desktop or mobile rendering mode, browser engine, theme, locale,
   reduced-motion or color-scheme settings, and zoom.
3. Reproduce the exact application state with deterministic fixtures where the
   project supports them. Do not change production data to manufacture a
   screenshot.
4. Wait for `document.fonts.ready`, decoded images, lazy content, and the
   application's own settled condition. A generic network-idle event may not
   prove that client-side jobs or fonts are ready.
5. Disable animations and transitions, hide the text caret, and freeze clocks
   or randomized content when they are not part of the design under test.
6. Capture the same boundary as Figma. Account for scrollbars, sticky regions,
   safe areas, and browser chrome. Crop by a stable element or explicit region,
   not by an unexplained manual offset.

Playwright can capture at CSS-pixel scale, disable animation, hide the caret,
and apply a temporary screenshot-only stylesheet. Use those controls only to
remove volatility. Hiding a product element that should match Figma is not
normalization. Record every intentionally excluded dynamic region.

Rendering varies by operating system, browser version, font installation,
headless mode, hardware, and settings. Reuse one environment during the loop.
If the project later adopts regression snapshots, generate and compare their
baselines in that same controlled environment.

## Read the diff at three levels

No one comparison view explains every mismatch:

- Side by side: best for wrong content, missing regions, states, and overall
  hierarchy.
- 50 percent opacity overlay or rapid blink: best for shifted edges, wrong
  dimensions, baselines, and cumulative spacing drift.
- Pixel-diff heatmap plus changed-pixel count: best for locating residual
  regions after dimensions are normalized.

Pair those images with Figma properties and the browser's computed CSS and box
model. Pixel differences identify where rendering diverges; structured and
computed values explain why. Use a project-approved tolerance when one exists.
Otherwise report the raw metric and classify every remaining region instead of
inventing a universal pass percentage.

Maintain a ledger such as:

| ID | Region or node | Figma | Rendered | Evidence | Root cause | Correction | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `VP-01` | Header | `gap: 16` | `gap: 12` | overlay + computed CSS | stale spacing token | use `--space-4` | open |

## Diagnose patterns before editing

| Diff pattern | Check first | Typical source correction |
| --- | --- | --- |
| Whole page shifted or scaled | viewport, DPR, zoom, crop, scrollbar, root margin | repair capture contract or root shell |
| Many descendants too wide or narrow | parent width, box sizing, grid columns, max-width | correct the nearest shared container |
| Repeated components differ identically | component mapping, variant, shared token | fix or select the shared primitive once |
| Text wraps or baselines drift | copy, font file, weight, size, line height, letter spacing, width | load the intended font and correct typography or container width |
| Spacing grows down the page | parent gap, padding, flex or grid alignment, text metrics | correct the earliest upstream layout rule |
| Icon or image silhouette differs | source asset, SVG viewBox, intrinsic size, `object-fit`, crop | use the exported or repository-native asset |
| Colors differ across a theme | Figma variable mode, CSS token mode, opacity, blend | map the correct semantic token and mode |
| Borders, radii, or shadows differ | stroke placement, width, radius, blur, spread, background | model the effect with the closest stable CSS primitive |
| Only hover, focus, open, or disabled state differs | Figma variant and browser pseudo-state | reproduce and implement that exact state |
| Fine speckle around text or curves | OS, browser, font rasterization, DPR, fractional transform | normalize environment; do not nudge layout to chase noise |

Inspect the browser's Computed panel rather than only authored declarations:
inheritance, specificity, logical properties, percentage values, and browser
defaults can make the applied value differ from the source rule being read.

## Correction order

Use this order unless the evidence identifies a narrower upstream cause:

1. Comparison contract and runtime state.
2. Existing component or variant mapping and semantic tokens.
3. Fonts, icons, images, and their loading behavior.
4. Viewport shell, outer container, grid, and parent flex or auto-layout
   equivalents.
5. Component dimensions, spacing, alignment, and overflow.
6. Typography and text wrapping.
7. Colors, borders, radii, opacity, shadows, and decorative details.
8. Interactive and responsive variants affected by shared changes.

This order is an inference from the inspected data: a parent dimension, font,
or shared token can account for hundreds of child pixels. Fixing children first
usually creates overrides that must be removed when the real cause is corrected.

Prefer repository tokens and existing components. If no mapping exists, add the
smallest maintainable implementation consistent with the codebase. Do not:

- replace the interface with a screenshot or canvas trace;
- copy autogenerated Figma markup wholesale over established architecture;
- add unexplained absolute offsets for ordinary flow layout;
- loosen global tokens to fix one screen without checking other consumers; or
- update a visual baseline merely to make a failure disappear.

After a shared-token or shared-component change, inspect all directly affected
variants and at least the neighboring responsive widths defined by the project.
Visual parity does not replace behavior, accessibility, type, lint, or
interaction validation.

## Completion evidence

Store temporary expected, actual, overlay, and diff images outside the
repository by default. A completion statement should distinguish:

- `matched`: no unresolved material regions under the frozen contract;
- `matched with documented rendering noise`: only classified font,
  antialiasing, or subpixel regions remain;
- `partial`: some target nodes or states were not checked; and
- `blocked`: the Figma source, runtime state, font, asset, or comparable capture
  could not be obtained.

Do not turn a Figma export into a committed regression baseline without project
approval and a policy for design versioning, licensing, review, and refresh.
When baseline automation is requested, reuse the repository's visual-testing
stack and bind every accepted baseline update to a reviewed Figma version.

## Research basis

- [Figma MCP tools and prompts](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/)
  documents separate metadata, design-context, screenshot, variable, mapping,
  and asset capabilities.
- [Figma REST file endpoints](https://developers.figma.com/docs/rest-api/file-endpoints/)
  document versioned node JSON and scaled node-image exports.
- [Figma's guide to inspecting](https://help.figma.com/hc/en-us/articles/22012921621015-Guide-to-inspecting)
  covers layout, typography, variables, assets, measurements, annotations, and
  design-change comparison.
- [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots)
  documents screenshot baselines, pixelmatch-based differences, and the need
  for one consistent rendering environment.
- [Playwright screenshot API](https://playwright.dev/docs/api/class-page#page-screenshot)
  documents animation, caret, crop, mask, stylesheet, and CSS-pixel controls.
- [Chrome DevTools device mode](https://developer.chrome.com/docs/devtools/device-mode)
  documents viewport, DPR, media-query, ruler, and screenshot controls.
- [Chrome DevTools CSS reference](https://developer.chrome.com/docs/devtools/css/reference)
  documents applied styles, computed values, the box model, and forced
  pseudo-states for source-level diagnosis.
- [Storybook visual tests](https://storybook.js.org/docs/writing-tests/visual-testing)
  provides an optional component-state regression path when the target
  repository already uses Storybook.
