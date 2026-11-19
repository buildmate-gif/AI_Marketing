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
[ -d "$MARKET_SCRIPTS" ] || MARKET_SCRIPTS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/market/scripts"
```

```bash
python3 "$MARKET_SCRIPTS/analyze_page.py" <url>
```

## 検索表示とAI検索の確認

検索結果のタイトルと説明は端末幅・クエリなどで変わります。文字数は参考値として記録し、ページとの整合性、固有性、読みやすさを評価してください。[タイトルリンク](https://developers.google.com/search/docs/appearance/title-link)・[スニペット](https://developers.google.com/search/docs/appearance/snippet)

GoogleのAI検索では、クロール可能性、一次情報、具体的な経験、役立つ画像を点検します。専用ファイルや独自の構造化データを導入条件にせず、確認したページと具体例を示します。Search Consoleの生成AIレポートを利用者が提供した場合は、対象面・期間と表示回数を記録します。専用レポートの表示回数を全体値に加算しないでください。未提供のクリック数・送客・問い合わせは「未計測」とします。[公式ガイド](https://developers.google.com/search/docs/fundamentals/ai-optimization-guide)・[専用レポート](https://developers.google.com/search/blog/2026/06/gen-ai-performance-reports)

集計ファイルに指名／非指名分類がある場合は、対象プロパティ・期間・国・端末をそろえて比較します。対象外プロパティで返る空の結果は未取得として扱います。[11月16日のSearch Analytics API更新](https://developers.google.com/search/blog/2026/11/search-analytics-api-update)

## 建設業での優先順位

「地域名 ＋ 工種」のキーワードが最も成約に近く、競合も限られます。またサイトのSEOより、**Googleビジネスプロフィールの最適化の方が短期的な効果が大きい**場合があります。優先順位の判断時に必ず考慮してください。

## 出力

- `<ドメイン>/SEO-AUDIT.md`（規則は `../market/references/output-location.md`）

## 他スキルとの連携

`MARKETING-AUDIT.md`、`LANDING-CRO.md` があれば突き合わせて判断します。
