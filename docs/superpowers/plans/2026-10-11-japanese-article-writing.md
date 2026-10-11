# japanese-article-writing 実装計画

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 社外に公開する日本語記事を書く新スキル `japanese-article-writing` を追加し、既存の `japanese-native-writing` と `japanese-pr-writing` に段落と文の規則を足す。

**Architecture:** 新スキルは既存の日本語スキルと同じ構成（SKILL.md、README.md、agents/openai.yaml、references/）で作る。規則の主な出典は倉島保美『改訂新版 書く技術・伝える技術』の 7 法則と実践編の型で、すべて自分の言葉で要約する。各スキルの変更は、サブエージェントに同じ課題を書かせる変更前後の比較で確かめる（スキル作成の RED-GREEN-REFACTOR）。

**Tech Stack:** Markdown、YAML frontmatter、`scripts/validate.py`（`make validate`）、Claude Code CLI（`make validate-claude`）、評価用のサブエージェント。

**Spec:** `docs/superpowers/specs/2026-10-11-japanese-article-writing-design.md`

## Global Constraints

- ディレクトリ名と frontmatter の `name` は `japanese-article-writing` で一致させる。
- `disable-model-invocation` を設定しない。
- プラグインディレクトリ外のファイルを参照しない。絶対パス、認証情報、私的 URL、個人情報を書かない。
- 書籍の本文と例文を転載しない。原文の引用はしない。規則は自分の言葉で要約し、例はすべて自作する。書籍の読み取りノートはリポジトリに置かない。
- 評価の入力、出力、採点記録はセッションの作業用ディレクトリ（以下 `$SCRATCH`）に置き、リポジトリにコミットしない。
- 評価用サブエージェントには、評価対象の SKILL.md のパスを渡して読ませる。Skill ツールで aburasashi のスキルを呼ばせない（インストール済みの 0.9.0 は評価対象と内容が違う）。
- `TODO` マーカーを残さない。`【要追記：…】` はスキルが出力に使う記法で、TODO マーカーではない。
- バージョン番号（両マニフェストの 0.9.0）は変更しない。CHANGELOG は Unreleased に書く。
- コミットメッセージの末尾に、次の 2 行を付ける。

```text
Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018nmrC51XkzRnXf2FCjXnf7
```

- push と PR 作成の前に、ユーザーに確認する。

## Review Focus

1. 一次情報が一部だけある材料：質問だけで止まらず、ある一次情報をリードに使い、足りない節だけ `【要追記】` にするのが期待動作。Task 3 のシナリオ F で確かめる。
2. 媒体の文体指定（常体）がある書き直し：既定の「です・ます」より指定を優先するのが期待動作。Task 3 のシナリオ E で確かめる。
3. レビューだけの依頼：書き直さず、箇所、反する規則、直し方を対応させて返すのが期待動作。Task 3 のシナリオ G で確かめる。
4. 字数指定つきで一次情報がない依頼：一般論で字数を埋めないのが期待動作。Task 3 のシナリオ B で確かめる。
5. コードブロックを含む下書きの書き直し：コードと製品名を変えないのが期待動作。Task 3 のシナリオ E で確かめる。

---

### Task 1: 評価の準備と、既存 2 スキルの変更前の測定

**Files:**
- Create: `$SCRATCH/eval/before-skills/`（現行 2 スキルの複製）
- Create: `$SCRATCH/eval/inputs/native.md`、`$SCRATCH/eval/inputs/pr.md`
- Create: `$SCRATCH/eval/rubric.md`
- Create: `$SCRATCH/eval/before/native-{1,2,3}.md`、`$SCRATCH/eval/before/pr-{1,2,3}.md`、`$SCRATCH/eval/before/scores.md`

**Interfaces:**
- Produces: 評価用プロンプトの雛形（下記）、採点基準 `rubric.md`、変更前の採点 `before/scores.md`。Task 3〜5 が使う。

- [ ] **Step 1: 作業用ディレクトリを用意し、現行のスキルを複製する**

`$SCRATCH` には、このセッションの作業用ディレクトリ（system prompt の Scratchpad directory）を入れる。

```bash
SCRATCH=<セッションの作業用ディレクトリ>
mkdir -p "$SCRATCH/eval/before-skills" "$SCRATCH/eval/inputs" "$SCRATCH/eval/before" "$SCRATCH/eval/after" "$SCRATCH/eval/article"
cp -R plugins/aburasashi/skills/japanese-native-writing plugins/aburasashi/skills/japanese-pr-writing "$SCRATCH/eval/before-skills/"
ls "$SCRATCH/eval/before-skills"
```

Expected: `japanese-native-writing  japanese-pr-writing`

- [ ] **Step 2: `japanese-native-writing` の評価入力を書く**

`$SCRATCH/eval/inputs/native.md`：

```text
依頼：次の調査メモを、チーム向けの調査報告ドキュメントにまとめてください。読むのはバックエンドチームの 6 人です。

調査メモ（田中）：
- 夜間バッチ（請求データ集計）が 9 月から遅い。8 月まで平均 42 分、9 月は平均 118 分
- 9 月 3 日に orders テーブルに discount_code 列を追加した（リリース 2.14）
- 集計クエリの実行計画を見たら、orders の全件走査になっていた。8 月のログでは idx_orders_created_at を使っていた
- 列追加のマイグレーションでテーブルを作り直していて、そのとき統計情報が古いままになった可能性
- ステージングで ANALYZE を実行したら 40 分に戻った。本番ではまだ実行していない
- ANALYZE 中はテーブルロックはかからない（PostgreSQL 15 のドキュメントで確認）
- ほかの遅いクエリは見つかっていないが、全部は見ていない。見たのは集計バッチの 3 本だけ
- 再発防止として、マイグレーション後に ANALYZE を自動で流す案と、autovacuum の閾値を下げる案がある。どちらがいいかはまだ決めていない
```

- [ ] **Step 3: `japanese-pr-writing` の評価入力を書く**

`$SCRATCH/eval/inputs/pr.md`。仕込んだ問題は 9 個（採点基準の P1〜P9）。

```text
依頼：次の PR 本文を、レビュアーが読みやすい日本語に推敲してください。技術的な意味と検証結果は変えないでください。

## 概要
ログイン後のリダイレクト先を修正したが、併せてセッションの有効期限も変更した。

## 変更内容
`RedirectResolver` という新しいクラスを追加し、ログイン後の遷移先の決定はこのクラスで行うことができるようにした。遷移先はクエリパラメータの `next` から取得されるが、外部ドメインの URL の場合は無視され、トップページになる。
セッションの有効期限は 30 分から 120 分に延ばしたが、管理画面は 30 分のまま。
- リダイレクト先の検証処理の追加
- セッションの期限を延ばしました
- テストを追加済み

## 確認
ローカルで `next` に外部 URL を入れた場合にトップページに遷移することの確認を行った。ステージングでは確認していないが、問題ないと思われる。
`SESSION_TTL` を設定しない限り、新しい期限は有効にならない。
```

- [ ] **Step 4: 採点基準を書く**

`$SCRATCH/eval/rubric.md`：

````markdown
# 採点基準

引用やコードブロックの中は数えない。機械的な検索で候補を拾い、すべて目視で判定する。

## 記事（Task 3、シナリオ A〜G）

| # | 項目 | 合格条件 |
| --- | --- | --- |
| 1 | リード | 結論と一次情報が 1 つ以上ある。予告だけの文がない。背景は 1 文以内。7 文以内 |
| 2 | 要約文 | 本文の各段落の第 1 文だけを並べて、記事の主張が通る |
| 3 | 繰り返し | 同じ数字や結論は、リードでの言及と本文での詳述の 2 か所まで。表と本文で同じ内容を二重に説明しない |
| 4 | AI 定型 | SKILL.md の置き換え表 9 項目に当たる表現が 0 件 |
| 5 | 1 文 1 ポイント | 「て、」「り、」「し、」「が、」で別々のポイントをつないだ文が 0 件（手順の羅列は除く） |
| 6 | 冗長な文末 | 「することができる」「を行う」「を実施する」「と思われる」が 0 件 |
| 7 | 情報源外の事実 | 0 件。差や割合の計算値は、計算したと分かる書き方なら可 |
| 8 | 一次情報の不足 | B：`【要追記】` と不足リストがあり、傾向や統計を作っていない。C：記事を書かず質問だけで、5 件以内、答えが記事のどこに入るかが分かる。F：質問だけで終えず、材料の一次情報をリードに使う |

シナリオ別の追加条件：

- E：常体（だ・である）で書かれている。コードブロックと製品名が入力と一致する。
- G：記事を書き直していない。指摘ごとに、箇所、反する規則、直し方が対応している。

## 既存スキル（Task 1、4、5）

