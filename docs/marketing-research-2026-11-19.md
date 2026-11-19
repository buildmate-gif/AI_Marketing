# 日本の集客・販促ツール改修の調査記録

調査基準日は日本時間2026年11月19日。工務店の「地域で見つけてもらう → 見学・見積相談 → 商談・受注 → 翌月の報告」を代表業務とし、他業種では資料請求・購入などに置き換える。以下の製品仕様は公開されている一次資料で確認した。管理画面や顧客の実績を要する項目には、受け取る資料と集計条件を定めた。日付を表示しないヘルプの確認日は上記基準日である。

## 確認結果と採用仕様

| 領域 | 一次資料で確認した内容 | ツールへの反映と、現場での検証方法 |
|---|---|---|
| Google検索・AI検索 | Googleは独自の経験・役立つ具体例・クロール可能性等を案内。6月3日発表の生成AI専用レポートは8月31日に全世界への展開完了。SearchとDiscoverの生成AI面の表示回数をページ・国の軸で確認でき、全体レポートにも含まれる。[最適化ガイド](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)・[レポートの範囲と展開日](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports) | 公開ページの観察と所有者のSearch Console実績を別々に出す。施工事例のオリジナル写真、工期・商圏・施工判断の具体性を対象URLごとに確認。専用表示回数を全体に足し戻さず、AI面だけのクリックや成約は推計しない。 |
| 検索語の計測 | 11月16日にSearch Analytics APIのブランド分類、複数国・端末のフィルターなどが発表された。ブランド分類は対象プロパティ限定で、対象外では行が返らない。[Google発表](https://developers.google.com/search/blog/2026/11/search-analytics-api-update) | 実績ファイルがある案件で指名／非指名の増減を同一期間・国・端末条件で比較する。無分類・データなしを区別する。APIの接続は将来の自動化候補。 |
| 検索結果の見え方 | タイトル・スニペットはページ内容や検索・表示条件に応じて生成される。GoogleのFAQリッチリザルトは2026年5月に終了。[タイトル](https://developers.google.com/search/docs/appearance/title-link)・[スニペット](https://developers.google.com/search/docs/appearance/snippet)・[変更履歴](https://developers.google.com/search/updates) | 固定文字数による不合格を廃止。顧客にとって有用な質問と回答は残し、FAQ用マークアップの欠落を改善点に数えない。 |
| 地域集客 | 地域検索の主因には関連性・距離・知名度がある。ビジネスプロフィールの通話数は通話ボタンのクリック数で、実際の通話・相談には別途記録が必要。[ローカル順位](https://support.google.com/business/answer/7091?hl=ja)・[パフォーマンス](https://support.google.com/business/answer/9918094?hl=ja) | 地図を見る地点・日時・語句・端末と、どの結果面を見たかを記録。電話ボタンのクリックと電話経由の相談件数に別々の欄を使う。地点・地図結果を確認できない検索の要約では地図順位は未取得。 |
| 国内広告 | 4月に広告基盤が統合され、10月26日に旧LINE広告の日本への配信が終了。統合後のディスプレイ広告にはトークリストと別に友だちタブの掲載面もある。[統合](https://www.lycbiz.com/jp/news/20260218/)・[国内配信終了](https://www.lycbiz.com/jp/news/line-ads/20261026/)・[掲載面と形式](https://www.lycbiz.com/jp/news/ly-ads/20260629/) | 新規広告案をLINEヤフー広告の検索広告・ディスプレイ広告に分け、旧LINE広告と終了したVOOMへの入稿例を更新。媒体別の想定単価表を、実績と許容問い合わせ単価に基づく試算に変更。 |
| 広告レポートの今後 | 11月17日にLINEヤフーはコンバージョン経路、アトリビューションモデル比較、横断リーチの各レポートの提供終了を告知。実施予定は2027年1月13日。[告知と予定日](https://www.lycbiz.com/jp/news/ly-ads/20261117/) | 利用中の案件で、次回の媒体仕様点検の対象とする。発表時点と終了予定日を併記する。 |
| SNS・LINE | LINE公式アカウントの配信結果にはクリックユーザー等があり、ステップ配信の到達率には定義された分母がある。Instagramでは利用条件に応じてリーチ・反応などの指標を取得できる。[LINE配信分析](https://www.lycbiz.com/jp/manual/OfficialAccountManager/insight_message/)・[ステップ配信](https://www.lycbiz.com/jp/manual/OfficialAccountManager/insight-stepmessage/)・[Instagram Insights](https://developers.facebook.com/docs/graph-api/reference/shadow-ig-user/insights/) | 工務店ならInstagramの施工事例に見学予約の導線を用意し、LINEの案内からのクリック人数と予約台帳の完了人数を別々に記録する。配信数・人数・件数の単位を記す。管理データなしは未計測。 |
| 計測と商談 | GA4では問い合わせ送信をgenerate_leadとして扱え、見込み客の段階別イベントも定義される。Google広告の拡張コンバージョン設定は4月から統合。6月15日からオフライン成果のアップロード経路にData Manager APIへの移行条件がある。[GA4イベント](https://support.google.com/analytics/answer/9267735?hl=ja)・[キーイベント設定例](https://support.google.com/analytics/answer/12966437?hl=ja)・[Google広告の変更](https://support.google.com/google-ads/answer/16884284) | フォーム送信・有効商談・受注を別イベントとして扱う。二重計上と媒体の集計期間を確認。初版は担当者が共有した集計を利用し、オフライン成果の連携は案件の設定・契約・同意の条件を確認して別途設計する。 |
| メール追客 | 広告宣伝メールは原則オプトイン。Gmailは個人用アドレス宛の送信に要件を設け、大量送信者のマーケティングメール等では認証とワンクリック解除用ヘッダーなどを求める。[消費者庁](https://www.caa.go.jp/policies/policy/consumer_transaction/specifed_email/pdf/specifed_email_180709_0001.pdf)・[Gmailガイドライン](https://support.google.com/mail/answer/81126?hl=ja) | 受付確認と継続販促の目的を分ける。予約済み・停止希望・商談移行時の配信終了条件を設計し、予約率の分母・集計元・期間を明示する。 |

## 国内外の競合を同じ仕事で比較

比較課題は「サイトの改善点を選び、顧客に修正理由を説明し、次回に変化を報告する」。ここでは製品提供者が公表した手順・成果物を比較した。操作時間、正答率、有料契約で得られるデータ量は未実測である。

| 製品 | 課題に使える公開機能 | 自社版の設計に取り込む点 |
|---|---|---|
| ミエルカSEO（国内） | 2026年4月1日発表のAIリライトβ版は、対象URL・キーワードを指定し、競合上位コンテンツと比較して改善を提案する。製品ページには順位比較やPPTレポートも掲載されている。[リライトの手順](https://mieru-ca.com/blog/ai_rewrite/)・[製品機能](https://mieru-ca.com/) | 改善策に「どのURLを、何を根拠に、どのように直すか」を残す。自社側で取得できた競合ページと対象顧客の検討課題を結び付ける。 |
| Semrush（海外） | Site Auditでテーマ別に問題を整理し、Compare Crawlsでは2回のクロール間で問題・Site Healthの変化を比較して書き出せる。[監査機能](https://www.semrush.com/features/site-audit/)・[比較結果の出力](https://www.semrush.com/kb/905-exporting-site-audit) | 初回の対象と条件を保存して、翌月に修正箇所・残課題・実績を追う。見かけのスコア改善を受注効果と混同しない。 |

この版では、日本語で顧客に説明する支援担当者が、公開サイトで得た証拠と受領した集計値を一つの改善サイクルにまとめる業務を優先する。競合の大規模クロールや専有データとの機能数比較は、製品の順位を判定する材料にはならない。

## 次回の再評価

- 媒体の配信面・入稿要件、検索のレポート定義、APIの廃止予定を更新する際は、公式発表の公開日・提供開始日・対象国・対象アカウントを記録する。更新予定と提供完了を区別する。
- 同じ工務店と別業種の公開ページ、同一時点の月別集計、同じ顧客説明課題を用意し、根拠を照合できた割合、追加調査なしに着手できた割合、提出までの分数を記録する。有料製品の比較実行には、対象契約の利用者が実際に操作した測定値を使う。
- 2027年1月13日予定のLINEヤフー広告レポート変更は次回検証対象に入れる。運用中の案件に知らせる際は、最新の実施状況を上記公式告知で確認する。
