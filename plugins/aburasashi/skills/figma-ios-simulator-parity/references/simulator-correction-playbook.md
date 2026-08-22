# Figma-to-iOS Simulator correction playbook

Use this reference to reproduce one Figma state on a pinned iOS Simulator,
classify the visual difference, and correct the native source that caused it.
Device and runtime mismatches can move every pixel, so normalize them before
editing SwiftUI or UIKit code.

## Pin the comparison contract

Record the contract before the first build or capture:

```text
Design: <Figma URL> / node <ID> / version or observed-at <value>
Implementation: <workspace or project> / scheme <name> / revision <value>
Simulator: <device type> / UDID <value> / iOS <runtime build> / <orientation>
Environment: <appearance> / Dynamic Type <size> / <language-region> / <state>
Accessibility: <contrast, motion, bold text, layout direction as relevant>
Boundary: <content crop | app window | full screen> / <system UI included?>
```

Figma frame dimensions commonly represent points, while exported and simulator
screenshots contain physical pixels. Record the simulator's logical dimensions
and display scale, then export Figma at the corresponding scale. Select the
device by model and runtime, not by width alone: safe areas, Dynamic Island,
rounded display masks, system bars, and default control rendering differ.

The runtime matters even for the same device model. SwiftUI, UIKit controls,
materials, navigation bars, and font rasterization can change between iOS
versions. If the Figma frame does not identify its target iOS version, infer it
only from strong component or annotation evidence and disclose the uncertainty.

## Pull native design evidence

Use both structured Figma context and the rendered node:

- metadata for identity, hierarchy, position, dimensions, and device-template
  boundaries;
- design context for exact text, layout, components, variants, annotations, and
  SF Symbol or Code Connect mappings;
- variables and styles for semantic colors, spacing, and named typography;
- source assets for images and vectors; and
- a Figma screenshot or PNG export for the composed result.

When using Figma MCP for a SwiftUI implementation, request Swift and SwiftUI
context. For UIKit, request the closest available Apple or Swift context and
translate it to the project's existing UIKit architecture. React or Tailwind
output is a structural approximation; do not transliterate absolute CSS frames,
device-chrome layers, or mix-blend stacks into native code.

Do not settle for screenshot plus metadata when design context is available.
Exact copy, semantic variable names, component mappings, and SF Symbol names
cannot always be recovered from pixels.

## Distinguish system surfaces from app content

Classify these layers before choosing the screenshot boundary:

- device bezel and rounded hardware mask;
- status bar and Dynamic Island;
- home indicator;
- software keyboard and input accessory views;
- permission, share, picker, and other system sheets;
- navigation bars, toolbars, tab bars, lists, forms, and standard controls.

Bezel artwork is reference-only and never belongs in the app. Status bars,
home indicators, keyboards, and permission alerts are rendered by iOS; compare
them only when the Figma state and simulator environment describe the same
surface. Native bars and controls belong to the app hierarchy, but should use
their SwiftUI or UIKit APIs rather than traced shapes when the design depicts
the system appearance.

Choose one boundary:

- content crop for a component or a frame that deliberately excludes system
  bars;
- app-window screenshot for the complete scene without Simulator window chrome;
  or
- full-screen framebuffer when system overlays are part of the state.

Never compare a Figma device template against only an app content crop and then
"fix" the app to compensate.

## Resolve and normalize the simulator

Inspect the repository's Xcode project, schemes, test plans, destinations, and
minimum deployment target first. Resolve a single simulator UDID. Useful local
commands include the following; confirm the current Xcode syntax with
`xcrun simctl help` before automation:

```bash
xcrun simctl list devices booted
xcrun simctl ui <UDID> appearance light
xcrun simctl ui <UDID> content_size large
xcrun simctl status_bar <UDID> override --time 9:41 --wifiBars 3 --batteryState charged --batteryLevel 100
xcrun simctl io <UDID> screenshot --type=png --mask=alpha /absolute/path/to/actual.png
```

Use an exact UDID in scripts. Apply a status-bar override only when it is inside
the frozen boundary, and clear an override after the run if this task introduced
it. Do not erase, delete, or globally reset simulator data as a shortcut.

Pin these settings as relevant:

- device type, iOS runtime, orientation, and display scale;
- light or dark appearance and increased contrast;
- Dynamic Type content-size category and Bold Text;
- language, region, calendar, 12/24-hour preference, and layout direction;
- Reduce Motion and other accessibility overrides;
- software keyboard visibility and hardware-keyboard behavior;
- app permissions, notifications, location, and system sheets;
- navigation stack, selected tab, scroll offset, focus, and entered data; and
- status-bar time, network, and battery values when included.

Prefer scheme or test-plan language and region settings, Xcode environment
overrides, and existing UI-test launch arguments over changing a developer's
global Simulator settings. If settings must be changed globally, record the
previous values and restore only the values this task changed.

## Make the application state repeatable

Use the project's existing route, preview fixture, UI-test launch arguments,
launch environment, test plan, deep link, mock service, or seeded test account.
Avoid manually tapping through a long flow when a supported deterministic route
already exists. Do not add a production backdoor solely for parity capture.

For UI automation, use accessibility identifiers for stable state discovery
and wait for an observable element or model-backed condition. XCTest can take a
screenshot of the full main screen or an app window and attach the PNG to the
test result. Match the choice to the frozen boundary. Keep attachments when they
are the evidence under review; avoid publishing personal data or secrets.

Animations and asynchronous rendering should be settled before capture. Prefer
a bounded expectation over an arbitrary sleep. When the app already exposes a
UI-test configuration that disables nonessential animation or supplies fixed
data and time, reuse it. Do not change user-facing motion behavior merely to
make one screenshot deterministic.

## Compare at matching pixels and points

Keep the original simulator PNG. Export the Figma node at a scale that produces
the same pixel dimensions and boundary. If the dimensions still differ, stop
and explain the mismatch; resizing both images can hide an incorrect safe area,
screen class, or crop.

Use three views of the pair:

- side by side for content, hierarchy, system-state, and missing regions;
- 50 percent opacity overlay or blink for safe areas, baselines, bounds, and
  accumulated spacing drift; and
- pixel-diff heatmap plus raw metric for residual regions.

Normalize color profiles only when the diff tool requires it, and retain the
original files. Do not invent a universal changed-pixel tolerance. Use a
project-approved threshold when one exists; otherwise classify every remaining
region. System font antialiasing and materials can produce fine noise, while a
small wrong glyph can be semantically important.

Maintain a ledger:

| ID | Region or node | Figma | Simulator | Evidence | Root cause | Correction | Status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `IP-01` | Header title | `Title2/Emphasized` | custom 22 pt regular | overlay + Figma style | wrong text style | use semantic title style | open |

## Diagnose native mismatch patterns

| Diff pattern | Check first | Typical source correction |
| --- | --- | --- |
| Whole screen shifted vertically | device model, status bar, navigation bar, safe area, boundary | correct the contract or native container |
| Bottom region overlaps or floats | home indicator, tab bar, keyboard, safe-area inset | use system bar or safe-area APIs |
| Every system control looks different | iOS runtime, tint, control style, custom reimplementation | match runtime and use the native control |
| Repeated components differ the same way | shared view, component variant, semantic token | fix or select the shared component once |
| Text wraps, clips, or changes baseline | copy, locale, Dynamic Type, font availability, semantic style, width | correct typography or parent layout; preserve scaling |
| Icon weight or silhouette differs | SF Symbol name, variant, rendering mode, font weight, custom asset | use the mapped symbol or exported asset |
| Light and dark colors diverge | Figma variable mode, asset catalog variants, semantic system color | map the correct named or semantic color |
| Image crop differs | asset, scale, intrinsic size, content mode, clipping shape | use the original asset and intended content mode |
| Fine edge noise only | runtime build, display scale, font rasterization, material | keep environment fixed; do not nudge layout to chase noise |

Use Xcode's View Debugger to inspect the resolved hierarchy and frames. For Auto
Layout, follow the constraints affecting a mis-sized or misplaced view. For
SwiftUI, inspect the resolved size and placement and correct the nearest layout
container rather than stacking offsets on descendants.

## Correct in native order

Use this order unless evidence identifies a narrower root cause:

1. Device, runtime, boundary, state, and environment.
2. Native navigation, tab, list, form, toolbar, or control choice.
3. Existing component mapping and semantic design tokens.
4. Fonts, SF Symbols, images, and asset-catalog entries.
5. Safe area, size class, parent SwiftUI layout, or Auto Layout constraints.
6. Component dimensions, alignment, spacing, clipping, and scroll behavior.
7. Semantic typography and text wrapping.
8. Colors, materials, borders, radii, shadows, and state details.

