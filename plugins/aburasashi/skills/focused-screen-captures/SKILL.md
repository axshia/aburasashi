---
name: focused-screen-captures
description: Use when a document, ticket, pull request description, or review comment refers to a specific place on a real screen, such as a banner, a field, a column, a side panel item, or a button, and the reader would need to find that place. Captures the real screen with fixed viewport conditions, dims everything except the target with a backdrop, outlines the target, places the image after a one-sentence lead, and checks it on the page. Also builds a proposal image by adding the proposed element to the same real screen and capturing it with the same frame, for documents that ask for agreement on a screen change. Triggers include キャプチャを載せて, 提案のイメージ, 変更後の画面のイメージ, スクショを貼って, 画面のどこか分かるように, バックドロップ, フォーカス, 赤枠, and screenshot. Do not use for diagrams of flows or structures (use excalidraw-diagrams), design-to-implementation comparison (use figma-web-parity), or OpenAPI documentation captures (use openapi-redoc-pr-screenshots).
---

# Focused Screen Captures

ドキュメント、チケット、PR 本文、レビューコメントで画面の特定の箇所を指すときに、実際の画面のキャプチャを撮り、対象以外を暗くして（バックドロップ）、対象を枠で囲んで（フォーカス）載せる。
読み手が、文がどの画面のどこを指すかを、画像だけで読み違えずに分かるようにする。
画像の周りの文章は、`japanese-doc-writing`（ドキュメント・チケット）と `japanese-pr-writing`（PR）に従う。このスキルは、撮り方と載せ方を扱う。

## 適用範囲を確かめる

- 対象は、画面の箇所を指す文がある、あとから人が読む文面。
  例：「上部の帯に審査状況を表示します」「サイドパネルの投稿者の欄は〜」「検索フォームの『作成日時』は〜」。
- 対象外：流れや構造の図（`excalidraw-diagrams`）、デザインとの照合（`figma-web-parity`）、OpenAPI のドキュメントのキャプチャ（`openapi-redoc-pr-screenshots`）、ターミナルへの返答。
- 撮る画面を開けないとき（起動できない、ログインできない、データがない）は、撮らずに、何が足りないかを依頼者に伝える。画面を想像で描かない。

## 何を撮るかを決める

- 画面の箇所を指す文ごとに、1 枚を撮る。1 枚で示す対象は、1 つの話題に関わる箇所だけにする（離れた 2 か所でも、同じ話題なら 1 枚に入れてよい）。
- 対象は、文が指す範囲にそろえる。節全体を指す文なら節の枠、項目を指す文なら項目の行を囲む。
  囲む範囲が広すぎると、どこを読めばよいかが伝わらないため。
- 今の画面にまだ存在しないもの（これから追加する欄）は、今の画面としては撮らない。追加する場所を文で書くか、「提案のイメージを作る」に従って、合成のイメージとして載せる。
- 写るアカウントとデータは、開発用のダミーか、載せる先で公開してよいものに限る。

## 撮り方

1. 撮る画面を、ブラウザの自動操作（Playwright、Chrome DevTools Protocol など）で開く。
2. viewport を固定する。幅は 1440px、デバイスピクセル比は 2 を基準にする。
   ウィンドウの大きさを変えるツールは、すでに開いているウィンドウでは効かないことがある。viewport のエミュレーション（Playwright の `setViewportSize`、DevTools の `Emulation.setDeviceMetricsOverride` など）を使い、`innerWidth` が変わったことを確かめる。
3. 撮る範囲は、viewport の高さで決める。
   内側の要素でスクロールする画面（サイドバーを固定した管理画面など）は、ページ全体のスクリーンショットでも下が切れる。対象が収まる高さまで viewport を伸ばすか、内側の要素のスクロール位置を合わせてから撮る。
   画像を後から切り出すツールは、指定によらず中央を基準に切り出すことがある。切り出したら、必ず開いて範囲を確かめる。
