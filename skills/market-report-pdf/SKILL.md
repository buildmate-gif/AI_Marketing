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

## 2つの生成方式

同じJSONから、2つの方式でPDFを作れます。**特に理由がなければHTML版を使ってください。**

| 方式 | スクリプト | 構成 | 見た目 | 必要なもの |
|---|---|---|---|---|
| **HTML版（推奨）** | `generate_report_html.py` | 表紙・スコア内訳・主要課題・アクションプラン・**競合比較**・**採点方法** | 書体と配色を整えたレイアウト | Chrome（PDF変換時） |
| reportlab版 | `generate_pdf_jp.py` | 表紙・スコア内訳・主要課題・アクションプランの4ページ | 簡素 | reportlab |

**HTML版でのみ、競合比較ページと採点方法ページが出力されます。** クライアント提出用は必ずHTML版を使ってください。

### HTML版（推奨）

```bash
# HTMLとPDFを両方生成
python3 "$MARKET_SCRIPTS/generate_report_html.py" /tmp/report_data.json \
  "MARKETING-REPORT-<ドメイン>.html" --pdf "MARKETING-REPORT-<ドメイン>.pdf"
```

Chrome が見つからない環境では、HTMLだけ生成されます。その場合はブラウザで開き「印刷 → PDFとして保存」で変換するようユーザーに案内してください。

競合比較ページを出すには、JSONに `competitors` を含めます。

```json
"competitors": [
  {"name": "△△塗装工業", "positioning": "地域最大手", "pricing": "90〜160万円",
   "social_proof": "施工事例80件", "content": "週2回更新",
   "reviews": "4.5（86件）", "map_rank": "1位"}
]
```

省略した場合、競合比較ページは「未取得」と表示されます。

### reportlab版

```bash
python3 "$MARKET_SCRIPTS/generate_pdf_jp.py" /tmp/report_data.json "MARKETING-REPORT-<ドメイン>.pdf"
```

Chrome が使えない環境や、HTML経由を避けたい場合に使います。

## 必ず守ること

- JSONは**UTF-8**で書き出す
- `brand_name` を指定すると表紙に「〇〇 御中」が入る。クライアント提出時は必須
- 重要度は `致命的 / 重大 / 中程度 / 軽微`（英語の Critical/High/Medium/Low も自動変換されます）
- HTML版のPDFは埋め込みフォントを含むため2MB前後になります。メール添付時は容量に注意してください

## 提出前の検証

この成果物はクライアントに渡るため、出力後に `market-critic` サブエージェントで検品してください。

1. 生成したファイルのパスと業種を `market-critic` に渡す
2. 5観点（具体性・数値根拠・実行可能性・日本語の自然さ・法令リスク）で採点される
3. 「不合格」なら指摘に沿って書き直し、再検証する（書き直しは2回まで）

手順の詳細は `../market/references/self-review.md` を参照してください。
検証を省略した場合は、その旨を必ずユーザーに伝えてください。

## 出力

- `MARKETING-REPORT-<ドメイン>.pdf`（カレントディレクトリ）
