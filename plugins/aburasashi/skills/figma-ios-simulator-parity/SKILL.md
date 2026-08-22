---
name: figma-ios-simulator-parity
description: Verify and correct an in-progress iOS screen against an exact, accessible Figma frame using a pinned iOS Simulator configuration, native design context, and normalized visual diffs. Use only when Figma design data, the target node, and a runnable iOS Simulator build are available; do not invoke from screenshot-only or prose-only references.
---

# Figma iOS Simulator Parity

Align a SwiftUI or UIKit implementation to the selected Figma state without
hard-coding one device screenshot or replacing native platform behavior. Read
[references/simulator-correction-playbook.md](references/simulator-correction-playbook.md)
before launching a simulator or correcting code.

## Applicability gate

Proceed only when all of the following are true:

- an accessible Figma Design file and exact frame or component node identify
  the requested iOS screen and state;
- the iOS project or workspace, scheme, and implementation revision can be
  resolved; and
- the app can be built and rendered on a specific compatible iOS Simulator.

A standalone screenshot, exported PNG, prose specification, approximate frame,
or neighboring device variant is not Figma design data. If the Figma file or
node is missing, inaccessible, ambiguous, or not the requested state, stop
using this skill and report the missing prerequisite. Do the same when no
compatible simulator runtime can render the implementation. Never claim parity
for unrepresented devices, orientations, themes, or states.

Treat the selected Figma node as the visual source of truth for its represented
state. Preserve application requirements, behavior, accessibility, and data
contracts where Figma is silent. Surface contradictions instead of encoding
mock values as product logic. Do not edit Figma unless the user separately
authorizes a design change.

## Workflow

### 1. Freeze the design and simulator contract

Before editing code, record:

- Figma URL, file key, node ID, version or last-modified value, frame
  dimensions, variable mode, and represented state;
- workspace or project, scheme, target, bundle identifier when relevant,
  checkout or revision, and data fixture;
- simulator UDID, device type, iOS runtime and build, orientation, appearance,
  Dynamic Type size, locale and region, layout direction, contrast and motion
  settings, permissions, keyboard state, navigation and scroll state; and
- capture boundary: app content, app window, or full device screen, including
  whether system bars and overlays are expected.

Resolve one exact simulator UDID. Do not use an ambiguous `booted` alias when
several simulators are running. Never erase a simulator or its app data merely
to normalize a capture without explicit authorization.

Use Figma's connected inspection tools when available. Retrieve metadata,
design context configured for the project's Apple framework, screenshot,
variables or styles, component mappings, annotations, and source assets as
relevant. For large nodes, inspect the hierarchy first and retrieve bounded
child context. Record the Figma version so a design update cannot silently
replace the baseline.

### 2. Separate app UI from device-template UI

Identify Figma layers representing the bezel, status bar, Dynamic Island, home
indicator, keyboard, permission alerts, navigation bars, tab bars, and other
system surfaces. Do not recreate system chrome inside the app merely to match a
mockup. Either exclude equivalent template layers on both sides or capture the
matching real system surface on the pinned simulator.

Determine whether the design represents a native control. Prefer the project's
existing SwiftUI or UIKit component and semantic token. Use platform controls
for system navigation, tabs, lists, forms, buttons, toggles, text styles,
semantic colors, and SF Symbols unless the design intentionally departs from
the native appearance. Treat generated React or Tailwind design code as a
structural hint, never as Swift source.

### 3. Inspect the implementation before changing it

Trace each visible region to its SwiftUI view or UIKit controller and view,
shared component, asset catalog entry, typography style, constraints or layout
container, and state source. Inspect existing snapshot tests, UI-test launch
arguments, test plans, preview fixtures, deep links, and mock services before
adding new test-only seams.

If the user requested diagnosis or review only, stop after producing an
evidence-backed diff ledger. Make source changes only when correction is in
scope.

### 4. Render and capture deterministically

Build with the repository's established Xcode or `xcodebuild` workflow and the
pinned simulator destination. Reproduce the exact state through existing test
fixtures, launch arguments, environment, deep links, or UI automation. Match
appearance, content-size category, language, region, orientation, permissions,
and system overlays. Stabilize status-bar values only when the status bar is
inside the comparison boundary.

Wait for the observable screen state, fonts, assets, and asynchronous content
to settle. Avoid arbitrary sleeps when an accessibility element, model state,
or test expectation can prove readiness. Capture the app window with XCUITest
or the full simulator framebuffer with `simctl` according to the frozen
boundary. Keep the unscaled simulator PNG and export the Figma node at the
matching pixel dimensions; do not resize one side until it merely looks close.

Keep temporary expected, actual, overlay, and diff artifacts outside the
repository unless the project has an approved snapshot-baseline policy.

### 5. Diagnose before correcting

Compare side by side, with an opacity overlay, and with a pixel-diff image when
available. Pair pixel evidence with Figma metadata and the resolved SwiftUI or
UIKit hierarchy. Use Xcode's View Debugger for misplaced or mis-sized views and
Auto Layout constraints, or for SwiftUI's resolved size and placement.

Maintain a diff ledger with a stable ID, region or node, expected value,
observed value, evidence, root cause, correction, and status. Classify each
mismatch as one of:

- device, runtime, display scale, capture boundary, or system chrome;
- data, navigation, application state, or Figma variant;
- appearance, Dynamic Type, locale, accessibility, or size class;
- wrong native control, component, variant, or semantic token;
- safe area, parent layout, Auto Layout constraint, or SwiftUI sizing;
- font, text style, wrapping, SF Symbol, image, or asset catalog entry;
- color, material, border, radius, shadow, opacity, or rendering mode; or
- simulator, font, antialiasing, subpixel, or color-profile noise.

A changed-pixel percentage alone is not a pass criterion. System UI and font
rasterization can vary across iOS and Xcode runtimes, while a small region may
contain a material semantic error.

### 6. Correct from platform roots to details

Fix an invalid comparison contract before product code. Then correct the
highest shared cause first: native container or component mapping, semantic
tokens, fonts and assets, safe area and parent layout, component geometry,
typography, and finally decorative effects or state-specific details.

Prefer the smallest maintainable source change. Do not replace the interface
with an image, copy device chrome into the app, guess an SF Symbol name from
pixels, hard-code offsets that break safe areas or Dynamic Type, or rebuild a
system control from primitives solely to match one runtime screenshot.

After each coherent correction batch:

1. rebuild or rerun on the same simulator UDID and contract;
2. capture and regenerate the overlay or pixel diff;
3. update the ledger;
4. run relevant unit, snapshot, UI, accessibility, and build checks; and
5. inspect other devices, orientations, themes, and content sizes affected by
   shared code.

If the Figma version or simulator runtime changes, reacquire the baseline. When
that change materially alters the target, ask which version is authoritative.

### 7. Close with bounded evidence

Claim parity only for the exact Figma nodes and pinned simulator conditions
actually checked. Report:

- Figma URL, node ID, version or observation time, and implementation revision;
- workspace or project, scheme, simulator model, UDID, runtime, orientation,
  appearance, content size, locale, state, and capture boundary;
- corrected differences and changed source files;
- remaining differences, exclusions, and whether each is material;
- build and test commands with results; and
- safe locations of the expected, actual, and diff artifacts.

Do not claim exact parity when Figma was inaccessible, the simulator and frame
represented different device geometry, required fonts or assets were missing,
system-template layers were compared to app content, only manual spot-checking
was performed, pixel dimensions were not normalized, or a material ledger item
remains open. State explicitly when pixel diffing was unavailable or when a
simulator cannot represent hardware-specific rendering.