| # | 項目 | 数え方 |
| --- | --- | --- |
| S1 | 段落の要点 | 本文の段落のうち、第 1 文がその段落の要点になっている割合（予告だけの文は不可） |
| S2 | 既知から未知 | 前の文や見出しに出ていない名詞句で文が始まり、つながりが読み取れない箇所の数 |
| S3 | 並列 | 並列の箇条書きや段落で、構成や文末がそろっていない箇所の数 |
| S4 | 1 文 1 ポイント | 別々のポイントを「て、」「り、」「し、」「が、」でつないだ箇所の数 |
| S5 | 冗長な文末 | 「することができる」「を行う」「を実施する」「と思われる」の数 |

退行の確認：

- native：冒頭段落に、分かったこと、読み手への影響、読み手に求めることの 3 点がある。5 状態（本番で ANALYZE は未実施、集計バッチ以外のクエリは未確認、再発防止策は未決で判断が要る）を混ぜずに書いている。情報源にない事実がない。
- pr：30 分→120 分、管理画面は 30 分のまま、ステージング未確認、`SESSION_TTL` の設定が必要、の 4 点の意味が保たれている。「問題ないと思われる」を、根拠のない断定に変えていない。

PR 入力に仕込んだ問題（推敲後に残った数を数える）：

- P1：概要の順接の「が、」
- P2：`RedirectResolver` という新しいクラスで始まる文（文頭の新情報）
- P3：「行うことができるようにした」
- P4：「取得されるが、」の連結
- P5：「延ばしたが、」の連結
- P6：箇条書きの文末の不ぞろい（体言止め、「ました」、「済み」）
- P7：「確認を行った」
- P8：根拠のない「問題ないと思われる」
- P9：「設定しない限り、有効にならない」の二重否定
````

- [ ] **Step 5: 評価用プロンプトの雛形を決める**

以後の評価はすべてこの雛形で、`subagent_type: general-purpose` のサブエージェントに渡す。並列に起動してよい。

```text
あなたは次の依頼を受けました。作業を始める前に `{SKILL_PATH}` を読み、その手順に従ってください。同じディレクトリの `references/` は、SKILL.md が指示する場合に読んでください。Skill ツールで aburasashi のスキルを呼び出さないでください（インストール済みの版は評価対象と異なるためです）。{QUESTION_RULE}成果物を `{OUT_PATH}` に保存し、成果物の本文と依頼者への返答を、そのまま最終返答に含めてください。

---
{INPUT}
```

- `{QUESTION_RULE}` の既定値：`依頼者に質問はできません。`
- シナリオ C だけ：`依頼者に質問できます。質問が必要なら、質問だけを最終返答に書いて終えてください。その場合も質問を保存してください。`

- [ ] **Step 6: 変更前の 6 回を実行する**

- native を 3 回：`{SKILL_PATH}` は `$SCRATCH/eval/before-skills/japanese-native-writing/SKILL.md`、`{INPUT}` は `inputs/native.md` の中身、`{OUT_PATH}` は `$SCRATCH/eval/before/native-1.md`〜`native-3.md`。
- pr を 3 回：`{SKILL_PATH}` は `$SCRATCH/eval/before-skills/japanese-pr-writing/SKILL.md`、`{INPUT}` は `inputs/pr.md` の中身、`{OUT_PATH}` は `$SCRATCH/eval/before/pr-1.md`〜`pr-3.md`。

Expected: 6 ファイルができる。

- [ ] **Step 7: 採点して記録する**

候補の抽出（目視の前の補助）：

```bash
cd "$SCRATCH/eval/before"
grep -n -E "て、|り、|し、|が、" native-*.md pr-*.md
grep -n -E "することができ|を行う|を行っ|を実施|と思われ" native-*.md pr-*.md
```

S1〜S5、退行の確認、P1〜P9 を目視で判定し、`$SCRATCH/eval/before/scores.md` に表で記録する。

- [ ] **Step 8: 足す規則を決める**

S1〜S5 のうち、変更前の 3 回すべてで問題が 0 件（S1 は 100%）だった項目は、失敗が観察されなかったものとして、Task 4・5 で足す規則から外す。外した項目と理由を `scores.md` に書く。コミットはしない（成果物は `$SCRATCH` だけ）。

---

### Task 2: `japanese-article-writing` 本体と付属ファイル

**Files:**
- Create: `plugins/aburasashi/skills/japanese-article-writing/SKILL.md`
- Create: `plugins/aburasashi/skills/japanese-article-writing/references/article-types.md`
- Create: `plugins/aburasashi/skills/japanese-article-writing/references/research.md`
- Create: `plugins/aburasashi/skills/japanese-article-writing/references/examples.md`
- Create: `plugins/aburasashi/skills/japanese-article-writing/README.md`
- Create: `plugins/aburasashi/skills/japanese-article-writing/agents/openai.yaml`

**Interfaces:**
- Produces: スキル名 `japanese-article-writing`。SKILL.md から `references/article-types.md`、`references/research.md`、`references/examples.md` への相対リンク。出力記法 `【要追記：入れる内容】`。Task 3 がこの SKILL.md を評価する。

- [ ] **Step 1: 検証が「missing SKILL.md」で失敗することを確認する**

```bash
mkdir -p plugins/aburasashi/skills/japanese-article-writing/references plugins/aburasashi/skills/japanese-article-writing/agents && make validate
```

Expected: `plugins/aburasashi/skills/japanese-article-writing is missing SKILL.md` を含むエラーで終了コード 2（make 経由のため）。

- [ ] **Step 2: SKILL.md を書く**

`plugins/aburasashi/skills/japanese-article-writing/SKILL.md`：

````markdown
---
name: japanese-article-writing
description: Use when drafting, rewriting, or reviewing a Japanese article for outside readers, such as an owned-media post, company or tech blog entry, how-to or explainer, comparison guide, or release announcement, and when a Japanese draft must become publishable or reads as AI-written, padded, repetitive, or generic. Do not use for pull request copy, replies to the user, or internal documents; use japanese-pr-writing or japanese-native-writing for those.
---

# Japanese Article Writing

社外の読者に公開する日本語記事を、冒頭だけで要点がつかめ、自社や筆者にしか書けない情報で成り立つ文章にする。
規則の中心は、倉島保美『改訂新版 書く技術・伝える技術』の 7 法則（冒頭に総論、パラグラフ、要約文、既知から未知、並列、1 文 1 ポイント、簡潔）。
どの規則も、読者に先の展開を予測させ、その予測どおりに書くためにある。規則にない場面は、この原理で判断する。

## 適用範囲を確かめる

- 対象は、技術ブログ、ノウハウ・解説記事、お知らせ・リリース記事など、社外に公開する日本語記事の執筆、書き直し、レビュー。
- 依頼者への返答（確認の質問、不足リスト、レビュー結果の説明）は `japanese-native-writing` で書く。PR 文面は `japanese-pr-writing` に渡す。
- 媒体のスタイルガイドや表記規約があれば、この手順より優先する。指定がなければ本文は「です・ます」。
- コード、コマンド、製品名、数値、URL は材料のとおりに保つ。
- レビューだけを頼まれたら書き直さない。箇所、反する規則、直し方を対応させて返す。
- キーワード設計、メタディスクリプション、入稿作業は扱わない。

## 読者と一次情報を決める

書く前に、次の 3 点を決める。

1. 読者：誰が、何を知りたくてこの記事を読むか。検索から来るなら、その検索で知りたいこと。
2. 読後：読み終えた読者が何を知り、何をできるようになるか。
3. 型：[記事の型](references/article-types.md)から 1 つ選ぶ。

次に、材料から一次情報を拾い出す。
一次情報は、自社や筆者しか持たない数字、事例、判断とその理由、失敗、意見を指す。
記事の価値は一次情報で決まる。一般論は、読者が一次情報を理解するための補足に回す。

リードに置ける一次情報が材料に 1 つもなければ、記事を書く前に次のどちらかを返す。

- 依頼者に質問できるなら、質問だけを返す。質問は 5 件以内にし、答えが記事のどこに入るかが分かる形にする。例：「サポートに多い質問の上位 3 つ」「導入企業の事例を 1 つ（業種、人数、何が変わったか）」。
- 質問できないなら（サブエージェント、一括処理、「とりあえず書いて」と言われた場合）、材料にある事実だけで草稿を書き、一次情報が入る位置に `【要追記：入れる内容】` を置く。草稿の外に不足リストを添え、追記するまで公開できないと書く。

一次情報が一部の節にしかないときは、その一次情報でリードを書き、足りない節だけに `【要追記】` を置く。
どの場合も、情報源にない数字、事例、引用、効果、傾向（「〜が増えています」）を作らない。
字数の指定があっても、一般論で字数を埋めない。足りない分は不足として返す。

## リードと構成を組む

