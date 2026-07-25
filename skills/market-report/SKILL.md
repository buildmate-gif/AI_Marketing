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

## 出力

- `MARKETING-REPORT.md`（カレントディレクトリ）
- PDF形式が必要な場合は `/market report-pdf` を使ってください