This order follows the dependency graph: runtime and native containers define
safe areas and default control metrics; fonts and parent layout then determine
many descendant bounds. Correcting leaf offsets first creates brittle code that
breaks on another device, locale, or Dynamic Type size.

For a system-looking design, preserve platform behavior:

- SwiftUI: prefer `NavigationStack`, `TabView`, `List`, `Form`, semantic `Font`
  and `Color`, native controls, and `Image(systemName:)`.
- UIKit: prefer navigation and tab controllers, standard controls, semantic
  colors and fonts, Auto Layout, and trait-aware asset catalog entries.

Use project components and tokens before adding new ones. Do not guess SF Symbol
names, trace device chrome, hard-code black and white for semantic backgrounds,
or flatten the screen into an image. A visual correction must continue to work
with safe areas, localization, accessibility, and supported devices.

After a shared correction, check the directly affected orientations, device
classes, appearances, locales, and text sizes. Simulator parity complements but
does not replace behavior, accessibility, unit, UI, and device testing.

## Snapshot regression is an optional next gate

If the repository already uses screenshot or snapshot tests, add the corrected
state to that system when requested. XCTest attachments preserve captured PNGs
for review. Third-party libraries such as Point-Free SnapshotTesting can compare
view images and traits, but their own documentation warns that reference and
actual snapshots need the same simulator environment.

Do not add a new snapshot dependency, commit Figma exports, or rerecord a
baseline without user or project authorization. Bind any accepted baseline to
the exact Figma version, simulator runtime, device traits, and reviewed diff.

## Completion evidence

Use one of these outcomes:

- `matched`: no unresolved material region under the pinned contract;
- `matched with documented rendering noise`: only classified runtime, font,
  material, antialiasing, or color-profile noise remains;
- `partial`: some requested nodes, devices, orientations, or states were not
  checked; or
- `blocked`: the Figma source, compatible runtime, build, asset, font, or
  comparable state could not be obtained.

Report the design and code revisions, simulator contract, capture boundary,
ledger, build and test results, and artifact paths. A simulator is not proof of
hardware-specific behavior; keep physical-device verification as a separate
gate when the UI depends on camera, display, GPU, keyboard, or other hardware.

## Research basis

- [Figma MCP tools and prompts](https://developers.figma.com/docs/figma-mcp-server/tools-and-prompts/)
  documents metadata, design-context, screenshot, variable, mapping, and asset
  tools used together in design-to-code work.
- [Figma's guide to inspecting](https://help.figma.com/hc/en-us/articles/22012921621015-Guide-to-inspecting)
  covers layout, typography, component, variable, asset, annotation, and design
  change inspection.
- [Apple Human Interface Guidelines: Layout](https://developer.apple.com/design/human-interface-guidelines/layout)
  explains safe areas and validation across device sizes, orientation,
  localization, and Dynamic Type.
- [Apple Human Interface Guidelines: Typography](https://developer.apple.com/design/human-interface-guidelines/typography)
  explains semantic text styles, system fonts, and Dynamic Type behavior.
- [Running apps on simulated or physical devices](https://developer.apple.com/documentation/xcode/running-your-app-on-simulated-or-physical-devices)
  defines simulator destinations and the boundary between simulated and
  hardware verification.
- [Diagnosing issues in a running app's appearance](https://developer.apple.com/documentation/xcode/diagnosing-issues-in-the-appearance-of-your-running-app)
  documents environmental overrides and View Debugger diagnosis for SwiftUI
  and Auto Layout.
- [XCUIScreen](https://developer.apple.com/documentation/xcuiautomation/xcuiscreen)
  documents full-screen capture; [XCTest attachments](https://developer.apple.com/documentation/xctest/adding-attachments-to-tests-activities-and-issues)
  document app-window screenshot evidence in test results.
- [Xcode test plans](https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback)
  document launch arguments, environment, app language, region, and simulated
  location for repeatable tests.
- [Point-Free SnapshotTesting](https://github.com/pointfreeco/swift-snapshot-testing)
  is an optional existing-project integration for image snapshots and traits;
  its documentation also calls out same-simulator comparison requirements.