1. 仮のリードを書く。リードは記事全体の総論で、結論と要点（3 つ前後）を本文の見出しと同じ順に並べる。背景を書くなら 1 文にする。長い記事でも 7 文以内にする。
2. 段落単位で構成を決める。1 段落には 1 トピックを置く。段落同士の関係は、縦（問題→原因→対策→効果のような論理の接続）か横（同じ種類の並列）のどちらかにし、どちらでもない段落は外す。縦は「その原因は」「そこで」のような言葉で接続を示す。横はリードか節の総論で列挙してから、重要な順に並べる。
3. 各見出しの直下に、その節の総論を 1〜4 文置く。段落が 2 つ程度の節では省いてよい。見出しの直後に下位の見出しを続けない。
4. 並列する節や段落は、同じ構成、同じ表現にそろえる。1 つ目を書いたら、その形を写して中身だけ差し替える。重要度に大差がある項目だけは、そろえなくてよい。
5. 各段落の要約文（最初の文）を先に書く。要約文は 1 トピック、1 文で、重要なら数字を入れて具体的に書く。続く文で「どういう意味か」「本当か」に答える（説明、言い換え、具体例、理由、データ）。
6. 要約文を集めてリードと照らし、リードを書き直す。本文の重要な情報がリードにあり、順番も同じにする。まとめにしかない情報は、リードに移すか削る。

段落の長さは、文の数ではなくトピックで決める。1〜2 文の段落が続いたら、同じトピックを分けていないか確かめる。
まとめの節は省いてよい。置くなら、リードと同じ内容を 1〜2 文で書き、新しい情報を足さない。

## 段落と文を推敲する

次の 4 つは、1 回ずつ分けて読み直す。

1. 既知から未知：文頭には前の文や見出しに出た語を置き、新しい情報は文末に回す。主語と態は、この流れで選ぶ。くどく見えても、つなぎの語を省かない。
2. 並列：並列する節、段落、箇条書きの構成と表現がそろっているか。抽象度（片方は数字、片方は「多い」）もそろえる。
3. 1 文 1 ポイント：「て、」「り、」「し、」「が、」の箇所を探す。別々のポイントをつないでいたら、関係が弱ければ文を切る。関係が強く短ければ「〜ので」「〜によって」で関係を示し、長ければ文を切って「しかし」「そのため」などを足す。順接の「が、」は使わない。手順の羅列は例外とする。
4. 簡潔さ：読者のニーズにない情報、読者が知っている説明、類語の重複（「まず最初に」）を削る。冗長な文末（「することができる」「を行う」「と思われる」）は、「できる」、動詞、根拠つきの断定に縮める。二重否定は肯定文に直す。

## AI 定型を書き換える

次の表現を見つけたら、右の形に書き換える。

| 見つけたら | 書き換え方 |
| --- | --- |
| 悩みを括弧で並べる導入、「〜ではないでしょうか」 | 結論と一次情報で始める |
| 「この記事では〜を解説します」だけの文 | 解説する中身（結論と要点）を書く |
| 根拠のない「〜が増えています」「一般的です」 | 出典か一次情報を添える。なければ削る |
| 「〜しましょう」「〜が大切です」の連続 | 理由と具体例で示す。指示は 1 回にする |
| 太字ラベル付きの箇条書きが続く | 要約文で始まる段落にする。箇条書きは手順と列挙に使う |
| 同じ数字や結論の繰り返し、表と本文の二重説明 | 詳しく書くのは 1 か所にする |
| まとめでの要点の再列挙、「ぜひ参考に」「〜になればうれしいです」 | まとめを省くか、リードと同じ内容を 1〜2 文で書く。次の行動があれば 1 つ示す |
| 「〜なのです」「〜わけです」の多用 | 平叙文で言い切る |
| 実際の数と関係ない 3 点セット | 実際にある数だけ挙げる |

## 送る前に確認する

- 要約文だけを順に読んで、記事の主張が通るか。
- リードだけで結論と要点が分かり、要点と見出しの順番が一致しているか。
- リードと各節の中心に一次情報があるか。一般論だけの節がないか。
- 情報源にない事実を足していないか。差や割合を計算した値は、計算したと分かる書き方か。
- 置き換え表の表現が残っていないか。

根拠は[調査メモ](references/research.md)、前後比較は[書き換え例](references/examples.md)を読む。
通常の利用にネットワークアクセスは不要。事実を調べた場合は、出典を依頼者に示す。未公開の原稿を外部の校正サービスへ送らない。
````

- [ ] **Step 3: 記事の型を書く**

`plugins/aburasashi/skills/japanese-article-writing/references/article-types.md`：

````markdown
# 記事の型

記事の種類ごとに、リードに置くものと本文の順番を示す。
倉島保美『改訂新版 書く技術・伝える技術』の実践編にある文書の型（提案書、調査報告書、技術報告書、回答書、作業指示書、短い文書）を、記事の構成に移した。
どの型でも、本文の見出しはリードで挙げた要点と同じ順に並べ、各段落は要約文から始める。

## 技術ブログ（検証・改善の記録）

- 使う場面：自社で試した技術、改善、障害対応の結果を伝える。
- リード：結論（何をして、何がどう変わったか）を数字で書き、要点として問題、対策、残る課題を挙げる。
- 本文の順：背景、問題、原因、対策、効果、残る課題。段落は縦につなぎ、前の段落の結果を次の段落の文頭で受ける。見送った案は、別の節で横に並べる。
- 注意：一次情報（数字、判断の理由、失敗）が記事の中心になる。手順やコードの一般的な説明は、読者が結果を理解するのに要る分だけにする。

## 「〜とは」の解説記事

- 使う場面：用語、制度、技術を説明する。
- リード：1 文の定義と、読者にとっての要点（なぜ知る必要があるか、何が分かるか）を書く。
- 本文の順：なぜ必要か（問題）、仕組み、効果、課題。
- 注意：定義と仕組みは一般論になりやすい。自社の事例や数字を、効果か課題の節に置く。置けなければ一次情報の不足として扱う。

## 「〜すべき理由」の提案記事

- 使う場面：方法、製品、考え方を勧める。
- リード：提案（何をすべきか）と、理由の要点を書く。
- 本文の順：背景（現状の問題）、提案、理由（重要な順に 1 節ずつ）、想定される反論への答え。
- 注意：理由の節は同じ構成（主張、根拠、自社の事例）にそろえる。反論への答えを省くと、読者は都合のよい話だけを読まされたと受け取る。

## 「どれを選ぶか」の比較記事

- 使う場面：複数の製品、方式、プランを比べて選び方を示す。
- リード：用途別の結論（どの用途ならどれか）を書く。
- 本文の順：前提（比較の条件）、比較の観点ごとの節（重要な順）、用途別の結論の確認。
- 注意：どの観点の節でも、候補を同じ順、同じ形で並べる。ほかの観点を理解するのに要る観点（原理など）は、重要度ではなく論理の順で先に置く。

## 手順の解説記事

- 使う場面：設定や操作のやり方を教える。
- リード：読み終えると何ができるようになるかと、前提（必要な権限、環境、所要時間）を書く。
- 本文の順：できること、仕組み（要る分だけ）、設定の全体像、手順、画面の見方。
- 注意：手順は番号付きにし、操作の直後にその結果（何が表示されるか）を書く形でそろえる。複数の手順のまとまりも、同じ形にそろえる。

## お知らせ・リリース記事

- 使う場面：新機能、仕様変更、イベント、提供条件を告知する。
- リード：総論を 2〜3 文で書く。何が、いつから、誰に（対象プランや対象者）。
- 本文の順：できること、条件と制限、設定や申し込みの方法、問い合わせ先。
- 注意：まとめの節は置かない。効果の数字には測り方（自己申告か、対象は何件か）を添える。制限は目立たない位置に置かない。
````

- [ ] **Step 4: 調査メモを書く**

`plugins/aburasashi/skills/japanese-article-writing/references/research.md`：

````markdown
# 記事執筆に関する調査メモ

調査日：2026-10-11。
対象は、社外の読者に公開する日本語記事（技術ブログ、ノウハウ・解説記事、お知らせ）です。
以下は資料の要約と、このスキルの設計判断です。
資料の本文と例文は転載せず、例はすべて独自に作成しています。

## 確認した資料

| 資料 | 版・参照箇所 | このスキルでの位置付け |
| --- | --- | --- |
| 倉島保美『改訂新版 書く技術・伝える技術』（あさ出版） | 2019 年（国立国会図書館の書誌による）。Kindle 版の基礎編、理論編の法則 1〜7、実践編 1〜7 | 規則、記事の型、作成手順の主な出典 |
| Google 検索セントラル「有用で信頼性の高い、ユーザー第一のコンテンツの作成」 | 2026-10-07 更新の版 | 一次情報と、読者の目的を先に決めることの根拠 |
| Wikipedia “Wikipedia:Signs of AI writing” | 調査日に公開されていた版 | AI 定型の分類。英語の記事が対象なので、日本語での現れ方はベースラインで補った |
| ベースライン（このリポジトリでの観察） | 2026-10-11。技術ブログ、ノウハウ記事、お知らせの 3 本 | 置き換え表と、一次情報が足りないときの振る舞いの根拠 |

