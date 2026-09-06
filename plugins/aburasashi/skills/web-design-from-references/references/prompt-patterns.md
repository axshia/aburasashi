# Prompt patterns

Use these patterns only after the two-image applicability gate passes.
They are writing aids, not tool schemas. Replace brace fields with concrete
details; omit optional fields that do not help. Prompts may use the user's
language; English is not a prerequisite for quality.

## Common direction plus one section

```text
Use case: ui-mockup.
Create ONE finished website SECTION image for {product and audience}.
Output: {viewport, pixel dimensions or supported aspect ratio}; flat front-on
website screenshot, edge-to-edge, without an outer browser/device frame or
presentation board. Render only {section}, not the whole page or alternatives.

REFERENCE ROLES:
Image 1, {actual identifier}: brand-concept reference. Derive {specific observed
visual cues and supported meaning}. Preserve {logo or other identity assets}.
Image 2, {actual identifier/region}: content wireframe. Preserve {copy, hierarchy,
section order, required elements}. Redesign composition within {user constraints}.
Image 3, {actual identifier, only if supplied}: verified style anchor. Match
{shared visual decisions}; retain this section's distinct composition.

SHARED VISUAL RULES:
Palette and roles: {background, text, accent, actions; source or estimate}.
Typography: {language, heading/body hierarchy, weight, tracking, line spacing}.
Layout: {margins, text bounds, whitespace, radii, action treatment}.
Imagery: {appropriate medium, subject or actual product example, light/materials}.
Brand motif: {only when supported; what it connects and why}.

SECTION PURPOSE:
{One message the reader should understand and any intended action.}
{Connection to previous/next section, when applicable.}

COMPOSITION:
{Dominant element, relative scale, positions, layering, and reading sequence.}
{Where text starts/ends, line breaks, and clearance from imagery.}
{Meaningful product relationship represented by the visuals.}
{Header/footer only when this section actually includes them.}

EXACT TEXT:
{Enumerate visible labels and copy verbatim, grouped by visual role.}
{Distinguish illustration/UI specimen labels from the website's real CTA.}

CONSTRAINTS:
Use only the supplied visible copy. No invented claims, prices, metrics,
testimonials, providers, badges, or guarantees.
Preserve {product distinctions that would otherwise be easy to misrepresent}.
Avoid {relevant failure modes}; instead use {desired concrete treatment}.
Return only the finished section image.
```

The outer screenshot framing does not prohibit a device or browser *inside*
the design when it communicates the product. Explain its role explicitly.
Use only devices, people, or material treatments supported by the direction.

## Composition decisions that transfer across products

- Define a dominant element and a reading sequence. A photo, editorial headline,
  product interaction, or comparison can each be the visual center.
- Pair an exclusion with a positive alternative: for example, use distinct
  upload/link/result specimens when three identical cards would obscure a flow.
- Keep repeated brand decisions stable; vary layout only to serve the message.
  A dark section or oversized photo is a choice, not a required chapter.
- If a motif conveys a connection, name the actual endpoints. If no relevant
  connection exists, omit that motif rather than inventing product meaning.
- Lock the copy before composing. For dense sections, increase available space
  or simplify the composition rather than silently removing required copy.
- For mobile work, recompose for the requested viewport and readable text.
  A scaled-down desktop mockup is not evidence of a mobile design.

## Targeted correction

```text
Edit this exact {section name and output identifier}.
Make ONE targeted correction: {observed defect and affected region}.
Required result: {exact copy/line breaks/bounds/spacing or other observable target}.
Permitted secondary adjustment: {only what is needed, or none}.
Preserve: {canvas, crop, photos/identities, logo, palette, surrounding text,
actions, motif paths, footer, and other relevant invariants}.
Do not add content or redesign other regions.
```

Supply the actual edit target through the host's supported reference mechanism
and retain access to the two original inputs. Read the current tool instructions
instead of copying another environment's parameter names. Check the whole edited
section for drift before marking the correction successful.

## Minimal working record

Use the project's existing artifact convention when present. Otherwise a small
Markdown record next to project-bound outputs is enough:

| Section / viewport | Reference roles | Submitted prompt | Output / revision | Verification / remaining issue |
| --- | --- | --- | --- | --- |
| Descriptive identifier | Actual portable identifiers | Exact prompt or relative file link | Real relative path | Observed result |

Record missing history as missing. Do not emit literal `undefined`, reconstruct
an unobserved earlier prompt, or label a proposal as a generated revision.

## Basis and limits

The workflow makes the reference roles, design decisions, content, and correction
boundaries explicit. It does not promise that every constraint will be followed
or that any single prompt phrase causes a particular quality improvement.

The [OpenAI image prompting guide](https://developers.openai.com/cookbook/examples/multimodal/image-gen-models-prompting-guide)
supports explicit reference roles, composition, exact text, and edit invariants.
Tool availability and supported arguments must be checked in the active host.
