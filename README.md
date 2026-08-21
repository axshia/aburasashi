# aburasashi

日々のソフトウェア開発にある摩擦を減らし、ボトルネックを見つけて解消するための Agent Skills コレクションです。

同じスキル本体を Claude Code と Codex の両方へ配布できる構成を採用しています。スキルは `plugins/aburasashi/skills/` だけで管理し、各プラットフォーム固有の manifest は配布メタデータだけを担当します。

> [!NOTE]
> 現在はプロジェクトの初期セットアップ段階で、配布対象のスキルはまだありません。通常の構造検証は通りますが、`make validate-release` は最初の実スキルが追加されるまで意図的に失敗します。

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

必要なのは Python 3.10 以降と `make` だけです。

```bash
make validate
```

Claude Code CLI がインストール済みなら、公式 validator も実行できます。

```bash
make validate-claude
```

スキルの追加ルールは [CONTRIBUTING.md](CONTRIBUTING.md)、ローカル導入と公開手順は [docs/publishing.md](docs/publishing.md) を参照してください。

## Design principles

- 1 つのスキル実装を Claude Code と Codex で共有する
- provider 固有の記述は、その provider の機能が本当に必要な場合だけ使う
- スクリプトは決定的に実行でき、副作用と必要な権限を明示する
- 小さなスキルを組み合わせ、コンテキスト消費と保守コストを抑える
- manifest、バージョン、公開手順を CI で継続的に検証する

## License

[MIT](LICENSE)