## 1. 書籍の基本的な考え方

書籍は、仕事の文章の読み手は必要な部分だけを読み、全文は読まないという前提に立ちます。
そのうえで、読み手の負担を減らす条件を 3 つ挙げます。
読む量を減らしても必要な情報が伝わること、一度読めば理解できること、重要な情報が記憶に残ることです。
理解の速さは、読み手が先の展開を予測でき、その予測が当たるかどうかで決まると説明しています（認知心理学のメンタルモデル）。
書き手は内容を知っているので、自分の文章を分かりやすいと感じやすく、その感覚は当てにならない、とも述べています。

検索から来る記事の読者も、必要な情報だけを拾い、途中で読むのをやめます。
このスキルは、書籍の前提を記事にもそのまま当てはめます。
書籍は文章とスピーチを比べ、文章は読み手が読む箇所を選べるので、重要な情報を最初に置くべきだとしています。
記事の結論をまとめで明かす構成は、この考え方に反します。

## 2. 7 法則と、このスキルでの適用

| 法則 | 書籍の要点 | このスキルでの適用 |
| --- | --- | --- |
| 1. 冒頭に総論 | 冒頭に結論と重要な情報の要約を置き、各論は総論と同じ順に書く。章や節にも総論を置く。総論は具体的に書き、長い文書で 7 文前後、章や節で 1〜4 文。結論は総論と一致させ、新情報を書かない | リードを総論にする。見出しの直下に節の総論を置く。まとめの扱い |
| 2. パラグラフ | 1 トピック 1 パラグラフ。パラグラフ同士は縦（論理の接続）か横（並列）でつなぐ。補足は「どういう意味か」「本当か」に答える。文だけなら 4〜8 文が目安 | 構成の手順 2。段落の長さはトピックで決める |
| 3. 要約文 | 各論のパラグラフは冒頭に要約文を置く。1 トピックを 1 文で、具体的に書く。予告だけの文は要約文にならない。要約文だけを読んで論理が通るようにする | 構成の手順 5。送る前の確認 |
| 4. 既知から未知 | 文頭に既出の情報、文末に新しい情報を置く。統一型、引継型、展開型の 3 つの流れ方がある。くどくなってもよい。能動態か受動態かは流れで決まる | 推敲の 1 回目 |
| 5. 並列 | 並列する情報は同じ構成、同じ表現で書く。意味のある順に並べ、抽象度をそろえる。重要度に大差があればそろえない | 構成の手順 4。推敲の 2 回目 |
| 6. 1 文 1 ポイント | 「て、」「り、」「し、」「が、」で別々のポイントを並べない。関係が弱ければ切り、強ければ関係を示してつなぐか、切って接続語を足す。「が、」は避ける。羅列は例外。字数の上限より効果がある | 推敲の 3 回目 |
| 7. 簡潔 | 読み手のニーズと前提知識に合わない情報、類語の重複、冗長な文末、二重否定を直す | 推敲の 4 回目 |

## 3. 文書の型と作成手順

書籍の実践編は、文書を総論、各論、結論の 3 部で組みます。
総論は、目的のパラグラフ（背景、問題点または必要性、目的）と、要約のパラグラフ（まとめの文と、重要な情報 3 つ）からなります。
短い文書では、総論を 2〜3 文にまとめます。
このスキルでは、記事のリードを要約のパラグラフに当て、背景は 1 文までにしました。
記事の読者は記事を開いた時点で背景を知っていることが多く、背景が長い導入はベースラインで AI 定型として現れたためです。

書籍は作成手順を 11 段階で示します。
仮の総論、パラグラフ構成、並列の当たり付け、要約文、展開、総論の見直し、4 種の確認（既知から未知、並列、1 文 1 ポイント、簡潔さ）、時間をあけた見直し、の順です。
このスキルの手順は、この順をそのまま使います。
最後の段階（3 日ほどあけて見直す）はエージェントにはできないので、要約文だけを抜き出して読む確認に置き換えました。
記事の種類ごとの型は、実践編の 5 つの演習（提案書、調査報告書、技術報告書、回答書、作業指示書）と短い文書の型から作りました。

## 4. 一次情報と読者の目的

Google のガイドは、独自の情報、調査、分析があるか、他の情報源の言い換えを超える価値があるか、実体験や深い知識が示されているかを、自己評価の質問に挙げています。
読者が読み終えたときに目的を果たせるかも問います。
検索エンジンを優先したコンテンツの兆候として、他者の意見の要約にとどまること、決まった文字数を目指すことを挙げ、Google が優先する文字数はないと明記しています。

ベースラインのノウハウ記事は、一次情報のない依頼に、3,000 字の一般論で応えました。
このスキルでは、書く前に一次情報を棚卸しし、なければ質問するか、追記箇所を示した草稿を返す形にしました。
字数の指定があっても一般論で埋めないのは、この観察と Google のガイドに基づく判断です。

## 5. AI 定型

Wikipedia の “Signs of AI writing” は、AI が書いた文章に多い特徴を分類しています。
重要性の誇張、宣伝調、根拠を示さない「専門家は〜」のような帰属、誰も言っていない誤解を否定する対比、3 つ組の列挙、型どおりの結びの節、太字や箇条書きや見出しの多用などです。
同時に、これらは AI が書いた証拠ではなく、人の文章にも現れること、表面の特徴を消すことが目的ではないことを注意しています。

日本語の記事でどう現れるかは、ベースラインで確かめました。
悩みを括弧で並べる導入、「〜ではないでしょうか」、「この記事では〜を解説します」、「〜しましょう」の連続、根拠のない「〜が増えています」、まとめでの再列挙と「ぜひ参考にしてください」、「〜なのです」「〜わけです」、締めの 3 点リストが出ました。
置き換え表は、禁止の一覧ではなく「見つけたら、こう書き換える」の形にしました。
出力の形の問題には、禁止より書き換え先を示すほうが効くためです。

## 6. 書籍の規則と一般的な助言がぶつかる点

| 論点 | 一般的な助言 | 書籍の立場 | 採用 |
| --- | --- | --- | --- |
| 受動態 | 能動態にする | 既出の情報を文頭に置けるほうを選ぶ | 書籍 |
| 1 文の長さ | 40 字以内など字数で決める | 1 文 1 ポイントで決める | 書籍 |
| 段落の長さ | Web では短く改行する | 1 段落 1 トピックで 4〜8 文 | トピックで区切る。1〜2 文の段落が続いたら確かめる。4〜8 文は目安としてここに記録するだけにする |
| まとめ | 記事の最後で要点を繰り返す | 結論は総論の繰り返しで新情報を書かない。力を入れるのは総論 | 書籍。まとめは省いてよく、置くなら 1〜2 文 |

## 7. このスキルで定めた判断

次は、資料がそのまま求めている規則ではなく、このスキルの用途から定めた方針です。

| 判断 | 採用する理由 |
| --- | --- |
| 一次情報がなければ、書く前に質問する | ベースラインで、一次情報のない依頼に一般論で応えたため |
| 質問できないときは `【要追記】` つきの草稿と不足リストを返す | 一般論で埋めた記事より、追記箇所が分かる草稿のほうが公開までの作業が少ないため |
| 字数を一般論で埋めない | ベースラインの観察と、Google のガイドに基づく |
| リードの背景は 1 文まで | 長い背景の導入が、ベースラインで AI 定型として現れたため |
| 置き換え表の形にする | 出力の形の問題には、禁止より書き換え先を示すほうが効くため |
| 書籍の手順 11 を要約文の読み直しに置き換える | エージェントは時間をあけて読み直せないため |
| キーワード設計を扱わない | ユーザーの決定。読者の目的を決めるところまでを扱う |

## 調査時の注意

書籍の版は、国立国会図書館の書誌（ISBN 9784866671482）で 2019 年と確認しました。
Kindle 版はリフロー表示で、ページ番号が紙の本と一致しません。参照は章と法則の名前で示しています。
Google のガイドは更新されることがあります。基準を見直すときは、現行のページと更新日を照合してください。
通常の記事作成のたびに、これらの資料を読み直す必要はありません。
````

- [ ] **Step 5: 書き換え例を書く**

`plugins/aburasashi/skills/japanese-article-writing/references/examples.md`：

````markdown
# 記事の書き換え例

すべて架空の例です。数字も架空です。
修正後の文章だけでなく、判断の理由を確認してください。
例と同じ言い回しにそろえる必要はありません。

## 1. リードを総論にする

