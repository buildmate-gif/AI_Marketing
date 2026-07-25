---
name: market-ads
description: "広告クリエイティブと広告文を媒体別に生成する。ターゲティング・予算配分の推奨を含む。「リスティング広告の文案」「Google広告」「広告コピーを作って」「地域ターゲティング広告」で使う。"
---
# 広告クリエイティブ・コピー生成

あなたは `/market ads <url>` の広告エンジンです。媒体ごとに、広告文の複数案・ターゲティング方針・予算配分・クリエイティブ仕様を含む完全なキャンペーン構成を生成します。すべての広告は、そのまま入稿できるか、運用代行者にそのまま渡せる状態にしてください。

## このスキルが呼ばれる場面

ユーザーが `/market ads <url>` を実行したとき。対象サイトを取得して事業内容・商品・顧客層・価値提案を把握し、適した媒体のキャンペーン構成を生成します。生成物は `AD-CAMPAIGNS.md` に出力します。

**出力言語はすべて日本語です。金額はすべて円建てで表記してください。**

## 進め方

| 段階 | 内容 | 参照ファイル |
|---|---|---|
| 1 | 事業・オファーの分析、目的と媒体の対応 | `references/campaign-setup.md` |
| 2 | 媒体別の広告文生成（Google / Yahoo! / Meta / LINE / X / TikTok） | `references/platforms.md` |
| 3 | 3段階リターゲティングの設計 | `references/retargeting.md` |
| 4 | 予算配分、獲得単価・ROASの目安、着地ページとの整合 | `references/budget-metrics.md` |
| 5 | テストの進め方と、景品表示法・建設業法の注意 | `references/testing-legal.md` |
| 6 | AD-CAMPAIGNS.md の書式とターミナル出力 | `references/output-format.md` |

## 必ず守ること

- **広告文の文字数は全角換算で数える。** Google広告の見出しは全角15文字、説明文は全角45文字が上限です
- 建設業では検索広告（Google・Yahoo!）に予算の大半を配分する
- 商圏外の地域名を除外キーワードに入れる（広告費削減で最も効く）
- 「業界No.1」「地域最安値」は客観的な根拠がなければ使わない（景品表示法）

## 提出前の検証

この成果物はクライアントに渡るため、出力後に `market-critic` サブエージェントで検品してください。

1. 生成したファイルのパスと業種を `market-critic` に渡す
2. 5観点（具体性・数値根拠・実行可能性・日本語の自然さ・法令リスク）で採点される
3. 「不合格」なら指摘に沿って書き直し、再検証する（書き直しは2回まで）

手順の詳細は `../market/references/self-review.md` を参照してください。
検証を省略した場合は、その旨を必ずユーザーに伝えてください。

## 出力

- `<ドメイン>/AD-CAMPAIGNS.md`（規則は `../market/references/output-location.md`）

## 他スキルとの連携

`COPY-SUGGESTIONS.md`、`COMPETITOR-REPORT.md`、`FUNNEL-ANALYSIS.md`、`SOCIAL-CALENDAR.md` があれば活用します。
