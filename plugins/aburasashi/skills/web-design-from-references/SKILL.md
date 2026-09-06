---
name: web-design-from-references
description: Create high-fidelity website and landing-page section mockups from a supplied brand-concept image and a readable content-wireframe image. Use for visual web design or redesign exploration. Require both image roles before generating or editing images; prose alone is insufficient. Not for code-only implementation or Figma parity checks.
---

# Web Design from References

Turn visual brand direction and an established content structure into coherent
website section images. The output is a design mockup, not an implemented site
or an editable Figma design system.

## Required inputs: check before image generation or editing

Actually open and inspect both of these user-supplied image roles:

| Input role | Required evidence | Authority |
| --- | --- | --- |
| Brand concept | A concept sheet, moodboard, or brand image with usable visual direction | Brand meaning, palette, shapes, materials, image treatment, mood |
| Content wireframe | An image showing readable copy, information hierarchy, and the requested sections | Content, section order, required elements, and intended actions |

Attachments, accessible local images, and images retrieved from exact linked
design nodes are acceptable. A URL or file name alone is not inspected evidence.
One sheet can satisfy both roles when its separate regions are clearly readable.
A logo-concept sheet can establish brand direction; do not invent an entire
brand story from a bare wordmark without supporting direction.

If either role is absent, inaccessible, ambiguous, or too illegible to use,
**do not call an image generation or editing tool**. Identify the missing input
once and return a text-only input summary or useful outline. Do not create,
search for, or substitute an unsolicited concept or wireframe image to bypass
this gate. Prose, palette values, and a previously generated Hero do not replace
either required image role.

Readable companion copy supplied by the user can resolve unclear words in an
otherwise inspectable wireframe; it does not replace the wireframe image.
If only some sections are readable, identify the blocked sections and proceed
only with independently specified sections within the requested scope.
For later edits, reuse previously inspected inputs that remain accessible;
do not ask for the same attachments again unnecessarily.

## 1. Extract the reference contract

Record a concise input map with each image's identifier and role. Distinguish
observed details from interpretation and from explicit user instructions.

- Extract the audience, intended user action, section order, required copy,
  product capabilities, and any stated exclusions.
- Treat the wireframe as content authority. Redesign visual composition unless
  the user also requires its geometry; retain semantic reading order and all
  required content. Resolve meaningful conflicts with the user before generating
  the affected section.
- Derive visual rules from the concept image. Reuse supplied palette values and
  assets; label color estimates as estimates. Preserve the identity of an
  existing logo rather than redesigning it incidentally.
- Separate intentional brand motifs from incidental background decoration.
  Connect a motif to a real product relationship only when the concept supports
  it. Do not invent rings, threads, people, or photo metaphors for every product.

Do not infer unreadable prices, claims, testimonials, guarantees, CTA labels, or
product behavior. A dense dashboard, an editorial portfolio, and a photo service
need different visual priorities.

## 2. Present a concrete design outline

Before generation, show a short outline containing:

- the shared visual rules: colors, typography hierarchy, spacing, image medium,
  shape language, and action treatment;
- for each requested section: its communication goal, dominant visual, proposed
  composition, exact copy source, and relationship to adjacent sections; and
- requested viewport or aspect ratio, image dimensions, and output destination
  when relevant.

Keep stable rules across sections while varying composition to suit each
message. Translate adjectives into visible decisions: scale, position, negative
space, overlap, light, texture, and contrast. Choose photography, illustration,
product UI, or another medium from the references and product purpose.

Derive the section count, language, palette, and canvas from the inputs. Do not
default every task to seven sections, family photos, coral pills, a dark chapter,
or 1536 × 1024. Keep a consistent target viewport within a series, but allow
section heights to follow content. Reserve explicit text bounds and clearance
from imagery rather than relying on overlapping percentage allocations.

An authorized design request permits proceeding after presenting the outline;
do not add a mandatory approval round. Honor a requested review checkpoint and
pause only dependent work when a material choice remains unresolved.

## 3. Generate one section at a time

Read [references/prompt-patterns.md](references/prompt-patterns.md) when composing
generation or correction prompts. Use its common contract plus the relevant
section specification; omit irrelevant fields and resolve template values.

Use the host's supported image-generation/editing capability and follow its
tool-specific instructions. In Codex, use built-in `image_gen` by default and
the available imagegen skill. If the capability is unavailable, deliver the
outline and prompt drafts without claiming image output. Do not silently switch
to a credentialed API, CLI fallback, or another paid provider.

- Pass the actual concept and wireframe images as references, with explicit
  roles. Describing unseen images in text does not satisfy the contract.
- Generate one finished section per image, with the required copy. Do not pack
  the whole page, contact sheets, or multiple alternatives into that image.
- For a multi-section page, inspect the first representative section before
  producing dependent sections. Once it fits the direction, pass it as an
  additional style anchor where tool input limits permit. Keep the two original
  reference roles available; an anchor does not supersede them. Do not claim it
  was supplied unless it was actually passed to the tool.
- If reference capacity is limited, use faithful crops of the supplied images
  for the current section. If the required references still cannot be included,
  stop the dependent generation and explain the limitation.
- Keep copies of the submitted prompts, actual reference identifiers, section
  and viewport labels, output locations, and revision reasons. Record tool/model
  and settings only when exposed; do not guess hidden model names. Use portable
  relative paths for project records, and exclude expiring or credentialed URLs.

Retrieving remote references and generating images may use network access.
This workflow does not authorize Figma writes, deployment,
PR publication, or replacement of existing assets. Respect any such authorization
already present in the user's request instead of asking for it again.

## 4. Inspect and correct

Open every output at sufficient resolution to inspect its real contents.
Compare against the input contract, not only against the previous generated
image:

- exact copy, spelling, labels, omissions, invented text, and unintended claims;
- heading hierarchy, line breaks, clipping, text/image collisions, margins, and
  action visibility;
- brand cues, logo fidelity, image quality, and product meaning; and
- continuity across sections, useful changes in composition, and transitions.

For a local defect, edit that exact output. State the one requested change,
measurable target where useful, and the elements to preserve. Inspect both the
changed region and surrounding content afterward; preservation wording is not
proof that the rest stayed unchanged. Save a new revision unless replacement
was authorized. Never record a missing correction prompt as an executed edit.

If a correction fails or drifts, identify the cause before retrying. If repeated
targeted edits cannot resolve the defect, stop the affected loop, retain the
best verified result, and report the limitation rather than spending indefinitely
or silently redesigning approved sections. Do not add more variants once the
requested outputs meet the contract.

## 5. Deliver for web development

Return the verified section images, their order and viewport, prompt/revision
record, and any unresolved issues. Follow the user's destination and the host's
artifact rules. Use versioned files for project deliverables; temporary preview
paths are not durable implementation assets.

Explain what was visually verified and what remains a mockup. Generated text,
buttons, shadows, and shapes are pixels, not editable text or controls. A desktop
image does not verify mobile layout, accessibility, browser behavior, or product
functionality. If implementation or Figma authoring is also requested, carry
forward the reference contract into the appropriate workflow: rebuild text and
controls natively, use existing components/tokens, and verify each requested
viewport. Do not deliver a screenshot as the entire functioning UI.

For maintenance or behavioral evaluation of this skill, use
[references/evaluation-cases.md](references/evaluation-cases.md). These cases
are not additional steps for ordinary design work.
