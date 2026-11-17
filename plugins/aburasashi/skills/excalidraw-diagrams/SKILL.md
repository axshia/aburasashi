---
name: excalidraw-diagrams
description: Use when a document, ticket, pull request description, inline review comment, or review reply would be clearer with a diagram, such as a flow across people, screens, or systems, a problem that appears over time, a normal path with a failure fallback, or a before-and-after difference, and when an existing diagram must be revised. Also use when a chat reply reports how something currently works across several tables, screens, or systems, to offer diagrams on a local HTML page opened in the browser. Draws the diagram as an Excalidraw scene from a generator script, renders it to PNG, checks it, and places it. Triggers include 図解して, 図にして, 図を入れて, フロー図, 構成図, and diagram. Do not draw inside chat replies in a terminal, and do not use for comparisons a table can carry, or screenshots of real screens; use focused-screen-captures for real screens.
---

# Excalidraw Diagrams

ドキュメント、チケット、PR 本文、インラインコメントに載せる図を、Excalidraw で描いて PNG にする。
読み手が、図だけで「誰が・何をすると・どうなるか」を追えるようにする。
図の周りの文章は、`japanese-doc-writing`（ドキュメント・チケット）と `japanese-pr-writing`（PR）に従う。このスキルは、図の中身と作り方を扱う。

## 適用範囲を確かめる

- 対象は、あとから人が見る図（設計書、調査結果、チケット、PR 本文、インラインコメント、レビュー返信）。
- ターミナルへの返答では画像を表示できないので、`japanese-native-writing` のテキストのフロー図を使う。
- 現状調査（コード、スキーマ、チケットを読んで今の作りを説明する）で、複数のテーブル・画面・システムにまたがる構造や流れを返答で報告したときは、返答の末尾で「Excalidraw の図にして、ブラウザで開けるページで図解しますか？」と 1 回だけ提案する。頼まれる前に描き始めず、ユーザーが図を頼むまで文章の説明を重ねない。
  承諾されたら、見出しごとに 1 枚の図を置いたローカルの HTML ページ（Notion のページに似せた体裁など）を作り、ローカルの HTTP サーバーで配信してブラウザで開く。ページの文章は `japanese-doc-writing` に従う。
- 同じ観点の短い値の比較は表、実際の画面はスクリーンショットにする。図にしない。実際の画面の箇所を示すときは `focused-screen-captures` を使う。

## 図にするかを決める

- 図にする: 複数の人・画面・システムをまたぐ流れ、時間がたつと起きる問題、通常の流れと失敗したときの流れ、変更の前後の差。
  文章だけだと、読み手が頭の中で図を組み立てる必要がある場面。
- 図にしない: 1 本道の手順（番号付きのリストにする）、1 文で言えること。
- 1 枚の図で伝えることは 1 つにする。本文の見出しごとに 1 枚を置く。

## 型を選ぶ

伝えたいことに合わせて、次の型から選ぶ。描き方の詳細は [図の型](references/patterns.md) にある。

1. **現状のシナリオ**: 1 行に 1 つの操作で、「誰が / どの画面で / 何をすると / どうなるか」の列に並べる。テーブルやクラスの構造の図にしない。読み手が最初に知りたいのは、データの形ではなく、何が起きるかのため。
2. **問題**: 問題が起きない場面と、起きる場面を上下に並べ、右端に結果を置く（起きない場面は「問題なし」、起きる場面は何が困るか）。差は 1 か所だけにする。
3. **時系列の処理**: 出来事の箱を左から右へ並べる。経過時間は手順の箱にせず、縦の破線の矢印とラベル（「一定期間が過ぎる」）で表す。処理の対象（削除するもの、送るもの）は、矢印で直接指す。
4. **仕組み**: 通常の流れと、失敗したときの流れを、グレーの見出しを付けたレーンに分け、破線で区切る。リトライは、破線で戻る矢印で表す。

## 描き方

- 箱のラベルは、読み手が知っている出来事や操作の名前で書く（「Web の処理」ではなく「キャンセル / 返品」）。
  実装の名前が要るときは、役割の名前のあとに括弧で添える（「再送バッチ（cron の rake タスク）」）。