4. 開発用のオーバーレイ（デバッグツールのメニュー、プロファイラーの表示など、`position: fixed` の要素）を非表示にする。画面の中身には手を加えない。
5. [`scripts/focus-overlay.js`](scripts/focus-overlay.js) をページで評価し、`window.__focusCapture.apply({ targets: [...] })` でオーバーレイを重ねる。
   対象以外を半透明の黒（既定は `rgba(0,0,0,0.55)`）で暗くし、対象を赤の 3px の角丸の枠で囲む。対象は CSS セレクタか、セレクタと表示テキストの組で指定する。
6. viewport の範囲を撮る。続けて別の対象を撮るときは、`apply` を呼び直す（前のオーバーレイは置き換わる）。
7. 撮り終えたら、`window.__focusCapture.clear()` でオーバーレイを外し、viewport のエミュレーションを解除する。

## 提案のイメージを作る

画面の変更を提案する資料では、今の画面のキャプチャと、同じ画面に変更を加えた合成のイメージを並べる。
読み手が、2 枚を見比べるだけで、何が変わるかを分かるようにするため。

1. 今の画面を、「撮り方」の手順で撮る。
2. 同じページ、同じ viewport のまま、ページの DOM に変更を加える。追加する要素は、画面にある似た部品（既存のラベルやボタン）を複製して、文言と色だけを変える。合成が、実際の部品の見た目から離れないようにするため。
3. 追加した要素に目印の属性（`data-mock` など）を付け、1 と同じ対象を枠で囲んで撮る。
4. 撮り終えたら、追加した要素を消す。サーバーのデータや、リポジトリのコードは変えない。
5. 載せるときは、直前の文に、実際の画面に変更を加えた合成であることと、デザインがまだ決まっていないことを書く（「一覧の表示のイメージは、次の画像の赤枠のとおりです（実際の画面にタグを追加した合成で、デザインは未確定です）。」）。

`scripts/focus-overlay.js` を、ツールが読めない場所（プラグインのキャッシュなど）からは評価できないことがある。そのときは、作業用のディレクトリにコピーしてから評価する。

## 確かめる

撮った画像を開いて、次を確かめる。

- 枠が対象をずれずに囲んでいるか。対象の外の暗い部分に、文が指すものが残っていないか。
- 枠の中の文字が、載せる先の幅に縮小されても読める大きさか。読めなければ、viewport の高さを縮めて対象の周りだけを撮り直す。
- 開発用のオーバーレイや、写してはいけない情報が残っていないか。

## 載せる

- 画像は、画面の箇所を指す文の前に置く。画像の直前に、何を示すかの 1 文を置く（「現在、〇〇は次の画像の赤枠の箇所に表示されています。」）。
  文だけを読んでから画像を探させず、画像を見てから詳細の文を読めるようにするため。
- 画像で分かること（どこに表示されているか）は、文で繰り返さない。文には、画像に写らない結論・理由・時点だけを書く。
- 共有されているドキュメントに載せる前に、画像と差し込む位置を示して確認をもらう。
- Notion などのページ: 画像ブロックはページの直下に置く。箇条書きの子にした画像ブロックは、描画されないことがある。
- GitHub の PR: `gh pr edit --attach` で添付する（手順は `japanese-pr-writing` の動作確認とキャプチャの掲載）。
- 載せたら、ページを開き直して、画像が表示され、枠と文字が読めることを確かめる。

## 出す前の見直し

1. 画面の箇所を指す文のすべてに、画像があるか。
2. 画像だけを見て、どこの話かが分かるか（枠の範囲は文の範囲と合っているか）。
3. 画像の直前に、何を示すかの 1 文があるか。画像と文で、同じことを書いていないか。
4. 写っているデータは、載せる先で公開してよいものか。
5. 合成のイメージに、合成であることと、デザインが未確定であることを書いたか。追加した要素を、ページから消したか。
6. 載せたページで、画像が表示され、文字が読めるか。
