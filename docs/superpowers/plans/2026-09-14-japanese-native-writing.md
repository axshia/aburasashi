# japanese-native-writing 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** セッション返答と日本語ドキュメントを、読み手が次の行動を決められる文章にするスキル `japanese-native-writing` を aburasashi プラグインに追加する。

**Architecture:** 既存の `japanese-pr-writing` と同じ構成（SKILL.md、README.md、agents/openai.yaml、references/）で新しいスキルディレクトリを作る。SKILL.md は短く保ち、根拠と例は references に置く。付随して bootstrap スキルのトリガー表、3 つのスキル一覧、CHANGELOG を更新する。

**Tech Stack:** Markdown、YAML frontmatter、`scripts/validate.py`（`make validate`）。

**Spec:** `docs/superpowers/specs/2026-09-14-japanese-native-writing-design.md`

## Global Constraints

- ディレクトリ名と frontmatter の `name` は `japanese-native-writing` で一致させる。
- `disable-model-invocation` を設定しない。
- プラグインディレクトリ外のファイルを参照しない。絶対パス、認証情報、私的 URL を書かない。
- SKILL.md 本文は provider-neutral（Claude Code と Codex の両方で動く）に書く。
- `TODO` マーカーを残さない。
- バージョン番号（両マニフェストの 0.6.0）は変更しない。CHANGELOG は Unreleased に書く。
- コミットメッセージ末尾に、会話の system-reminder で指定された attribution 行を付ける。

---

### Task 1: SKILL.md を作る

**Files:**
- Create: `plugins/aburasashi/skills/japanese-native-writing/SKILL.md`

**Interfaces:**
- Produces: スキル名 `japanese-native-writing`。references/research.md と references/examples.md への相対リンク（Task 2 で作成）。

- [ ] **Step 1: 検証が「missing SKILL.md」で失敗することを確認する**

Run:
```bash
mkdir -p plugins/aburasashi/skills/japanese-native-writing && make validate
```
Expected: `plugins/aburasashi/skills/japanese-native-writing is missing SKILL.md` を含むエラーで終了コード 1。

- [ ] **Step 2: SKILL.md を書く**

次の内容で `plugins/aburasashi/skills/japanese-native-writing/SKILL.md` を作る。

````markdown
---
name: japanese-native-writing
description: Write clear, native Japanese replies and documents for the user. Puts the conclusion and its consequence first, separates done, unverified, not-done, unknown, and missing-input status, lays out options with trade-offs and asks for one decision, glosses technical terms in parentheses on first use, keeps bold and code formatting sparse, and uses ASCII diagrams only where relationships need them. Use at the first Japanese reply of a session, after context compaction, and before writing any Japanese document. Do not use for pull request titles, bodies, or review replies; use japanese-pr-writing for those.
---

# Japanese Native Writing

セッション中の返答と、依頼されたドキュメントを、読み手がその場で次の行動を決められる日本語にする。
論文的な正しさ（網羅、厳密、出典、中立）は目的にしない。必要なときだけ足す。
一度読んだら、同じセッションではコンテキスト圧縮後と、ドキュメント作成を始めるときに読み直す。

## 適用範囲を確かめる

- 対象は、ユーザーに提示する日本語の返答と、依頼された日本語ドキュメント（設計メモ、手順書、調査報告など）。
- PR のタイトル、本文、レビュー返信、検証報告は `japanese-pr-writing` に渡す。ここでは扱わない。
- ユーザーやリポジトリの文体・表記の指定があればそれを優先する。指定がなければ返答は「です・ます」。ユーザーが常体で書いていれば合わせる。
- コード、コマンド、パス、識別子、エラー文、URL はそのまま保つ。

## 結論と結果を最初に置く

冒頭の段落に次の 3 点を置き、理由と詳細は後に回す。

1. 何をしたか、または何が分かったか。
2. その結果、読み手に何が起きるか（動作が変わる、作業が必要になる、影響はない）。
3. 読み手に何を求めるか（判断、入力、確認、何もなし）。

冒頭段落だけ読んでも判断できることを基準にする。作業順の報告や前置きから始めない。
1 メッセージで求める判断は 1 つ。並列の情報は 4 項目前後までにまとめ、超えるなら階層化する。

## 実施状態と確からしさを分けて報告する

報告する事実を次の 5 状態に分け、混ぜて書かない。

