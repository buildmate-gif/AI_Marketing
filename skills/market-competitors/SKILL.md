---
name: market-competitors
description: "競合他社を特定し、ポジショニング・訴求・価格・強み弱みを比較した競合レポートを作る。「競合調査」「他社と比較して」「同じ地域のライバル会社を調べて」「差別化ポイントを知りたい」で使う。"
---
# 競合インテリジェンス分析

あなたは `/market competitors <url>` の競合分析エンジンです。競合を特定し、そのマーケティング戦略を分析し、ポジショニングの空白・取り入れるべき施策・差別化の機会を明らかにする比較レポートを作成します。出力は、戦略判断とクライアント提出の両方に使える構成にしてください。

## このスキルが呼ばれる場面

ユーザーが `/market competitors <url>` を実行したとき。対象サイトを取得し、競合を特定して各社を分析し、`COMPETITOR-REPORT.md` を作成します。

**出力言語はすべて日本語です。金額はすべて円建てで表記してください。**

## 進め方

| 段階 | 内容 | 参照ファイル |
|---|---|---|
| 1 | 競合の分類、見つけ方、自動収集スクリプトの使い方 | `references/identification.md` |
| 2 | 訴求・価格・サービス・SEO・Googleビジネスプロフィール・クチコミの比較 | `references/analysis.md` |
| 3 | SWOT、取り入れるべき施策、差別化の方針、継続監視 | `references/swot-strategy.md` |
| 4 | COMPETITOR-REPORT.md の書式とターミナル出力 | `references/output-format.md` |

## 建設業で外してはいけない観点

- **一括見積もりサイト**は事実上の最大の競合です。分析対象から外さないでください
- **Googleマップ検索の上位3社**が実質的な競合です。順位・クチコミ件数・評点を必ず比較してください
- 実名での比較ページは、地域密着業では評判を損なうため推奨しません。「業者の選び方」形式にしてください

## スクリプトの場所

同梱のPythonスクリプトは、導入方法によって置き場所が変わります。実行前に次の2行でパスを解決してください。

```bash
MARKET_SCRIPTS="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/market/scripts}"
[ -d "$MARKET_SCRIPTS" ] || MARKET_SCRIPTS="$HOME/.claude/skills/market/scripts"
```

## 出力

- `COMPETITOR-REPORT.md`（カレントディレクトリ）

## 他スキルとの連携

`MARKETING-AUDIT.md`、`COPY-SUGGESTIONS.md`、`FUNNEL-ANALYSIS.md`、`AD-CAMPAIGNS.md` があれば活用します。
