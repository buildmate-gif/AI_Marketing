---
name: market-seo
description: "SEO監査。オンページSEO・E-E-A-T・キーワード・テクニカルSEOを診断し改善案を出す。「SEO診断して」「検索順位を上げたい」「地域名＋工種のキーワード対策」「Googleで上位表示したい」で使う。"
---
# SEOコンテンツ監査

## このスキルの目的

Webページ・サイトの網羅的なSEO監査を行います。オンページSEO、コンテンツ品質（E-E-A-T）、キーワード分析、テクニカルSEO、コンテンツ戦略を対象とし、`$MARKET_SCRIPTS/analyze_page.py` による自動分析と、専門的な手動レビューを組み合わせて、実行可能なSEO監査書を作成します。

**出力言語はすべて日本語です。文字数は全角換算で判定してください。**

## 使う場面

- URLを渡されてSEO分析・監査・改善提案を求められたとき
- 検索からの流入を増やしたいとき
- オンページSEO、メタタグ、コンテンツ品質、テクニカルSEOについて聞かれたとき
- コンテンツの不足領域や記事戦略の提案を求められたとき
- `/market seo <url>` または `/market seo` が実行されたとき

## 進め方

| 段階 | 内容 | 参照ファイル |
|---|---|---|
| 1 | 自動分析からコンテンツ戦略までの全12ステップ | `references/procedure.md` |
| 2 | SEO-AUDIT.md の書式 | `references/output-format.md` |

## スクリプトの場所

同梱のPythonスクリプトは、導入方法によって置き場所が変わります。実行前に次の2行でパスを解決してください。

```bash
MARKET_SCRIPTS="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/market/scripts}"
[ -d "$MARKET_SCRIPTS" ] || MARKET_SCRIPTS="$HOME/.claude/skills/market/scripts"
```

```bash
python3 "$MARKET_SCRIPTS/analyze_page.py" <url>
```

## 日本語で必ず守る文字数

- **タイトルタグ：全角28〜32文字**（英語基準の60文字では検索結果で切れます）
- **メタディスクリプション：全角80〜120文字**（スマホでは冒頭の全角50文字程度しか表示されません）

## 建設業での優先順位

「地域名 ＋ 工種」のキーワードが最も成約に近く、競合も限られます。またサイトのSEOより、**Googleビジネスプロフィールの最適化の方が短期的な効果が大きい**場合があります。優先順位の判断時に必ず考慮してください。

## 出力

- `SEO-AUDIT.md`（カレントディレクトリ）

## 他スキルとの連携

`MARKETING-AUDIT.md`、`LANDING-CRO.md` があれば突き合わせて判断します。
