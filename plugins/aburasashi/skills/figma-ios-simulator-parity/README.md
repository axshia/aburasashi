# Figma iOS Simulator Parity

[Back to aburasashi](../../../../README.md)

Compare an in-progress SwiftUI or UIKit screen with an exact Figma frame on a
pinned iOS Simulator, diagnose each visual difference, and correct the native
implementation without tracing one screenshot into brittle layout code.

## When it runs

The skill requires:

- an accessible Figma Design file and exact target node;
- a resolvable Xcode project or workspace and scheme; and
- a compatible iOS Simulator that can build and render the target state.

It deliberately does not run from prose, a standalone image, or a related but
different Figma frame.

## What it does

- Freezes the Figma version, device, iOS runtime, orientation, appearance,
  Dynamic Type size, locale, state, and screenshot boundary.
- Separates device-template chrome from app-owned UI and preserves native iOS
  bars, controls, safe areas, semantic typography, colors, and SF Symbols.
- Produces matching Figma and Simulator captures plus an evidence-backed diff
  ledger.
- Uses Xcode's resolved SwiftUI or Auto Layout hierarchy to trace pixels back to
  source-level causes.
- Corrects native containers, shared components, tokens, assets, parent layout,
  typography, and visual finish in dependency order.
- Rebuilds and rechecks the same pinned Simulator state after each correction
  batch.
- Reports parity only for the exact Figma node and Simulator conditions that
  were actually verified.

## Invoke it

```text
Use $figma-ios-simulator-parity to compare <exact Figma frame URL> with the
<scheme and state> screen on <iPhone model and iOS runtime>, correct the native
implementation differences, and show the final comparison evidence.
```

If the Figma source or compatible Simulator build cannot be obtained, the skill
stops as not applicable instead of guessing.
