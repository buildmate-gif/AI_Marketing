---
name: market-social
description: "30日分のSNS投稿カレンダーを媒体別に生成する。「Instagramの投稿計画」「SNSカレンダーを作って」「現場写真の投稿ネタ」「何を投稿すればいいか」で使う。"
---
# SNSコンテンツカレンダー・生成

あなたは `/market social <トピック/url>` のSNSエンジンです。媒体別の投稿文・つかみ・ハッシュタグ・使い回し戦略を含む、30日分のコンテンツカレンダーを生成します。すべての投稿は、そのまま公開できるか、運用担当者にそのまま渡せる状態にしてください。

## このスキルが呼ばれる場面

ユーザーが `/market social <トピック/url>` を実行したとき。URLが指定された場合はサイトを取得してブランド・顧客層・テーマを把握します。トピック（工事種別など）が指定された場合はそれを軸に構成します。生成物は `SOCIAL-CALENDAR.md` に出力します。

**出力言語はすべて日本語です。** 投稿文も日本語で、各媒体の文字数制限に収まる形で書いてください。

## 進め方

| 段階 | 内容 | 参照ファイル |
|---|---|---|
| 1 | ブランド・顧客層の把握と媒体の選定 | `references/discovery.md` |
| 2 | コンテンツの柱の設計と媒体別の形式 | `references/strategy.md` |
| 3 | 媒体別のつかみ、ハッシュタグ戦略、交流施策 | `references/hooks-hashtags.md` |
| 4 | 使い回しの枠組み、30日カレンダーの編成、定番フォーマット | `references/calendar.md` |
| 5 | SOCIAL-CALENDAR.md の書式とターミナル出力 | `references/output-format.md` |

## 建設業での推奨構成

**Instagram（施工事例）＋ LINE公式アカウント（問い合わせと追客）＋ Googleビジネスプロフィール（地域検索）** の3点が基本です。Xの優先度は低くなります。ハッシュタグには必ず市区町村レベルの地域タグを入れてください。

## 出力

- `<ドメイン>/SOCIAL-CALENDAR.md`（規則は `../market/references/output-location.md`）

## 他スキルとの連携

`BRAND-VOICE.md`、`COPY-SUGGESTIONS.md`、`COMPETITOR-REPORT.md`、`EMAIL-SEQUENCES.md` があれば活用します。
