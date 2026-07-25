---
name: market-report-pdf
description: "分析結果を日本語PDFレポートとして出力する。スコアゲージ・グラフ・施策一覧を含む。「PDFでレポートを作って」「印刷して持参できる資料」「クライアントに渡すPDF」で使う。"
---
# PDFマーケティングレポート生成

## このスキルの目的

Pythonスクリプト `$MARKET_SCRIPTS/generate_pdf_jp.py` を使い、体裁の整った日本語PDFレポートを生成します。利用可能な監査・分析データを集約し、所定のJSON形式に整えてスクリプトを呼び出し、スコアゲージ・棒グラフ・課題一覧・優先順位別アクションプランを含むPDFを出力します。

**出力言語はすべて日本語です。金額はすべて円建てで表記してください。**

## 使う場面

- Markdownではなく、PDF形式のレポートが欲しいとき
- クライアントへの提出資料を準備しているとき
- 「きれいなレポート」「そのまま渡せる資料」「PDFのレポート」と依頼されたとき
- グラフとスコアが入った視覚的なレポートが欲しいとき
- `/market report-pdf` または `/market report-pdf <ドメイン>` が実行されたとき

## PDFとMarkdownの使い分け

| 形式 | 向いている用途 | 長所 | 短所 |
|---|---|---|---|
| **PDF** | クライアントへの提出、メール添付、営業資料、印刷して持参 | 見栄えが良い、体裁が崩れない、グラフが入る、印刷できる | 編集しにくい、Pythonスクリプトが必要 |
| **Markdown** | 社内利用、下書き、繰り返しの修正、バージョン管理 | 編集が容易、どのエディタでも読める、差分管理しやすい | 見栄えは劣る、グラフがない |

**判断の目安：** クライアントや見込み客に渡すならPDF。社内利用や修正を重ねるならMarkdown。建設業の経営者には「印刷して手元で読める資料」が好まれるため、商談にはPDFを推奨します。

## 進め方

| 段階 | 内容 | 参照ファイル |
|---|---|---|
| 1 | データ収集、JSONの組み立て、スクリプト実行の全7ステップ | `references/procedure.md` |
| 2 | PDFの4ページ構成、配色、トラブルシューティング | `references/pdf-spec.md` |

## スクリプトの場所

同梱のPythonスクリプトは、導入方法によって置き場所が変わります。実行前に次の2行でパスを解決してください。

```bash
MARKET_SCRIPTS="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/market/scripts}"
[ -d "$MARKET_SCRIPTS" ] || MARKET_SCRIPTS="$HOME/.claude/skills/market/scripts"
```

```bash
python3 "$MARKET_SCRIPTS/generate_pdf_jp.py" /tmp/report_data.json "MARKETING-REPORT-<ドメイン>.pdf"
```

## 必ず守ること

- JSONは**UTF-8**で書き出す
- `brand_name` を指定すると表紙に「〇〇 御中」が入る。クライアント提出時は必須
- 重要度は `致命的 / 重大 / 中程度 / 軽微`（英語の Critical/High/Medium/Low も自動変換されます）
- 生成されるのは**全4ページ**です。競合比較ページと採点方法ページは未対応のため、必要な場合は `/market report` を併用してください

## 出力

- `MARKETING-REPORT-<ドメイン>.pdf`（カレントディレクトリ）