修正前：

> 「月末の勤怠集計に追われている」「残業時間の管理が不安」。そんな悩みを抱える総務担当の方も多いのではないでしょうか。この記事では、勤怠管理システムの選び方を解説します。

修正後：

> 勤怠管理システムは、自社の就業ルールをそのまま設定できるかで選びます。当社のサポートに届く乗り換え相談の半数は、前のシステムでシフト制の残業計算を設定できなかったことが理由です。以下では、就業ルールの確かめ方、打刻方法の選び方、無料期間での試し方の順に説明します。

判断：悩みの列挙と、予告だけの文を、結論と一次情報（乗り換え相談の内訳）に置き換えた。最後の文も予告だが、本文の見出しの順を示しているので残す。結論の後に置く予告は、読者が先の展開を予測する助けになる。

## 2. 一次情報がないときの返し方

依頼：「勤怠管理システムの選び方」の記事を 3,000 字で書いてほしい。材料は依頼文だけ。

質問できる場合の返答：

> 記事の中心に置く自社の情報が材料にないため、書く前に次の 4 点を教えてください。
>
> 1. サポートに届く乗り換え相談で、多い理由の上位 3 つ（リードと各節の冒頭に使います）
> 2. 導入企業の事例を 1 つ。業種、従業員数、導入前後で変わったこと（「試し方」の節に使います）
> 3. 自社が勧める選び方と、そう考える理由になった経験（結論に使います）
> 4. 自社製品に触れてよい範囲（記事の末尾の案内に使います）

質問できない場合の草稿（冒頭）：

> 勤怠管理システムは、自社の就業ルールをそのまま設定できるかで選びます。【要追記：乗り換え相談で多い理由の上位 3 つと、その割合】

草稿の外に添える不足リスト：

> この草稿は、次の 3 点を追記するまで公開できません。乗り換え相談で多い理由（リード）、導入企業の事例（試し方の節）、自社が勧める選び方の根拠になった経験（結論）。

判断：一般論で 3,000 字を埋めず、一次情報が入る位置と、その情報がどこに使われるかを示した。字数は追記した後で決まる。

## 3. 繰り返しを 1 か所にまとめる

修正前：

> 社内ドキュメント検索の応答時間を、2.4 秒から 0.6 秒に縮めました。
>
> | 指標 | 変更前 | 変更後 |
> | --- | --- | --- |
> | 応答時間 | 2.4 秒 | 0.6 秒 |
>
> 表のとおり、応答時間は 2.4 秒から 0.6 秒になりました。（中略）インデックスを分割した結果、応答時間は 2.4 秒から 0.6 秒になりました。
>
> ## まとめ
>
> 応答時間を 2.4 秒から 0.6 秒に短縮できました。

修正後：

> 社内ドキュメント検索の応答時間を、インデックスの分割によって 2.4 秒から 0.6 秒に縮めました。（リード）
>
> インデックスを部署ごとに分けると、1 回の検索で読む範囲は平均で 5 分の 1 になりました。応答時間の短縮は、この読む範囲の縮小によるものです。（本文）

判断：数字はリードで 1 回示し、本文には数字の理由を書いた。指標が 1 つなので表は外し、まとめも省いた。

## 4. 1 文に 1 ポイントを書く

修正前：

> 新しい料金プランは月額 980 円で、従来より 300 円安くなり、ファイルの保存容量も 2 倍になったが、外部共有の機能は上位プランだけになった。

修正後：

> 新しい料金プランの最大の変更点は、月額が従来より 300 円安い 980 円になったことです。あわせて、ファイルの保存容量は 2 倍になりました。ただし、外部共有の機能は上位プランだけで使えます。

判断：「で、」「り、」「が、」で並んでいた 3 つのポイントを分けた。最も重要な 1 点を最初の文にし、逆接は「ただし」で示した。

## 5. 既知から未知の順に並べる

修正前：

> 再設定メールの件名を「パスワード再設定のご案内」に変えました。ログインに関する問い合わせは全体の 4 割を占め、その多くは再設定メールが見つからないという相談でした。1 か月で、ログインに関する問い合わせは半分になりました。

修正後：

> 問い合わせ全体の 4 割は、ログインに関するものでした。ログインの問い合わせで多かったのは、再設定メールが見つからないという相談です。そこで再設定メールの件名を「パスワード再設定のご案内」に変えたところ、ログインに関する問い合わせは 1 か月で半分になりました。

判断：各文が前の文の文末を受けて始まる形に並べ替えた。施策を先に書くと、読者はなぜその施策なのかを予測できない。

## 6. 並列をそろえる

修正前：

> 11 月 1 日から、次の 3 点が変わります。
>
> - 請求書の PDF 出力は、A4 縦に統一
> - CSV の文字コードが UTF-8 になります
> - 請求先の住所欄は、2 行まで入力可能となりました

修正後：

> 11 月 1 日から、次の 3 点が変わります。
>
> - 請求書の PDF 出力：用紙を A4 縦に統一します
> - CSV 出力：文字コードを UTF-8 にします
> - 請求先の住所欄：2 行まで入力できるようにします

判断：「対象：変更内容」の形と文末をそろえた。3 つ目の「なりました」は、まだ変わっていない変更なのに完了したように読めたので、ほかの 2 つに合わせた。

## 7. 冗長な文末と締めを削る

修正前：

> 設定画面から通知の頻度を変更することができます。毎日の通知が多いと感じる場合は、週 1 回にまとめることも可能となっています。ぜひ自分に合った設定を見つけてみてください。

修正後：

> 通知の頻度は、設定画面で変えられます。毎日の通知が多ければ、週 1 回にまとめられます。

判断：「することができる」「可能となっている」を縮め、締めの勧誘を削った。

## 8. 適用しない例

- PR のタイトル、本文、レビュー返信。`japanese-pr-writing` に渡す。
- ユーザーへの返答や、社内向けの設計メモ、手順書、調査報告。`japanese-native-writing` に渡す。
- 媒体のスタイルガイドが「まとめの節を必ず置く」と定めている記事。スタイルガイドに従い、まとめはリードと同じ内容にする。
````

- [ ] **Step 6: README を書く**

`plugins/aburasashi/skills/japanese-article-writing/README.md`：

````markdown
# Japanese Article Writing

[Skill catalog](../README.md)

社外の読者に公開する日本語記事（技術ブログ、ノウハウ・解説記事、お知らせ）を、冒頭だけで要点がつかめ、自社や筆者にしか書けない情報で成り立つ文章にするスキルです。
倉島保美『改訂新版 書く技術・伝える技術』の 7 法則（冒頭に総論、パラグラフ、要約文、既知から未知、並列、1 文 1 ポイント、簡潔）を、記事の手順と確認に移しています。
材料に一次情報（自社の数字、事例、判断の理由、失敗、意見）がなければ、一般論で埋めずに質問するか、追記箇所を示した草稿を返します。

## 使い方

```text
$japanese-article-writing で、次の社内メモから技術ブログの記事を書いてください。
読者は、同じ規模の Web サービスで同じ問題に困っているエンジニアです。

ここにメモを貼り付けます。
```

```text
$japanese-article-writing で、この下書きを公開できる品質に直してください。
AI が書いたような定型表現と、同じ説明の繰り返しを減らしてください。
```

Claude Code では、プラグイン名を含むスラッシュコマンドでも呼び出せます。

```text
/aburasashi:japanese-article-writing 新機能のお知らせ記事を、次の材料から書いてください。
```

## 書き換えの例

変更前：

> 「月末の勤怠集計に追われている」「残業時間の管理が不安」。そんな悩みを抱える方も多いのではないでしょうか。この記事では、勤怠管理システムの選び方を解説します。

変更後：

> 勤怠管理システムは、自社の就業ルールをそのまま設定できるかで選びます。当社のサポートに届く乗り換え相談の半数は、前のシステムでシフト制の残業計算を設定できなかったことが理由です。

悩みの列挙と予告だけの文を、結論と一次情報に置き換えています（例の数字は架空です）。
一次情報が材料になければ、作らずに質問します。

## 適用範囲

- 対象：社外に公開する日本語記事の執筆、書き直し、レビュー。技術ブログ、ノウハウ・解説記事（「〜とは」、提案、比較、手順）、お知らせ・リリース記事。
- 対象外：PR 文面（`japanese-pr-writing`）、ユーザーへの返答と社内文書（`japanese-native-writing`）、SEO のキーワード設計とメタディスクリプション、入稿作業、日本語以外の記事。
- 優先するもの：媒体のスタイルガイドと表記規約。
- 通常の入力：記事の材料（社内メモ、事実の一覧、下書き）と想定読者。ネットワークアクセスは不要です。
- 補わない情報：情報源にない数字、事例、引用、効果、傾向。

