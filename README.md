# aburasashi

A collection of Agent Skills for reducing friction, exposing bottlenecks, and
making everyday software development more efficient.

The repository publishes the same skill implementations to both Claude Code and
Codex. Skills live only in `plugins/aburasashi/skills/`; platform-specific
manifests contain distribution metadata rather than duplicated instructions.

## Skills

- [OpenAPI ReDoc PR Screenshots](plugins/aburasashi/skills/openapi-redoc-pr-screenshots/README.md)
  detects changed OpenAPI endpoints, creates annotated headless ReDoc captures,
  and prepares per-endpoint Before/After tables for GitHub pull requests.
- [Playwright PR QA](plugins/aburasashi/skills/playwright-pr-qa/README.md)
  runs owner-approved multi-user web QA, captures labeled desktop and mobile
  evidence, and publishes append-only checkpoint results to Draft pull requests.

### Example: modified endpoint

| Before | After |
| --- | --- |
| ![Before ReDoc with CHANGE and REMOVED annotations](plugins/aburasashi/skills/openapi-redoc-pr-screenshots/assets/example/captures/get-widget-before.png) | ![After ReDoc with CHANGE and REMOVED annotations](plugins/aburasashi/skills/openapi-redoc-pr-screenshots/assets/example/captures/get-widget-after.png) |

See the [skill README](plugins/aburasashi/skills/openapi-redoc-pr-screenshots/README.md)
for added and removed endpoint examples, installation behavior, and usage.

## Repository layout

```text
.
├── .agents/plugins/marketplace.json       # Codex repo marketplace
├── .claude-plugin/marketplace.json        # Claude Code marketplace
├── plugins/aburasashi/
│   ├── .codex-plugin/plugin.json          # Codex/OpenAI manifest
│   ├── .claude-plugin/plugin.json         # Claude Code manifest
│   └── skills/                            # shared skill implementation
├── scripts/validate.py                    # dependency-free validation
└── docs/publishing.md                     # test and release procedure
```

## Development

Development requires Python 3.10 or later and `make`.

```bash
make validate
```

If the Claude Code CLI is installed, run its official validator as well:

```bash
make validate-claude
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for skill authoring rules and
[docs/publishing.md](docs/publishing.md) for local installation and release
procedures.

## Design principles

- Share one skill implementation between Claude Code and Codex.
- Use provider-specific behavior only when the provider capability is required.
- Keep scripts deterministic and make side effects and permissions explicit.
- Compose focused skills to limit context use and maintenance cost.
- Continuously validate manifests, versions, and release requirements in CI.

## License

[MIT](LICENSE)
