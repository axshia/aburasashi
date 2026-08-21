# Testing and publishing

The repository is both a Claude Code marketplace and a Codex repo marketplace.
Both catalogs point to the same plugin at `plugins/aburasashi`, and both plugin
manifests load the same `skills/` directory.

## 1. Validate locally

Run the repository checks:

```bash
make validate
```

When Claude Code CLI is installed, also run its strict validator against the
plugin and marketplace:

```bash
make validate-claude
```

The OpenAI manifest is checked by the repository validator against the
required `.codex-plugin/plugin.json` contract. The structure follows the
[OpenAI plugin packaging documentation](https://developers.openai.com/plugins/build/plugins).

## 2. Test installation from this checkout

These commands modify the current user's plugin configuration. Run them only
in a development environment.

Claude Code:

```bash
claude plugin marketplace add .
claude plugin install aburasashi@aburasashi
```

Codex:

```bash
codex plugin marketplace add .
codex plugin add aburasashi@aburasashi
```

Start a new session after installation, then exercise every skill's documented
trigger and at least one non-trigger case.

## 3. Prepare a release

1. Add user-facing changes to `CHANGELOG.md`.
2. Set the same semantic version in both plugin manifests:
   - `plugins/aburasashi/.codex-plugin/plugin.json`
   - `plugins/aburasashi/.claude-plugin/plugin.json`
3. Run `make validate-release` and `make validate-claude`.
4. Test each skill in fresh Claude Code and Codex sessions.
5. Tag the verified commit as `v<version>` and push the tag.

## 4. Publish

- Claude Code: the GitHub repository already contains the required
  `.claude-plugin/marketplace.json`. Users can add `axshia/aburasashi` as a
  marketplace. Follow the
  [Claude Code marketplace documentation](https://code.claude.com/docs/en/plugin-marketplaces)
  for community submission and distribution.
- OpenAI/Codex: package `plugins/aburasashi` and follow the
  [OpenAI plugin submission documentation](https://developers.openai.com/plugins/deploy/submission).
  Public OpenAI plugins use the universal directory shared by ChatGPT and
  Codex; the repo marketplace remains useful for local and team testing.

The package validators do not replace marketplace review. Before an OpenAI
public submission, prepare a verified publisher identity, production logo,
website and support URL, public privacy policy and terms, starter prompts, five
positive test cases, three negative test cases, availability, and release
notes. Keep these materials truthful and consistent with the final skill
bundle.

Do not publish until `make validate-release` passes and the install has been
verified from the tagged commit rather than an uncommitted checkout.