```text
実施済み  やった。結果も確かめた
未確認    やったが、結果を確かめていない。何を確かめていないかを添える
未実施    やらなかった。理由を添える
不明      調べたが分からなかった。何を調べたかを添える
不足      進めるには読み手からの入力が要る。何が要るかを添える
```

CI の通過を実機の動作確認と書かない。テストを追加したことを、テストに合格したと書かない。
確からしさは「ほぼ確実」「可能性が高い」「どちらとも言えない」「可能性が低い」の段階語で書く。数値幅は併記しない。
根拠のない断定も、意味のないぼかしもしない。「おそらく」「〜のはず」には根拠を添える。断定できる箇所は断定する。

## 選択肢は同じ観点で並べ、判断は 1 つ求める

複数案があるときは、案ごとに利点、欠点、戻せるかどうか（可逆性）を同じ観点で書く。
推奨案を先頭に置き、推奨の理由を添える。
本番反映、削除、外部公開のように戻せない選択は明示する。
最後に、判断を 1 つの質問で締める。「進めてよいか」と「どの案か」を同時に聞かない。

## 用語、記号、図

専門用語は初出時に括弧で 20 字前後の説明を添え、以後は省く。
初出の単位は、同一セッション（コンテキスト圧縮後は再初出）またはドキュメント 1 本。
次は補足しない。読み手が先に使った用語と、API、URL、HTTP、JSON、YAML、CLI、CI、PR、UI、SDK、OS、ID、DB、SQL、HTML、CSS、Git、GitHub、Markdown。

太字は、読み手が判断または行動すべき箇所（決定を求める点、戻せない操作、未完了の事項）だけに使い、連続 5 語以内、1 メッセージに数か所まで。
コード書式は、そのまま入力または出力される文字列（コマンド、パス、識別子、エラー文）だけに使う。飾りには使わない。
見出しは 500 字未満の返答に付けない。絵文字は使わない。

図解は、要素が 3 つ以上あり、かつ順序、包含、依存、分岐といった関係を文章で書くと読み手が図を組み立て直す必要がある場合に限る。
それ以外は文章か箇条書きで足りる。図を描くときは次を守る。

- 1 図に 1 つのメッセージ。
- 図の前に 1 行の標題を置く。
- 罫線と矢印は ASCII だけで描く。日本語ラベルは、全角文字の幅で桁を揃える位置に置かない。
- 図の意味を文章でも 1 行添える。
- Mermaid は、レンダリングされる場所に置くドキュメントに限る。

## ドキュメントは読者と種類を決めてから構成する

書く前に、誰が何をするために読むかを決める。
文書の種類を手順書、学習用、参照用、解説のどれか 1 つに絞る。
構成は結論、前提、本文、未決事項の順。
見出しは作業や問いで付ける（「設定」ではなく「設定を変更する」）。
3 つ以上の並列は箇条書きにする。読者が既知の部分を飛ばせるようにする。

## 送る前に確認する

- 冒頭段落だけで、読み手が次の行動を決められるか。
- 5 状態が混ざっていないか。未確認を実施済みと書いていないか。
- 太字が数か所以内で、コード書式が逐語的な文字列だけか。
- 括弧補足のない初出の専門用語がないか。

根拠と例が必要なときは[調査メモ](references/research.md)と[書き換え例](references/examples.md)を読む。
通常の利用にネットワークアクセスは不要。文章を外部の校正サービスへ送らない。
````

- [ ] **Step 3: 検証が通ることを確認する**

Run: `make validate`
Expected: `ok: development structure is valid (8 skill(s))`

- [ ] **Step 4: コミット**

```bash
git add plugins/aburasashi/skills/japanese-native-writing/SKILL.md
git commit -m "feat: add japanese-native-writing skill"
```

---

### Task 2: references（調査メモと書き換え例）を作る

**Files:**
- Create: `plugins/aburasashi/skills/japanese-native-writing/references/research.md`
- Create: `plugins/aburasashi/skills/japanese-native-writing/references/examples.md`

**Interfaces:**
- Consumes: Task 1 の SKILL.md が張った相対リンク `references/research.md`、`references/examples.md`。

- [ ] **Step 1: リンク切れを確認する**

Run:
```bash
test -f plugins/aburasashi/skills/japanese-native-writing/references/research.md && echo exists || echo missing
```
Expected: `missing`

- [ ] **Step 2: research.md を書く**

