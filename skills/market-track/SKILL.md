---
name: market-track
description: "前回の診断と今回の変化を比較する。「前回と比べて」「改善できたか」「効果を測定して」「定期レポート」で使う。施策の実施状況、診断スコア、根拠付き実測値を案件別に追跡する。"
---
# 定点観測

`/market track <url>` で、同一ドメインの施策、スコア、成果指標を日本語で報告する。

1. 対象ドメインの履歴、監査、`REPORT-DATA.json` があれば読む。手順は `references/procedure.md`。
2. 現在の監査結果と既存の作業記録・解析資料を使う。問い合わせ件数、受注数など未提供の数字は `null` として「未計測」と表示する。
3. 優先施策の ID を再利用し、実施状況と確認根拠を記録する。施策の提案と実施を区別する。
4. `record` が成功した後、`report` の出力と `references/output-format.md` に従い、`report <案件フォルダ>/MARKET-HISTORY.json --html <案件フォルダ>/TRACK-REPORT.html` を実行する。標準出力で案件フォルダの `TRACK-REPORT.md` を作成し、同時に出力される `TRACK-REPORT.html` を顧客向け月次画面として案内する。次回も同じ `MARKET-HISTORY.json` を使用する。

```bash
MARKET_SCRIPTS="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/market/scripts}"
[ -d "$MARKET_SCRIPTS" ] || MARKET_SCRIPTS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/market/scripts"
```

初回は基準値を報告する。2回目以降は `python3 "$MARKET_SCRIPTS/track_history.py" diff <案件フォルダ>/MARKET-HISTORY.json` で確認する。比較できない指標は理由を添える。問い合わせの数やスコアが動いた場合、実施した日や需要の季節性などを確認し、施策への因果帰属は検証方法に見合う範囲で記述する。
