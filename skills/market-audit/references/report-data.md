# 監査から顧客向けレポートへの受け渡し

診断のたびに同じ案件フォルダへ `REPORT-DATA.json` を UTF-8 で保存する。対象ドメインと日付を確認し、今回の観察で古い情報を更新する。既存の施策ID・実施状況は前回の同じ施策から引き継ぎ、新しい施策には未使用のIDを付ける。変更前に `MARKET-HISTORY.json` がある場合は前回のIDと実績を参照する。

基本項目は `url, brand_name, date, executive_summary, categories, overall_score, findings, quick_wins, medium_term, strategic, competitors`。各カテゴリは `{"score": 60, "weight": "25%"}` の形で、監査の6カテゴリと配点を使用する。評価材料が欠けたカテゴリは `score: null`、その場合は `overall_score: null` とし、サマリーで理由を書く。全項目がそろった場合は加重平均を四捨五入して総合点とする。主要課題には `severity, finding`、競合には名称と確認できた項目だけを入れる。業種が建設・建築業と判定された案件では `"industry": "建設・建築業"` を加える。レポートに効果発現までの期間の説明が載る。

`priority_actions` は影響・根拠・着手のしやすさを考慮した順に最大3件。確認できた件数だけ記載する。各項目の形は次の通り。

```json
{
  "id": "A01",
  "title": "施工事例の末尾に相談窓口を置く",
  "status": "予定",
  "page_url": "https://example.com/works/",
  "checked_on": "2026-11-19",
  "evidence": "確認した事例4件の本文末には一覧へ戻るリンクだけがある。",
  "hypothesis": "事例を読み終えた人が相談先を探す手間を減らせる。",
  "change": "事例テンプレートの末尾に「同じ工事を相談する」リンクを置く。",
  "metric": "事例から相談フォームへ進んだセッション数",
  "baseline": null,
  "period": null
}
```

例は架空。実案件では対象URL・観察日・観察内容を実際に確認した値にする。状態は「予定」「進行中」「実施済」「未確認」のいずれか。担当が確認できた範囲で記録する。指標の `baseline` には単位付きの値を入れ、`period` に期間・集計元を明記する。計測できていない値は null、測定結果が0のときだけ0を書く。金額の仮定を実績に入れない。

`MARKETING-AUDIT.md` と同じ根拠・施策を使って、次を実行する。`case_dir` は出力先規則に沿って作成済みの対象ドメインフォルダのパスを設定しておく。

```bash
MARKET_SCRIPTS="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/market/scripts}"
[ -d "$MARKET_SCRIPTS" ] || MARKET_SCRIPTS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/skills/market/scripts"
python3 "$MARKET_SCRIPTS/generate_report_html.py" "$case_dir/REPORT-DATA.json" "$case_dir/MARKETING-REPORT.html"
```

顧客に渡すHTMLを開き、上位施策、該当URL、未計測の表示を確認する。次回の `/market track` では同じ施策IDと指標名で実施状況と実績を記録する。