- ラベルは、現場で使う呼び名と、読み手に起きる結果で書く（「仮の 30 件」ではなく「モックデータ」、「絞り込まない」ではなく「絞り込みできない」）。件数や項目数は、図の主題でなければ書かない。
- 矢印は、要素どうしの関係の形を確かめてから引く。並列の関係（1 つの画面が 2 つの先を参照する）を、1 本の直列の矢印でつながない。関係の形が指示から読み取れないときは、描く前に確かめる。
- 状態や結果は、流れの次の箱にせず、対象に添える吹き出しで描く。吹き出しのしっぽは短くする。
- 前後を比べる図は、同じ位置のラベルを同じ形にそろえる（上下とも「表示対象: 〜」）。形がずれると、読み手は差がどこにあるかを探す。
- 図の言葉を本文とそろえる。同じものを、図と本文で別の言葉で呼ばない（図は「棄却」、本文は「却下」にしない）。
- 図には、流れ・構造と短いラベルだけを描く。方針の文、利点・欠点、注記、図のタイトルは本文に書く。
- 色は役割ごとに決め、同じドキュメントのすべての図でそろえる（人、もう一人の担当、処理、キュー、保存先、問題、スケジューラ、補足）。値は `scripts/excalidraw_scene.py` の `COLORS` にある。
- 人は人のアイコン、画面は小さなウィンドウ、保存先は円柱で描く。箱だけで並べるより、どこで何が起きるかが早く分かる。
- 1 枚の箱は 10 個程度までにする。キャンバスの幅は 1,100px 程度までにし、ラベルは 14px 以上にする。ページの幅に縮小されると、文字が読めなくなるため。
- 手書き風の線（`roughness: 1`）と、Normal のフォント（`fontFamily: 2`）を使う。手書きのフォント（Virgil）は日本語の字形を持たないため使わない。

## 作り方

1. 生成スクリプトを書く。`scripts/excalidraw_scene.py` の `Scene` を import し、座標を決めて部品を置く。例は `assets/example/` にある。
   スクリプトと出力は、作業用の一時ディレクトリ（gitignore 済みのディレクトリなど）に置く。依頼がなければ、リポジトリにコミットしない。
2. `.excalidraw` を書き出す。
3. PNG に変換する。

   ```bash
   uv run --with playwright==1.62.0 python <このスキルのディレクトリ>/scripts/render.py diagram.excalidraw
   ```

   Excalidraw のライブラリを esm.sh から読み込むため、ネットワークへのアクセスが必要になる。
   このコマンドを使えない環境では、`scripts/render.html` と `.excalidraw` を同じディレクトリに置いてローカルの HTTP サーバーで配信し、ブラウザのツールで `render.html?file=diagram.excalidraw` を開く。タイトルが `done` になったら、`window.__png`（PNG の data URL）か、表示された画像を保存する。
4. PNG を開いて確かめる。文字の重なりとはみ出し、矢印の向きと始点・終点、本文との言葉のずれを見る。
5. 載せる。共有されているドキュメントに載せる前に、画像と差し込む位置を示して確認をもらう。
   - Notion などのページ: 画像ブロックにアップロードする。
   - GitHub の PR: `gh pr edit --attach` で添付する（手順は `japanese-pr-writing` の動作確認とキャプチャの掲載）。
6. 載せたページを開き、図が表示され、文字が読める大きさかを確かめる。
7. 直すときは、生成スクリプトを直して再生成し、同じ位置の画像を差し替える。差し替えたあとも 6 を行う。
   `.excalidraw` を残しておくと、人が excalidraw.com で開いて直接直せる。

## 出す前の見直し

1. 図だけで、誰が・何をすると・どうなるかを追えるか。
2. 1 枚の図で伝えることは 1 つか。本文の見出しと図が 1 対 1 か。
3. ラベルは、読み手が知っている名前で、本文と同じ言葉か。前後の図で、同じ位置のラベルの形がそろっているか。
4. 方針・注記・タイトルが図に入っていないか。
5. 載せたページで、文字が読めるか。

図に写すのは、架空のデータか、載せる先で公開してよい情報に限る。