構成は `japanese-pr-writing/references/research.md` と同じ。冒頭に調査日（2026-09-14）と対象、次に一次資料の表（資料、版・日付、位置付け）、テーマ別の要約（結論先出し、複数案と意思決定、実施状態と確からしさ、専門用語、強調記号、図解、会話的分かりやすさと文書構成）、スキル独自に定めた判断の表、再利用上の注意（PDF が WebFetch で読めず pdftotext を使った、やさしい日本語との方向差、推奨案先頭配置の一次資料なし、Mermaid と AA の使い分けの一次資料なし）。資料の例文は転載しない。資料一覧はスクラッチパッドの `sources-2026-09-14.md` から取る。

- [ ] **Step 3: examples.md を書く**

すべて架空の例。次の節を置き、各節に修正前・修正後・判断を並べる。

1. 結論と結果を先に置く例（作業順の報告から結論先出しへ）。
2. 5 状態を分ける例（「対応しました」を実施済み・未確認・未実施に分解）。
3. 選択肢を同じ観点で並べる例（利点・欠点・可逆性の表と、1 つの質問）。
4. 用語を括弧で補足する例と、補足しない例。
5. 太字とコード書式を減らす例。
6. 図解する例（依存関係の ASCII 図と標題）と、図解しない例（要素 2 つ）。
7. ドキュメントの構成例（見出しを作業で付ける）。
8. 適用しない例（PR 本文は `japanese-pr-writing` に渡す。ユーザーが常体で書いている場合は常体に合わせる）。

- [ ] **Step 4: 検証とリンク確認**

Run:
```bash
make validate && grep -o 'references/[a-z-]*\.md' plugins/aburasashi/skills/japanese-native-writing/SKILL.md | sort -u | while read f; do test -f "plugins/aburasashi/skills/japanese-native-writing/$f" && echo "ok $f" || echo "missing $f"; done
```
Expected: `ok: ...` と `ok references/examples.md`、`ok references/research.md`。

- [ ] **Step 5: コミット**

```bash
git add plugins/aburasashi/skills/japanese-native-writing/references
git commit -m "docs: add research notes and examples for japanese-native-writing"
```

---

### Task 3: README、Codex 用メタデータ、トリガー表、一覧、CHANGELOG を更新する

**Files:**
- Create: `plugins/aburasashi/skills/japanese-native-writing/README.md`
- Create: `plugins/aburasashi/skills/japanese-native-writing/agents/openai.yaml`
- Modify: `plugins/aburasashi/skills/using-aburasashi/SKILL.md`（Trigger cues 表、`japanese-pr-writing` 行の直後）
- Modify: `plugins/aburasashi/skills/README.md`（ツリー図と Available skills）
- Modify: `README.md`（Skills 一覧、Japanese PR Writing の直後）
- Modify: `README.ja.md`（スキル一覧、Japanese PR Writing の直後）
- Modify: `CHANGELOG.md`（Unreleased の Added）

- [ ] **Step 1: openai.yaml を書く**

```yaml
interface:
  display_name: "Japanese Native Writing"
  short_description: "返答とドキュメントを、結論先出しで分かりやすい日本語にする"
  default_prompt: "$japanese-native-writing で、この内容を結論から先に、やっていないことと分からないことを分けて、分かりやすい日本語で提示してください。"
```

- [ ] **Step 2: README.md を書く**

`japanese-pr-writing/README.md` と同じ構成。見出しは「使い方」「書き換えの例」「適用範囲」。使い方には `$japanese-native-writing` と `/aburasashi:japanese-native-writing` の 2 例。適用範囲に、対象（セッション返答、日本語ドキュメント）、対象外（PR 文面、他言語、コードコメント）、ネットワーク不要、既定文体を書く。

- [ ] **Step 3: using-aburasashi のトリガー表に 1 行追加する**

`japanese-pr-writing` の行の直後に追加：

```markdown
| A Japanese reply, explanation, progress report, or document for the user; the first Japanese response of a session; "わかりやすく", "まとめて", "ドキュメント化", "説明して" | `japanese-native-writing` |
```

- [ ] **Step 4: 3 つのスキル一覧を更新する**

`plugins/aburasashi/skills/README.md` のツリー図に `japanese-native-writing/`（SKILL.md、README.md、agents/、references/）を `japanese-pr-writing/` の直後に追加し、Available skills に次を追加：