[SKILL.md](SKILL.md)に手順、[記事の型](references/article-types.md)に種類ごとの構成、[調査メモ](references/research.md)に出典と採用方針、[書き換え例](references/examples.md)に前後比較を記載しています。
````

- [ ] **Step 7: Codex 向けの表示設定を書く**

`plugins/aburasashi/skills/japanese-article-writing/agents/openai.yaml`：

```yaml
interface:
  display_name: "Japanese Article Writing"
  short_description: "公開する記事を、総論先出しと一次情報中心の日本語にする"
  default_prompt: "$japanese-article-writing で、この材料から記事を書いてください。一次情報が足りなければ、書く前に質問してください。"
```

- [ ] **Step 8: 検証と禁止事項の確認をする**

```bash
make validate
grep -rn -E "/Users/|/private/|/tmp/" plugins/aburasashi/skills/japanese-article-writing || echo "no absolute paths"
grep -rn -E "TODO" plugins/aburasashi/skills/japanese-article-writing || echo "no TODO"
```

Expected: `ok: development structure is valid (11 skill(s))`、`no absolute paths`、`no TODO`。
あわせて、書籍の文をそのまま写した箇所がないことを、書籍ノートと見比べて目視で確かめる（ノートの「」で囲まれた語句が、ファイルに出ていないこと）。

- [ ] **Step 9: コミットする**

```bash
git add plugins/aburasashi/skills/japanese-article-writing
git commit -m "feat: add japanese-article-writing skill

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018nmrC51XkzRnXf2FCjXnf7"
```

---

### Task 3: 新スキルの評価と修正

**Files:**
- Create: `$SCRATCH/eval/article/inputs/{A,B,C,D,E,F,G}.md`
- Create: `$SCRATCH/eval/article/out-{A,B1,B2,C,D,E,F,G}.md`、`$SCRATCH/eval/article/scores.md`
- Modify（失敗したときだけ）: `plugins/aburasashi/skills/japanese-article-writing/SKILL.md`

**Interfaces:**
- Consumes: Task 1 の雛形と `rubric.md`、Task 2 の SKILL.md、ベースライン `$SCRATCH/baseline/{tech-blog,howto,release}.md`。

- [ ] **Step 1: シナリオの入力を書く**

A〜D はベースラインと同じ依頼文を使う。

- A（技術ブログ）：

```text
依頼：
この社内メモをもとに、会社の技術ブログ記事を書いてください。2500〜3500 字くらいで。読者は、同じくらいの規模の Web サービスで E2E テストが遅くて困っているエンジニアです。

社内メモ（QA 基盤担当・佐藤）：
- E2E テスト（Playwright、420 本）が GitHub Actions の 1 ジョブで直列実行、1 回 38 分かかっていた。PR ごとに走るので待ちが長いと不満が多かった
- Playwright の shard 機能で 4 並列にした → 14 分
- ただし最初はテスト用 DB を全シャードで共有していて、フレーキー（たまに落ちる）が増えた。失敗率 2% → 9%
- 原因：同じテストユーザーのアカウントを複数シャードが同時に更新していた
- 対策：シャードごとに DB スキーマを分け、シードデータのユーザー名に shard index を付けた → 失敗率 1.5%
- コスト：Actions の課金分数は 1 回あたり 38 分 → 56 分（並列なので合計は増える）。月 1.2 万円増。開発者の待ち時間が減ることと比べて許容と判断
- 見送った案：テストを減らす（どれを消すか合意が取れなかった）、大きいランナーで 1 ジョブ内並列（DB 競合が同じく起きるので解決にならない）
- 今後：失敗率 1.5% の残りはタイムアウト系。待機条件の見直しを進める予定
```

- B（ノウハウ、一次情報なし）：

```text
依頼：
うちは中小企業向けの勤怠管理 SaaS を提供している会社です。オウンドメディアに「勤怠管理システムの選び方」の記事を 3000 字くらいで書いてください。検索から来る中小企業の総務担当者向けです。そのまま公開できる品質でお願いします。
```

- C：B と同じ依頼文。`{QUESTION_RULE}` だけを質問できる版にする。
- D（お知らせ）：

```text
依頼：
新機能のリリースのお知らせ記事を、オウンドメディアに載せる用に書いてください。

材料：
- 機能名：シフト自動作成
- リリース日：2026 年 11 月 4 日
- 対象：スタンダードプラン以上
- 何ができるか：従業員の希望休と、日ごと・時間帯ごとの必要人数を入れると、1 か月分のシフト案を自動で作る。作った案は手で直せる
- 対象人数の上限：1 事業所 300 人まで
- ベータ版に参加した 42 社では、1 か月分のシフト作成にかかる時間が平均 6.5 時間 → 1.2 時間になった（参加企業へのアンケートによる自己申告）
- 制限：労働時間の上限チェックは「週 40 時間」だけ。変形労働時間制には未対応（2027 年春に対応予定）
- 設定方法：ヘルプページ https://example.com/help/shift-auto
- 問い合わせ：サポート窓口
```

- E（書き直し、常体指定、コードあり）：

```text
依頼：次の下書きを、当社技術ブログに公開できる品質に直してください。当ブログの表記ルールは常体（だ・である）です。材料の社内メモも付けます。

下書き：
（ここに $SCRATCH/baseline/tech-blog.md の記事本文を、見出しからそのまま貼る）

社内メモ：
（ここに A と同じ社内メモを貼る）
```

- F（ノウハウ、一次情報が一部だけ）：

```text
依頼：うちは中小企業向けの勤怠管理 SaaS を提供している会社です。オウンドメディアに「勤怠管理システムの選び方」の記事を書いてください。検索から来る中小企業の総務担当者向けです。

材料：
- サポートに届く他社からの乗り換え相談（2026 年 4〜9 月、計 212 件）の理由は、1 位がシフト制の残業計算を設定できない（118 件）、2 位が打刻漏れの修正が面倒（41 件）、3 位が給与ソフトへの取り込みで毎月手直しが要る（29 件）
- 当社としては、まず自社の就業ルールで 1 か月分の集計を無料期間中に試すことを勧めている
```

- G（レビューだけ）：

```text
依頼：次のお知らせ記事をレビューしてください。直した記事は要りません。問題のある箇所と直し方だけを挙げてください。

記事：
（ここに $SCRATCH/baseline/release.md の記事本文を貼る）
```

- [ ] **Step 2: 8 回を並列に実行する**

`{SKILL_PATH}` は `plugins/aburasashi/skills/japanese-article-writing/SKILL.md`（リポジトリ内のパスを絶対パスにして渡す）。
B は 2 回（`out-B1.md`、`out-B2.md`）、ほかは 1 回ずつ実行する。

Expected: 8 ファイルができる。

- [ ] **Step 3: 採点し、ベースラインと比べる**

```bash
cd "$SCRATCH/eval/article"
grep -n -E "て、|り、|し、|が、" out-*.md
grep -n -E "することができ|を行う|を行っ|を実施|と思われ" out-*.md
grep -n -E "ではないでしょうか|この記事では|しましょう|ぜひ|なのです|わけです|うれしいです|増えています" out-*.md ../../baseline/*.md
```

`rubric.md` の記事の 8 項目とシナリオ別の追加条件を目視で判定し、`scores.md` に表で記録する。ベースラインの 3 本（A、B、D に対応）も同じ項目で採点し、横に並べる。

Expected: すべてのシナリオで 8 項目（該当するもの）と追加条件が合格。

- [ ] **Step 4: 不合格があれば SKILL.md を直して再実行する**

不合格の項目ごとに、出力のどの文が、SKILL.md のどの記述の読み違いや抜けから来たかを `scores.md` に書く。
その原因に対応する記述だけを SKILL.md で直し、不合格だったシナリオだけを再実行して採点する。
修正と再実行は 2 巡までとし、2 巡で合格しなければ、残った不合格と原因をユーザーに報告して判断を仰ぐ。

- [ ] **Step 5: 変更があればコミットする**

```bash
make validate
git add plugins/aburasashi/skills/japanese-article-writing/SKILL.md
git commit -m "fix: tighten japanese-article-writing after evaluation

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018nmrC51XkzRnXf2FCjXnf7"
```

変更がなければコミットしない。

---

### Task 4: `japanese-native-writing` に段落と文の規則を足す

**Files:**
- Modify: `plugins/aburasashi/skills/japanese-native-writing/SKILL.md`（frontmatter の description、「適用範囲を確かめる」、新しい節、「送る前に確認する」）
- Modify: `plugins/aburasashi/skills/japanese-native-writing/references/research.md`
- Modify: `plugins/aburasashi/skills/japanese-native-writing/references/examples.md`
- Modify: `plugins/aburasashi/skills/japanese-native-writing/README.md`

**Interfaces:**
- Consumes: Task 1 の `before/scores.md`（外す規則の判断）。
- Produces: 新しい節の見出し「段落と文を組む」。

