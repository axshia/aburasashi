# Web Design from References

[Skill catalog](../README.md)

Design coherent website and landing-page section mockups from two input roles:

1. A brand-concept image showing the intended visual direction.
2. A readable content-wireframe image showing copy, hierarchy, and sections.

Both must be accessible and inspected before image generation or editing.
If either is missing, the skill returns missing-input guidance and can prepare
a text-only outline. Written instructions or a generated Hero do not replace
the required images. A single sheet with two clearly labeled regions can serve
both roles.

The workflow extracts shared design rules, proposes section-specific layouts,
generates one section per image, verifies the output, and makes targeted
corrections. Colors, imagery, section count, and canvas size follow the supplied
references instead of a fixed brand or page template.

## Invoke it

```text
Use $web-design-from-references to redesign this website.
Concept image: <attached concept sheet>
Content-wireframe image: <attached readable wireframe>
Preserve the copy and section order. Create desktop section mockups.
```

日本語でも利用できます。

```text
$web-design-from-references でWebデザインを作成してください。
コンセプト画像と、文章・情報構造が読めるワイヤーフレーム画像を添付します。
コピーと章順を維持し、構成案を示してから1セクション1画像で生成してください。
どちらかの画像が不足していたら画像生成は行わず、不足点を教えてください。
```

## Host and output boundaries

Requires a host-supported image-generation/editing tool for image output.
Codex uses built-in `image_gen` by default. Hosts without that capability can
produce the input contract and prompts; the skill does not silently fall back
to another paid service or credentialed API.

The outputs are raster design mockups. Editable Figma layers, responsive code,
browser QA, and deployment are separate work. Generation does not itself publish
the design or replace existing project assets.

See [SKILL.md](SKILL.md) for the workflow,
[prompt patterns](references/prompt-patterns.md) for reusable prompt structure,
and [evaluation cases](references/evaluation-cases.md) for maintenance checks.
