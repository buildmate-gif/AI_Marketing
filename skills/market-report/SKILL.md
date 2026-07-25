---
name: market-report
description: "既存の分析結果を統合し、マーケティングレポートをMarkdown形式で生成する。「レポートにまとめて」「納品用の報告書」「分析結果を1つの資料にして」で使う。"
---
# マーケティングレポート生成（Markdown形式）

## このスキルの目的

網羅的で体裁の整ったマーケティングレポートをMarkdown形式で生成します。これまでの監査・分析結果を1つの文書に統合し、スコア・所見・改善提案・収益インパクト付きの優先順位別アクションプランを、そのままクライアントに提出できる品質でまとめます。

**出力言語はすべて日本語です。金額はすべて円建てで表記してください。**

## 使う場面

- クライアント向け、または自社向けの総合レポートが欲しいとき
- 複数の監査スキルを実行済みで、それらを統合したいとき
- マーケティングの評価書・スコアカード・分析資料を求められたとき
- `/market report` または `/market report <ドメイン>` が実行されたとき

## 進め方

| 段階 | 内容 | 参照ファイル |
|---|---|---|
| 1 | データ収集、6カテゴリの採点、収益試算、ロードマップの全10ステップ | `references/procedure.md` |
| 2 | MARKETING-REPORT.md の書式 | `references/output-format.md` |

## 採点の配点

Webサイト・コンバージョン25% ／ SEO・自然流入20% ／ コンテンツ15% ／ SNS15% ／ メール15% ／ 有料広告10%

## 先に確認するファイル

`MARKETING-AUDIT.md` / `LANDING-CRO.md` / `SEO-AUDIT.md` / `BRAND-VOICE.md` / `COMPETITOR-REPORT.md` / `FUNNEL-ANALYSIS.md` / `COPY-SUGGESTIONS.md` / `AD-CAMPAIGNS.md` / `SOCIAL-CALENDAR.md` / `EMAIL-SEQUENCES.md`

1件も無い場合は、先に `/market audit <url>` の実行を推奨してください。

## スクリプトの場所

同梱のPythonスクリプトは、導入方法によって置き場所が変わります。実行前に次の2行でパスを解決してください。

```bash
MARKET_SCRIPTS="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/market/scripts}"
[ -d "$MARKET_SCRIPTS" ] || MARKET_SCRIPTS="$HOME/.claude/skills/market/scripts"
```

## 提出前の検証

この成果物はクライアントに渡るため、出力後に `market-critic` サブエージェントで検品してください。

1. 生成したファイルのパスと業種を `market-critic` に渡す
2. 5観点（具体性・数値根拠・実行可能性・日本語の自然さ・法令リスク）で採点される
3. 「不合格」なら指摘に沿って書き直し、再検証する（書き直しは2回まで）

手順の詳細は `../market/references/self-review.md` を参照してください。
検証を省略した場合は、その旨を必ずユーザーに伝えてください。

## 出力

- `MARKETING-REPORT.md`（カレントディレクトリ）
- PDF形式が必要な場合は `/market report-pdf` を使ってください