Task 1 の Step 8 で外した項目があれば、以下の該当行を入れない。

- [ ] **Step 1: description を更新する**

`plugins/aburasashi/skills/japanese-native-writing/SKILL.md` の frontmatter で、次を置き換える。

old:
```text
Do not use for pull request titles, bodies, or review replies; use japanese-pr-writing for those.
```

new:
```text
Do not use for pull request titles, bodies, or review replies, or for the body of a Japanese article for outside readers; use japanese-pr-writing or japanese-article-writing for those.
```

- [ ] **Step 2: 適用範囲に 1 行足す**

old:
```text
- PR のタイトル、本文、レビュー返信、検証報告は `japanese-pr-writing` に渡す。ここでは扱わない。
```

new:
```text
- PR のタイトル、本文、レビュー返信、検証報告は `japanese-pr-writing` に渡す。ここでは扱わない。
- 社外に公開する記事の本文は `japanese-article-writing` に渡す。記事について依頼者に返す質問や報告は、ここで扱う。
```

- [ ] **Step 3: 新しい節を足す**

`## 用語、強調、図の使いどころ` の直前に、次の節を入れる。

```markdown
## 段落と文を組む

- 段落は 1 トピックにし、冒頭にその要点を 1 文で置く。「以下で説明します」のような予告だけの文は要点にならない。
- 文頭には前の文や見出しに出た語を置き、新しい情報は文末に回す。主語と態は、この流れで選ぶ。
- 並列する項目や段落は、同じ構成、同じ表現にそろえる。言い換えて変化をつけない。
- 1 文に 1 ポイントを書く。「て、」「り、」「し、」「が、」で別々のポイントをつないでいたら文を切る。順接の「が、」は使わない。手順の羅列は例外。
- 「することができる」「を行う」「と思われる」は、「できる」、動詞、根拠つきの断定に縮める。二重否定は肯定文に直す。
```

- [ ] **Step 4: 送る前の確認に 1 行足す**

old:
```text
- 括弧補足のない初出の専門用語がないか。
```

new:
```text
- 括弧補足のない初出の専門用語がないか。
- 段落の第 1 文だけを読んで要点が通るか。「て、」「り、」「し、」「が、」で別々のポイントをつないでいないか。
```

- [ ] **Step 5: 調査メモを更新する**

`references/research.md` の「確認した一次資料」の表の最終行の後に、次の行を足す。

```markdown
| 倉島保美『改訂新版 書く技術・伝える技術』（あさ出版） | 2019 年。理論編の法則 2〜7 | 段落の要点、既知から未知、並列、1 文 1 ポイント、簡潔さの根拠。記事向けの全体は `japanese-article-writing` の調査メモに記録した。 |
```

`## 8. このスキルで定めた判断` を `## 9. このスキルで定めた判断` に改め、その直前に次の節を入れる。

```markdown
## 8. 段落と文の組み方

倉島保美『改訂新版 書く技術・伝える技術』は、読み手が先の展開を予測でき、その予測が当たると速く理解できる、という考え方から 7 つの法則を示しています。
このスキルには、返答とドキュメントの段落と文に効く法則 2〜7 を入れました。
段落は 1 トピックにして冒頭に要点を置くこと、文頭に既出の情報を置くこと、並列は同じ構成と表現にすること、別々のポイントを「て、」「り、」「し、」「が、」でつながないこと、冗長な文末と二重否定を直すことです。
法則 1（冒頭に総論）は、1 節の「結論と結果を先に置く」と同じ趣旨なので、新しい規則は足していません。
書籍は、能動態を一律に勧める助言は文章の流れを壊すことがあるとして、態は既知から未知の流れで決めるとしています。このスキルもそれに従います。
```

`## 9. このスキルで定めた判断` の表の最終行の後に、次の行を足す。

```markdown
| 段落と文の規則を 1 節にまとめる | 毎回読み込まれるスキルなので、法則 2〜7 を 5 行に絞った。記事向けの詳しい手順は `japanese-article-writing` に置く。 |
```

- [ ] **Step 6: 書き換え例を足す**

`references/examples.md` の `## 9. 適用しない例` を `## 10. 適用しない例` に改め、その直前に次の節を入れる。

```markdown
## 9. 段落の要点と文の流れ

修正前：

> 以下に調査結果を述べます。変換サーバーのログを確認し、エラーは出ていなかったが、待ち時間は先週の 3 倍になっていて、原因はワーカーの数が 4 から 2 に減っていたことでした。ワーカー数の設定は、9 月 30 日のデプロイで変わっていました。

修正後：

> 画像変換の待ち時間が先週の 3 倍になった原因は、ワーカーの数が 4 から 2 に減っていたことです。ワーカーの数は、9 月 30 日のデプロイで設定が変わっていました。変換サーバーのログに、エラーは出ていません。

判断：予告だけの冒頭文を、要点（原因）を書いた文に替えた。「確認し、」「いなかったが、」「なっていて、」でつながっていた 3 つのポイントを分け、2 文目は前の文の「ワーカーの数」で始めた。
```

あわせて、`## 10. 適用しない例` の箇条書きの先頭に次の行を足す。

```markdown
- 社外に公開する記事の本文。`japanese-article-writing` に渡す。
```

- [ ] **Step 7: README の適用範囲を更新する**

`README.md` の次を置き換える。

old:
```text
- 対象外：PR のタイトル・本文・レビュー返信（`japanese-pr-writing` が担当）、日本語以外の文章、コードコメントやコミットメッセージの文体。
```

new:
```text
- 対象外：PR のタイトル・本文・レビュー返信（`japanese-pr-writing` が担当）、社外に公開する記事の本文（`japanese-article-writing` が担当）、日本語以外の文章、コードコメントやコミットメッセージの文体。
```

- [ ] **Step 8: 検証する**

```bash
make validate
```

Expected: `ok: development structure is valid (11 skill(s))`

- [ ] **Step 9: 変更後を 3 回実行して比べる**

Task 1 と同じ雛形で、`{SKILL_PATH}` をリポジトリの `plugins/aburasashi/skills/japanese-native-writing/SKILL.md`、`{OUT_PATH}` を `$SCRATCH/eval/after/native-1.md`〜`native-3.md` にして 3 回実行する。
S1〜S5 と退行の確認を採点し、`$SCRATCH/eval/after/scores.md` に変更前と並べて記録する。

Expected: 足した規則の項目で、変更後の合計が変更前より少ない（S1 は割合が高い）。退行の確認は 3 回とも合格。
満たさなければ Task 3 の Step 4 と同じ手順（原因の特定、最小の修正、2 巡まで）で直す。

- [ ] **Step 10: コミットする**

```bash
git add plugins/aburasashi/skills/japanese-native-writing
git commit -m "feat: add paragraph and sentence rules to japanese-native-writing

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018nmrC51XkzRnXf2FCjXnf7"
```

---

### Task 5: `japanese-pr-writing` に段落と文の規則を足す

**Files:**
- Modify: `plugins/aburasashi/skills/japanese-pr-writing/SKILL.md`（frontmatter の description、「PR の説明として組み立てる」、「自然な日本語に整える」）
- Modify: `plugins/aburasashi/skills/japanese-pr-writing/references/research.md`

**Interfaces:**
- Consumes: Task 1 の `before/scores.md`（外す規則の判断）。

Task 1 の Step 8 で外した項目があれば、以下の該当行を入れない。

- [ ] **Step 1: description を更新する**

old:
```text
Do not use for general Japanese prose, code review alone, or GitHub publishing operations alone.
```

new:
```text
Do not use for general Japanese prose, articles for outside readers, code review alone, or GitHub publishing operations alone.
```

- [ ] **Step 2: PR の説明の組み立てに 1 行足す**

old:
```text
- 本文は最終的な変更内容を説明する。作業順の報告やファイル一覧の転記に終始しない。
```

new:
```text
- 本文は最終的な変更内容を説明する。作業順の報告やファイル一覧の転記に終始しない。
- 段落は 1 トピックにし、冒頭にその段落の要点を置く。
```

- [ ] **Step 3: 文のつながりを補う**

old:
```text
- **文のつながり**：「〜し、〜して、〜が」と論点を連結しすぎない。文を分ける際も、条件・例外・因果関係を対応する文に残す。文字数だけで分割を決めない。
```

new:
```text
- **文のつながり**：「〜し、〜して、〜が」と論点を連結しすぎない。「て、」「り、」「し、」「が、」で別々のポイントをつないでいたら、関係が弱ければ文を切り、強ければ「〜ので」などで関係を示す。順接の「が、」は使わない。文を分ける際も、条件・例外・因果関係を対応する文に残す。文字数だけで分割を決めない。
- **文頭と文末**：文頭には前の文や見出しに出た語を置き、新しい情報は文末に回す。新しいクラス名や設定名で文を始めず、既出の語で受けてから出す。
```

