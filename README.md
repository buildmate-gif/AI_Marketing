<p align="center">
  <img src="banner.svg" alt="AI Marketing Suite for Claude Code" width="100%">
</p>

# AI マーケティング for Claude Code（日本語版）

[Claude Code](https://docs.anthropic.com/en/docs/claude-code) 向けの包括的なマーケティング分析・自動化スキルシステムです。ウェブサイトのマーケティング監査、コピー生成、メールシーケンス作成、コンテンツカレンダー作成、競合分析、クライアント向けPDFレポート作成まで、すべてターミナルから実行できます。

**AIを活用したマーケティングサービスを提供したい、起業家・エージェンシービルダー・ソロプレナー向けのツールです。**

> 本リポジトリは [zubair-trabzada/ai-marketing-claude](https://github.com/zubair-trabzada/ai-marketing-claude) を日本語化・日本市場向けにカスタマイズしたものです。

---

## できること

Claude Code でコマンドを入力するだけで、即座に実用的なマーケティング分析を取得できます：

```
> /market audit https://example-kensetsu.co.jp

5つのエージェントを起動中...
✓ コンテンツ・メッセージング分析     — スコア：72/100
✓ コンバージョン最適化               — スコア：58/100
✓ SEO・発見可能性                    — スコア：81/100
✓ 競合ポジショニング                  — スコア：64/100
✓ ブランド・信頼性                    — スコア：76/100
✓ 成長・戦略                          — スコア：61/100

総合マーケティングスコア：69/100

詳細レポートを MARKETING-AUDIT.md に保存しました
```

---

## インストール

### ワンコマンドでインストール

```bash
curl -fsSL https://raw.githubusercontent.com/buildmate-gif/ai-marketing-claude-jp/main/install.sh | bash
```

### 手動インストール

```bash
git clone https://github.com/buildmate-gif/ai-marketing-claude-jp.git
cd ai-marketing-claude-jp
./install.sh
```

### オプション：PDFレポート機能を使う場合

```bash
pip install reportlab
```

---

## コマンド一覧

| コマンド | 内容 |
|---------|------|
| `/market audit <url>` | 5つの並列エージェントによる完全マーケティング監査 |
| `/market quick <url>` | 60秒のマーケティングスナップショット |
| `/market copy <url>` | 改善前・改善後付き最適化コピー生成 |
| `/market emails <topic>` | メールシーケンス一式生成 |
| `/market social <topic>` | 30日間SNSコンテンツカレンダー |
| `/market ads <url>` | 各プラットフォーム向け広告クリエイティブ |
| `/market funnel <url>` | 営業ファネルの分析・最適化 |
| `/market competitors <url>` | 競合インテリジェンスレポート |
| `/market landing <url>` | ランディングページCRO分析 |
| `/market launch <product>` | ローンチプレイブック生成 |
| `/market proposal <client>` | クライアント提案書自動生成 |
| `/market report <url>` | マーケティングレポート（Markdown） |
| `/market report-pdf <url>` | プロ仕様マーケティングレポート（PDF） |
| `/market seo <url>` | SEOコンテンツ監査 |
| `/market brand <url>` | ブランドボイス分析・ガイドライン |

---

## スコアリング方式

| カテゴリ | ウェイト | 評価内容 |
|---------|--------|---------|
| コンテンツ・メッセージング | 25% | コピー品質・価値提案・ヘッドライン・CTA |
| コンバージョン最適化 | 20% | ファネル・フォーム・社会的証明・摩擦・緊急性 |
| SEO・発見可能性 | 20% | オンページSEO・テクニカルSEO・コンテンツ構造 |
| 競合ポジショニング | 15% | 差別化・市場認知・代替サービスページ |
| ブランド・信頼性 | 10% | デザイン品質・信頼シグナル・権威性 |
| 成長・戦略 | 10% | 価格設定・集客チャネル・リテンション |

**総合マーケティングスコア** = 全カテゴリの加重平均（0〜100点）

---

## アンインストール

```bash
./uninstall.sh
```

または手動で：

```bash
rm -rf ~/.claude/skills/market*
rm -f ~/.claude/agents/market-*.md
```

---

## ライセンス

MITライセンス — 詳細は [LICENSE](LICENSE) をご覧ください。
