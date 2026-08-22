# aburasashi

[English](README.md) | [日本語](README.ja.md)

![aburasashi Agent Skills リポジトリのアイキャッチ](docs/assets/aburasashi-eyecatch-factory-closeup.png)

日々のソフトウェア開発における摩擦を減らし、ボトルネックを可視化して、
開発をより効率的にする Agent Skills のコレクションです。

このリポジトリは、同じスキル実装を Claude Code と Codex の両方に配布します。
スキル本体は `plugins/aburasashi/skills/` だけに配置し、プラットフォーム固有の
マニフェストには、重複した手順ではなく配布用のメタデータを記述しています。

## インストール

Aburasashi をインストールする前に、対応するホストを少なくとも1つインストールし、
ログインしてください。

- [Codex CLI](https://developers.openai.com/codex/cli)
- [Claude Code](https://code.claude.com/docs/en/quickstart)

### Codex

```bash
codex plugin marketplace add axshia/aburasashi
codex plugin add aburasashi@aburasashi
```

### Claude Code

```bash
claude plugin marketplace add axshia/aburasashi
claude plugin install aburasashi@aburasashi
```

インストールしたスキルを読み込むため、インストール後に Codex または
Claude Code で新しいセッションを開始してください。

## スキル

- [Figma iOS Simulator Parity](plugins/aburasashi/skills/figma-ios-simulator-parity/README.md)
  は、正確な Figma ノードと SwiftUI または UIKit の画面を、固定した
  iOS Simulator 条件で照合・是正します。ネイティブコントロール、safe area、
  Dynamic Type、プラットフォーム動作を維持します。
- [Figma Web Parity](plugins/aburasashi/skills/figma-web-parity/README.md)
  は、正確でアクセス可能な Figma ノードと実装中の Web 画面を、
  比較条件を揃えたキャプチャと原因別の視覚差分で照合・是正します。
  Figma デザインデータがない場合は起動しません。
- [OpenAPI ReDoc PR Screenshots](plugins/aburasashi/skills/openapi-redoc-pr-screenshots/README.md)
  は、変更された OpenAPI エンドポイントを検出し、注釈付きのヘッドレス ReDoc
  キャプチャを作成して、GitHub Pull Request 用にエンドポイントごとの変更前・変更後の
  表を準備します。
- [Playwright PR QA](plugins/aburasashi/skills/playwright-pr-qa/README.md)
  は、オーナー承認済みのマルチユーザー Web QA を実行し、ラベル付きのデスクトップ・
  モバイル証跡を取得して、追記専用のチェックポイント結果を Draft Pull Request に
  公開します。

### 例：変更されたエンドポイント

| 変更前 | 変更後 |
| --- | --- |
| ![CHANGE と REMOVED の注釈が付いた変更前の ReDoc](plugins/aburasashi/skills/openapi-redoc-pr-screenshots/assets/example/captures/get-widget-before.png) | ![CHANGE と REMOVED の注釈が付いた変更後の ReDoc](plugins/aburasashi/skills/openapi-redoc-pr-screenshots/assets/example/captures/get-widget-after.png) |

追加・削除されたエンドポイントの例、インストール時の動作、使い方については、
[スキルの README](plugins/aburasashi/skills/openapi-redoc-pr-screenshots/README.md)を
参照してください。

## リポジトリ構成

```text
.
├── .agents/plugins/marketplace.json       # Codex 用リポジトリマーケットプレイス
├── .claude-plugin/marketplace.json        # Claude Code 用マーケットプレイス
├── plugins/aburasashi/
│   ├── .codex-plugin/plugin.json          # Codex/OpenAI マニフェスト
│   ├── .claude-plugin/plugin.json         # Claude Code マニフェスト
│   └── skills/                            # 共通のスキル実装
├── scripts/validate.py                    # 外部依存のない検証スクリプト
└── docs/publishing.md                     # テストとリリースの手順
```

## 開発

開発には Python 3.10 以降と `make` が必要です。

```bash
make validate
```

Claude Code CLI がインストールされている場合は、公式バリデーターも実行します。

```bash
make validate-claude
```

スキル作成のルールについては [CONTRIBUTING.md](CONTRIBUTING.md)、ローカルでの
インストールとリリース手順については [docs/publishing.md](docs/publishing.md)を
参照してください。

## 設計原則

- Claude Code と Codex で1つのスキル実装を共有する。
- プロバイダー固有の機能が必要な場合に限り、プロバイダー固有の動作を使用する。
- スクリプトを決定的に保ち、副作用と必要な権限を明示する。
- 目的を絞ったスキルを組み合わせ、コンテキスト使用量と保守コストを抑える。
- マニフェスト、バージョン、リリース要件を CI で継続的に検証する。

## ライセンス

[MIT](LICENSE)