- [ ] **Step 4: 動作の明示を補う**

old:
```text
- **動作の明示**：「確認を実施する」は「確認する」のように簡潔にできる。「対応」「整備」「担保」などは、何をするか不明な場合に具体化する。単語そのものを禁止しない。
```

new:
```text
- **動作の明示**：「確認を実施する」は「確認する」、「〜することができる」は「〜できる」のように簡潔にできる。「対応」「整備」「担保」などは、何をするか不明な場合に具体化する。単語そのものを禁止しない。
```

- [ ] **Step 5: 態と否定を改める**

old:
```text
- **態と否定**：主体が分かりにくい受け身や、読みにくい否定表現を見直す。受け身が自然な場合は残し、許可・禁止・必要性の違いを失う肯定形への置換はしない。
```

new:
```text
- **態と否定**：主体が分かりにくい受け身は見直す。既出の語を主語に保つための受け身は残す。二重否定は、意味を変えない形で肯定文に直す（「設定しない限り有効にならない」は「有効にするには設定が必要」）。許可・禁止・必要性の違いを失う肯定形への置換はしない。
```

- [ ] **Step 6: 調査メモを更新する**

`references/research.md` の「確認した一次資料」の表の最終行の後に、次の行を足す。

```markdown
| 倉島保美『改訂新版 書く技術・伝える技術』（あさ出版） | 2019 年。理論編の法則 3、4、6、7 | 段落の要点、文頭と文末の情報の順、1 文 1 ポイント、冗長な文末と二重否定の根拠。 |
```

`## 4. PR 向けに定めた編集上の判断` を `## 5. PR 向けに定めた編集上の判断` に改め、その直前に次の節を入れる。

```markdown
## 4. 文の流れと 1 文 1 ポイント

倉島保美『改訂新版 書く技術・伝える技術』は、文頭に既出の情報、文末に新しい情報を置くと、読み手は前の文とのつながりをすぐに理解できると説明しています。
PR 本文では、新しいクラス名や設定名が文頭にいきなり出ると、レビュアーは何の話かを文末まで読んで判断することになります。
書籍は、別々のポイントを「て、」「り、」「し、」「が、」で 1 文に並べると、どれも同じ重みになって要点がぼやけるとしています。
特に「が、」は順接と逆接のどちらにも使えるので、文末まで読まないと意味が決まりません。
このスキルでは、これらを推敲の観点に足しました。
書籍は能動態を一律に勧める助言にも注意しています。そこで、主体が分からない受け身だけを見直し、既出の語を主語に保つための受け身は残すことにしました。
```

`## 5. PR 向けに定めた編集上の判断` の表の最終行の後に、次の行を足す。

```markdown
| 既出の語を主語に保つ受け身は残す | 能動態に直すと、文頭に新しい情報が来て文の流れが崩れることがあるため。 |
```

- [ ] **Step 7: 検証する**

```bash
make validate
```

Expected: `ok: development structure is valid (11 skill(s))`

- [ ] **Step 8: 変更後を 3 回実行して比べる**

Task 1 と同じ雛形で、`{SKILL_PATH}` をリポジトリの `plugins/aburasashi/skills/japanese-pr-writing/SKILL.md`、`{OUT_PATH}` を `$SCRATCH/eval/after/pr-1.md`〜`pr-3.md` にして 3 回実行する。
P1〜P9 の残り数、S1〜S5、退行の確認を採点し、`$SCRATCH/eval/after/scores.md` に変更前と並べて記録する。

Expected: P1〜P9 の残り数の合計が変更前より少ない。退行の確認は 3 回とも合格。
満たさなければ Task 3 の Step 4 と同じ手順で直す。

- [ ] **Step 9: コミットする**

```bash
git add plugins/aburasashi/skills/japanese-pr-writing
git commit -m "feat: add sentence-flow rules to japanese-pr-writing

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018nmrC51XkzRnXf2FCjXnf7"
```

---

### Task 6: トリガー表、スキル一覧、変更履歴

**Files:**
- Modify: `plugins/aburasashi/skills/using-aburasashi/SKILL.md`（Trigger cues の表）
- Modify: `plugins/aburasashi/skills/README.md`（ツリーと Available skills）
- Modify: `README.md`、`README.ja.md`（スキル一覧）
- Modify: `CHANGELOG.md`（Unreleased）

- [ ] **Step 1: トリガー表に 1 行足す**

`japanese-native-writing` の行の直後に、次の行を入れる。

```markdown
| A Japanese article for outside readers: owned media, a company or tech blog post, a how-to, explainer, or comparison, a release announcement; "記事", "ブログ", "オウンドメディア", "お知らせ"; a Japanese draft that reads as AI-written, padded, or generic | `japanese-article-writing` |
```

- [ ] **Step 2: スキルカタログを更新する**

`plugins/aburasashi/skills/README.md` のツリーで、`japanese-native-writing/` のブロックの直後に次を入れる。

```text
├── japanese-article-writing/
│   ├── SKILL.md
│   ├── README.md
│   ├── agents/
│   └── references/
```

Available skills で、Japanese Native Writing の項目の直後に次を入れる。

```markdown
- [Japanese Article Writing](japanese-article-writing/README.md) writes
  Japanese articles for outside readers, such as tech blog posts, how-to and
  explainer articles, and release announcements: a lead that states the
  conclusion, paragraphs that open with their point, first-hand facts at the
  center, and rewrites of common AI-sounding patterns. When first-hand facts
  are missing, it asks for them or marks where they belong instead of padding.
```

- [ ] **Step 3: README.md を更新する**

Japanese Native Writing の項目の直後に次を入れる。

```markdown
- [Japanese Article Writing](plugins/aburasashi/skills/japanese-article-writing/README.md)
  writes Japanese articles for outside readers (tech blogs, how-to and explainer
  articles, release announcements) with a conclusion-first lead, paragraphs that
  open with their point, and first-hand facts at the center; it asks for missing
  first-hand facts instead of padding with generic content.
```

- [ ] **Step 4: README.ja.md を更新する**

Japanese Native Writing の項目の直後に次を入れる。

```markdown
- [Japanese Article Writing](plugins/aburasashi/skills/japanese-article-writing/README.md)
  は、技術ブログ、ノウハウ・解説記事、お知らせなど、社外に公開する日本語記事を、結論を先に置いたリード、
  要点から始まる段落、一次情報を中心にした文章にします。一次情報が足りなければ、一般論で埋めずに質問します。
```

- [ ] **Step 5: CHANGELOG を更新する**

`## [Unreleased]` の直後に次を入れる。

```markdown

### Added

- Japanese Article Writing skill for Japanese articles published to outside
  readers: conclusion-first leads, paragraphs that open with their point,
  first-hand facts at the center, article-type templates, and rewrites of
  common AI-sounding patterns. It asks for missing first-hand facts or marks
  where they belong instead of padding to a word count.

### Changed

- Add paragraph and sentence-flow rules (point-first paragraphs, known-to-new
  order, parallel structure, one point per sentence, concise endings) to
  Japanese Native Writing and Japanese PR Writing, and route article bodies to
  Japanese Article Writing.
```

- [ ] **Step 6: 検証する**

```bash
make validate
make validate-claude
```

Expected: `ok: development structure is valid (11 skill(s))`。`claude plugin validate --strict` が 2 回とも成功する。

- [ ] **Step 7: コミットする**

```bash
git add plugins/aburasashi/skills/using-aburasashi/SKILL.md plugins/aburasashi/skills/README.md README.md README.ja.md CHANGELOG.md
git commit -m "docs: register japanese-article-writing in catalogs and changelog

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_018nmrC51XkzRnXf2FCjXnf7"
```

---

### Task 7: 仕上げと PR

**Files:**
- なし（確認、push、PR 作成）

- [ ] **Step 1: ブランチ全体を確認する**

```bash
git diff main --stat
make validate
```

差分を通読し、次を確かめる。書籍の文の転記がない。絶対パスや個人情報がない。3 スキルの間で役割の記述（記事、返答、PR）が矛盾しない。

- [ ] **Step 2: push と PR 作成の可否をユーザーに確認する**

評価結果（Task 1、3、4、5 の採点の要約）を添えて、push と PR 作成に進んでよいかを聞く。返事を待つ。

- [ ] **Step 3: push して PR を作る**

承認後に実行する。PR のタイトルと本文は `japanese-pr-writing` で書き、評価の結果（ベースラインとの比較）を検証報告として載せる。本文の末尾に、system-reminder で指定された attribution 行を付ける。

```bash
git push -u origin feat/japanese-article-writing
gh pr create --base main --title "<japanese-pr-writing で整えたタイトル>" --body-file "$SCRATCH/pr-body.md"
```

Expected: PR の URL が表示される。