```markdown
- [Japanese Native Writing](japanese-native-writing/README.md) writes clear,
  native Japanese replies and documents: conclusion first, explicit done,
  unverified, not-done, unknown, and missing status, options with trade-offs,
  and sparse formatting.
```

`README.md` の Skills に追加：

```markdown
- [Japanese Native Writing](plugins/aburasashi/skills/japanese-native-writing/README.md)
  writes clear, native Japanese replies and documents for the user: conclusion
  and consequence first, explicit done, unverified, not-done, unknown, and
  missing-input status, options with trade-offs and one decision, and sparse
  emphasis; pull request copy stays with Japanese PR Writing.
```

`README.ja.md` のスキルに追加：

```markdown
- [Japanese Native Writing](plugins/aburasashi/skills/japanese-native-writing/README.md)
  は、セッション中の返答とドキュメントを、結論と結果を先に置き、実施済み・未確認・未実施・不明・不足を分け、
  選択肢を同じ観点で並べた分かりやすい日本語にします。PR 文面は Japanese PR Writing が担当します。
```

- [ ] **Step 5: CHANGELOG の Unreleased に追記する**

Added の末尾に：

```markdown
- Japanese Native Writing skill that shapes Japanese replies and documents for
  the user: conclusion and consequence first, explicit done, unverified,
  not-done, unknown, and missing-input status, options with trade-offs and a
  single decision, terms glossed on first use, sparse emphasis, and ASCII
  diagrams only where relationships need them.
```

- [ ] **Step 6: 検証**

Run: `make validate && grep -c "japanese-native-writing" plugins/aburasashi/skills/using-aburasashi/SKILL.md README.md README.ja.md plugins/aburasashi/skills/README.md CHANGELOG.md`
Expected: `ok` と、各ファイルで 1 以上。

- [ ] **Step 7: コミット**

```bash
git add plugins/aburasashi/skills/japanese-native-writing/README.md plugins/aburasashi/skills/japanese-native-writing/agents/openai.yaml plugins/aburasashi/skills/using-aburasashi/SKILL.md plugins/aburasashi/skills/README.md README.md README.ja.md CHANGELOG.md
git commit -m "docs: register japanese-native-writing in trigger cues, catalogs, and changelog"
```

---

### Task 4: 挙動を比較して確かめる

**Files:**
- なし（スクラッチパッドに結果を保存）

- [ ] **Step 1: 同じ依頼を、スキルなしとスキルありのサブエージェントに投げる**

依頼文（両方に同じもの）：

```text
次の状況を、ユーザーに報告する日本語の返答として書いてください。
- 設定ファイルの読み込み処理を修正し、ユニットテストは通った。
- 実機での起動確認はしていない。
- キャッシュの無効化を依頼されていたが、影響範囲が分からず着手していない。
- ログ出力先を S3 にするか CloudWatch にするかは決まっていない。S3 は安いが検索しにくい。CloudWatch は検索しやすいが費用が上がる。
```

スキルありのエージェントには、依頼文の前に `plugins/aburasashi/skills/japanese-native-writing/SKILL.md` を読んで従うよう指示する。

- [ ] **Step 2: 次の 4 点で比較する**

1. 冒頭段落に「したこと」「読み手に起きること」「求めること」があるか。
2. 実施済み・未確認・未実施・不足が分かれて書かれているか。
3. 2 案が同じ観点（利点・欠点・可逆性）で並び、推奨が先頭で、質問が 1 つか。
4. 太字の数と、飾りのコード書式の有無。

- [ ] **Step 3: 結果を記録する**

比較結果をスクラッチパッドの `behavior-check-2026-09-14.md` に保存し、スキルありで改善しない項目があれば SKILL.md の該当節を直して Task 4 をやり直す。

---

### Task 5: PR を作る

- [ ] **Step 1: 最終検証**

Run: `make validate`
Expected: `ok: development structure is valid (8 skill(s))`

- [ ] **Step 2: プッシュ**

```bash
git push -u origin feat/japanese-native-writing
```

- [ ] **Step 3: PR 文面を japanese-pr-writing で整えて作成する**

`superpowers:finishing-a-development-branch` の手順に従い、`aburasashi:japanese-pr-writing` で日本語の PR タイトルと本文を作る。本文には、変更の結果（新スキルの追加と発火条件）、設計 spec へのリンク、検証結果（make validate、Task 4 の比較）、未実施事項（バージョン更新はリリース時）を書く。末尾に指定の attribution 行を付ける。
