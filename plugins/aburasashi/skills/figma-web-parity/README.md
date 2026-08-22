# Figma Web Parity

[Back to aburasashi](../../../../README.md)

Compare an in-progress web implementation with an exact Figma frame, diagnose
the source of visible differences, and correct the implementation in a
repeatable render-and-diff loop.

## When it runs

The skill requires an accessible Figma Design file and an exact target node for
the screen, component, responsive variant, or interaction state being checked.
It deliberately does not run from a prose specification, a standalone
screenshot, or an approximate neighboring frame.

## What it does

- Freezes the Figma node, version, viewport, theme, data, and browser state into
  a comparison contract.
- Uses Figma metadata and variables together with the rendered design instead
  of treating a screenshot as the whole specification.
- Normalizes the implementation capture for viewport, DPR, fonts, images,
  animations, data, and crop boundary.
- Builds an evidence-backed diff ledger and classifies root causes before
  changing code.
- Corrects shared components, tokens, fonts, parent layout, typography, and
  visual finish from roots to leaves.
- Repeats capture and visual comparison after each coherent correction batch,
  while preserving the repository's normal tests and architecture.
- Reports parity only for the exact nodes and states that were actually
  compared.

## Invoke it

```text
Use $figma-web-parity to compare the implementation at <local-or-preview URL>
with <exact Figma frame URL>, correct the implementation differences, and show
the final comparison evidence.
```

If the Figma file or node cannot be accessed, the skill stops as not applicable
instead of guessing from another artifact.
