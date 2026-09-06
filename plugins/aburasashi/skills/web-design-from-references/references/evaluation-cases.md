# Behavioral evaluation cases

Use these when changing the skill's input gate or generation workflow. Give an
independent evaluator the skill, a realistic request, and the specified input
artifacts. Ask it to perform the next steps without giving it the expected
behavior. Keep fixtures and outputs in a temporary workspace.

For a no-cost evaluation, disable generation/edit tools and ask for the planned
tool calls and prompts. This checks routing and decisions, not actual generated
quality. Label results accordingly. Real generation requires the normal host
capability and appropriate task authorization.

## Requests and checks

| Case | Supplied artifacts and request | Check after evaluation |
| --- | --- | --- |
| Two valid references | Brand-concept image and readable four-section B2B content wireframe; redesign the page | Both images are inspected; four section plans follow the actual content; visual choices follow this brand; one section per output; no forced family photos, seven chapters, or preset colors |
| Concept only | Concept image plus detailed prose; create the LP | No image generation or edit; identifies missing wireframe image; prose remains supporting material |
| Wireframe only | Wireframe image plus written palette; make it polished | No image generation or edit; identifies missing concept image; does not fabricate or search for one |
| Neither input | Prose-only product brief; just use your judgment and generate | No image calls; useful text-only next step; does not synthesize prerequisites |
| Unreadable copy | Concept image and wireframe with unreadable price/CTA | No guessed copy; affected section waits for a readable image or exact companion copy; independent readable sections may proceed within scope |
| Inaccessible source | Concept image and a wireframe URL that cannot be opened | Does not treat the URL as inspected evidence; no dependent image output |
| Combined sheet | One readable sheet with separately labeled concept and wireframe areas | Accepts the two roles without unnecessarily requiring two files |
| Local correction | Both original references and an existing output; reflow only a headline | Edits the exact image, states invariants, avoids full redesign, and plans inspection of changed and preserved regions |
| Lost originals | Only a generated Hero is available; finish the other sections | Does not use the Hero as a substitute for either missing original role |
| Code-only request | Both images available; change an existing CSS spacing value | Does not expand a code edit into image generation |
| No generation tool | Both valid images; produce mockups in a host without image capability | Returns outline/prompts and the capability limitation; does not claim output or silently choose a paid fallback |

## Inspect evidence

Record which inputs were actually opened, the chosen next action, planned or
executed tool calls, and any artifacts. Review decisions rather than matching
specific sentences or headings. In live generation, additionally inspect the
images for exact text, brand continuity, meaningful composition, and correction
drift. A dry run cannot prove visual quality, Figma editability, or web behavior.
