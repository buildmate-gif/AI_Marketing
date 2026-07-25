---
name: market-proposal
description: "クライアント向けのマーケティング提案書を生成する。入力は会社名（URLがあれば精度向上）。「提案書を作って」「営業資料を作成して」「見積つきの提案がほしい」で使う。"
---
# クライアント提案書生成

## このスキルの目的

そのまま提出できる、プロ品質のマーケティング支援提案書を生成します。自社を「選ばれて当然の相手」として位置づけ、価格を段階提示（松竹梅）で見せ、投資対効果の試算で金額を正当化する提案書を作ります。

**出力言語はすべて日本語です。金額はすべて円建てで表記してください。**

## 使う場面

- 見込みクライアント向けの提案書を作りたいとき
- ヒアリングを終えて、内容を提案書に落とし込みたいとき
- 自社の提案書テンプレートが欲しいとき
- `/market proposal` または `/market proposal <会社名>` が実行されたとき

## 進め方

| 段階 | 内容 | 参照ファイル |
|---|---|---|
| 1 | 情報収集、提案書の全11章、フォロー、反論対応、契約条件 | `references/procedure.md` |
| 2 | CLIENT-PROPOSAL.md の書式 | `references/output-format.md` |

## 必ず守ること

- 現状分析は**すべて「機会」として提示する**。経営者の面子を潰す表現は致命的です
- 価格は松竹梅の3段階で提示し、真ん中に「おすすめ」を置く
- 投資対効果は保守的に見積もり、**効果発現まで3〜6ヶ月**を明記する
- 見積は税抜・税込を併記し、稟議用の1枚要約も用意する
- `MARKETING-AUDIT.md` があれば必ず取り込む。データに基づく提案書は成約率が2〜3倍になります

## 提出前の検証

この成果物はクライアントに渡るため、出力後に `market-critic` サブエージェントで検品してください。

1. 生成したファイルのパスと業種を `market-critic` に渡す
2. 5観点（具体性・数値根拠・実行可能性・日本語の自然さ・法令リスク）で採点される
3. 「不合格」なら指摘に沿って書き直し、再検証する（書き直しは2回まで）

手順の詳細は `../market/references/self-review.md` を参照してください。
検証を省略した場合は、その旨を必ずユーザーに伝えてください。

## HTML・PDFへの変換

検証に通った `CLIENT-PROPOSAL.md` は、`generate_proposal_pdf.py` でHTMLとPDFの両方に変換します。**HTMLファイルは中間生成物として消さず、共有用の成果物として残してください。**（PDFが開けない相手への代替、ブラウザでの手早い確認用）

スクリプトの場所は、導入方法によって置き場所が変わるため、実行前に次の2行でパスを解決してください。

```bash
MARKET_SCRIPTS="${CLAUDE_PLUGIN_ROOT:+$CLAUDE_PLUGIN_ROOT/skills/market/scripts}"
[ -d "$MARKET_SCRIPTS" ] || MARKET_SCRIPTS="$HOME/.claude/skills/market/scripts"

python3 "$MARKET_SCRIPTS/generate_proposal_pdf.py" \
  <ドメイン>/CLIENT-PROPOSAL.md <ドメイン>/CLIENT-PROPOSAL.pdf
```

Chromeが見つからない環境ではPDF変換のみ失敗しますが、HTMLは出力済みのため、その旨をユーザーに伝えてブラウザでの手動変換を案内してください。

## 出力

- `<ドメイン>/CLIENT-PROPOSAL.md`（規則は `../market/references/output-location.md`）
- `<ドメイン>/CLIENT-PROPOSAL.html`（共有用。削除しない）
- `<ドメイン>/CLIENT-PROPOSAL.pdf`
