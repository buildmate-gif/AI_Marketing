#!/usr/bin/env python3
"""マーケティングレポートをHTMLで生成し、任意でPDFへ変換する。

reportlab 版（generate_pdf_jp.py）よりデザイン自由度が高く、
競合比較ページと採点方法ページを含む全7セクションを出力する。

配色・書体は Hiro個人HTMLデザインルール（hiro-html-design）に準拠。
唯一 --hiro-alert（#B3453A）のみ、重要度「致命的」と40点未満のスコア表示のため
パレットに追加している。不要な場合は ALERT を --hiro-accent に置き換えること。

使い方:
  # HTMLのみ生成
  python3 generate_report_html.py data.json report.html

  # HTML生成後、Chrome でPDFへ変換
  python3 generate_report_html.py data.json report.html --pdf report.pdf
"""
import argparse
import html
import json
import shutil
import subprocess
import sys
from pathlib import Path

# --- 配色（hiro-html-design 準拠） -------------------------------------
PALETTE = {
    "bg": "#FCFBF7", "paper": "#ffffff", "text": "#1F2A44", "gray": "#5A6478",
    "brand": "#1F2A44", "accent": "#B99745", "blue": "#2563EB",
    "blueLight": "#EFF4FF", "border": "#E8E4DA", "highlight": "#FDF8EC",
    "alert": "#B3453A",  # パレットへの唯一の追加（致命的・危機的スコア専用）
}

GRADES = [(85, "A", "優秀"), (70, "B", "良好"), (55, "C", "平均的"),
          (40, "D", "平均以下"), (0, "F", "危機的")]

SEVERITY = {
    "critical": ("致命的", "alert"), "致命的": ("致命的", "alert"),
    "high": ("重大", "accent"), "重大": ("重大", "accent"),
    "medium": ("中程度", "blue"), "中程度": ("中程度", "blue"),
    "low": ("軽微", "gray"), "軽微": ("軽微", "gray"),
}


def grade(score):
    for th, letter, label in GRADES:
        if score >= th:
            return letter, label
    return "F", "危機的"


def score_color(score):
    if score >= 70:
        return PALETTE["blue"]
    if score >= 55:
        return PALETTE["brand"]
    if score >= 40:
        return PALETTE["accent"]
    return PALETTE["alert"]


def e(v):
    """HTMLエスケープ。Noneは空文字にする。"""
    return html.escape(str(v)) if v is not None else ""


def severity_badge(value):
    label, key = SEVERITY.get(str(value).strip().lower(), (str(value), "gray"))
    color = PALETTE[key]
    return (f'<span style="display:inline-block;background:{color};color:#fff;'
            f'font-size:11px;font-weight:700;padding:3px 12px;border-radius:3px;'
            f'letter-spacing:.05em;white-space:nowrap;">{e(label)}</span>')


def score_gauge(score):
    """総合スコアの円形ゲージ（インラインSVG）。"""
    color = score_color(score)
    circ = 2 * 3.14159 * 78
    dash = circ * min(max(score, 0), 100) / 100
    letter, label = grade(score)
    return f"""
<svg width="200" height="200" viewBox="0 0 200 200" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="総合スコア {score}点">
  <circle cx="100" cy="100" r="78" fill="none" stroke="{PALETTE['border']}" stroke-width="12"/>
  <circle cx="100" cy="100" r="78" fill="none" stroke="{color}" stroke-width="12"
          stroke-dasharray="{dash:.1f} {circ - dash:.1f}" stroke-linecap="round"
          transform="rotate(-90 100 100)"/>
  <text x="100" y="96" text-anchor="middle" font-family="Outfit, sans-serif"
        font-size="52" font-weight="700" fill="{PALETTE['brand']}">{score}</text>
  <text x="100" y="120" text-anchor="middle" font-family="Outfit, sans-serif"
        font-size="15" fill="{PALETTE['gray']}">/ 100</text>
  <text x="100" y="146" text-anchor="middle" font-family="Outfit, sans-serif"
        font-size="15" font-weight="700" fill="{color}">{letter} · {e(label)}</text>
</svg>"""


def bar_row(name, score, weight):
    color = score_color(score)
    return f"""
      <tr style="border-bottom:1px solid {PALETTE['border']};">
        <td style="padding:12px 16px;font-weight:500;white-space:nowrap;">{e(name)}</td>
        <td style="padding:12px 16px;width:100%;">
          <div style="background:{PALETTE['border']};height:9px;border-radius:5px;overflow:hidden;">
            <div style="background:{color};height:9px;width:{min(max(score,0),100)}%;border-radius:5px;"></div>
          </div>
        </td>
        <td style="padding:12px 16px;text-align:right;font-family:Outfit,sans-serif;
                   font-weight:700;color:{color};white-space:nowrap;">{score}</td>
        <td style="padding:12px 16px;text-align:right;color:{PALETTE['gray']};
                   font-size:13px;white-space:nowrap;">{e(weight)}</td>
      </tr>"""


def section(title, body, bg="bg", page_break=False):
    pb = "page-break-before:always;" if page_break else ""
    return f"""
<section style="background:var(--hiro-{bg});padding:44px 0;border-bottom:1px solid var(--hiro-border);{pb}">
  <div class="wrap">
    <h2>{e(title)}</h2>
    {body}
  </div>
</section>"""


def build_html(d):
    overall = int(d.get("overall_score", 0))
    letter, glabel = grade(overall)
    brand_name = d.get("brand_name", "").strip()
    cats = d.get("categories", {}) or {}

    # --- 表紙 ---
    title_line = f'<p class="lead-brand">{e(brand_name)} 御中</p>' if brand_name else ""
    cover = f"""
<section style="background:var(--hiro-paper);padding:56px 0 44px;border-bottom:1px solid var(--hiro-border);">
  <div class="wrap">
    <span class="badge">MARKETING AUDIT</span>
    <h1>マーケティング監査レポート</h1>
    {title_line}
    <p class="meta">対象URL： {e(d.get('url', '—'))}　／　発行日： {e(d.get('date', '—'))}</p>
    <div style="display:flex;gap:36px;align-items:center;flex-wrap:wrap;margin-top:28px;">
      <div>{score_gauge(overall)}</div>
      <div style="flex:1;min-width:280px;">
        <h3 style="margin-top:0;">エグゼクティブ・サマリー</h3>
        <p style="margin:0;">{e(d.get('executive_summary', ''))}</p>
      </div>
    </div>
  </div>
</section>"""

    # --- スコア内訳 ---
    rows = "".join(bar_row(k, int(v.get("score", 0)), v.get("weight", ""))
                   for k, v in cats.items())
    weighted = sum(int(v.get("score", 0)) * float(str(v.get("weight", "0")).rstrip("%") or 0) / 100
                   for v in cats.values())
    breakdown = f"""
    <table>
      <thead>
        <tr>
          <th style="text-align:left;">カテゴリ</th>
          <th style="text-align:left;">スコア</th>
          <th style="text-align:right;">点数</th>
          <th style="text-align:right;">ウェイト</th>
        </tr>
      </thead>
      <tbody>{rows}</tbody>
    </table>
    <div class="note">加重平均： <strong style="font-family:Outfit,sans-serif;">{weighted:.1f}</strong> ／ 100　（評価 {letter}・{e(glabel)}）</div>"""

    # --- 主要課題 ---
    findings = d.get("findings", []) or []
    if findings:
        frows = "".join(
            f"""<tr style="border-bottom:1px solid var(--hiro-border);">
                  <td style="padding:14px 16px;vertical-align:top;">{severity_badge(f.get('severity', ''))}</td>
                  <td style="padding:14px 16px;">{e(f.get('finding', ''))}</td>
                </tr>""" for f in findings)
        issues = f"""<table><thead><tr>
            <th style="text-align:left;width:110px;">重要度</th>
            <th style="text-align:left;">課題内容</th></tr></thead>
            <tbody>{frows}</tbody></table>"""
    else:
        issues = '<p class="note">課題は記録されていません。</p>'

    # --- アクションプラン ---
    plan_blocks = []
    for label, key, hint in [("クイックウィン", "quick_wins", "今週中・低工数"),
                             ("中期施策", "medium_term", "1〜3ヶ月"),
                             ("戦略施策", "strategic", "3〜6ヶ月")]:
        items = d.get(key, []) or []
        if not items:
            continue
        lis = "".join(f"<li>{e(i)}</li>" for i in items)
        plan_blocks.append(f"""
        <h3>{label}<span class="hint">{hint}</span></h3>
        <ol class="plan">{lis}</ol>""")
    plan = "".join(plan_blocks) or '<p class="note">施策は記録されていません。</p>'

    # --- 競合比較（reportlab版には無かった） ---
    comps = d.get("competitors", []) or []
    if comps:
        head = "".join(f'<th style="text-align:left;">{e(c.get("name", ""))}</th>' for c in comps)
        labels = [("positioning", "ポジショニング"), ("pricing", "価格帯"),
                  ("social_proof", "信頼シグナル"), ("content", "コンテンツ"),
                  ("reviews", "クチコミ"), ("map_rank", "地図検索順位")]
        body_rows = ""
        for key, jp in labels:
            if not any(c.get(key) for c in comps):
                continue
            cells = "".join(f'<td style="padding:12px 16px;">{e(c.get(key, "—"))}</td>' for c in comps)
            body_rows += (f'<tr style="border-bottom:1px solid var(--hiro-border);">'
                          f'<td style="padding:12px 16px;font-weight:500;white-space:nowrap;">{jp}</td>{cells}</tr>')
        competitors = f"""<table><thead><tr>
            <th style="text-align:left;">評価項目</th>{head}</tr></thead>
            <tbody>{body_rows}</tbody></table>
            <div class="note">競合データは調査時点のものです。取得できなかった項目は「—」と表示しています。</div>"""
    else:
        competitors = ('<p class="note">競合データは未取得です。'
                       '<code>/market competitors &lt;url&gt;</code> を実行すると本節が生成されます。</p>')

    # --- 採点方法（reportlab版には無かった） ---
    grade_rows = "".join(
        f'<tr style="border-bottom:1px solid var(--hiro-border);">'
        f'<td style="padding:10px 16px;font-family:Outfit,sans-serif;font-weight:700;">{lo}–{hi}</td>'
        f'<td style="padding:10px 16px;font-family:Outfit,sans-serif;font-weight:700;'
        f'color:{score_color(lo)};">{lt}</td>'
        f'<td style="padding:10px 16px;">{lb}</td></tr>'
        for (lo, lt, lb), hi in zip(GRADES, [100, 84, 69, 54, 39]))
    method = f"""
    <p>各カテゴリを0〜100点で採点し、ウェイトを掛けた加重平均を総合スコアとしています。</p>
    <table><thead><tr>
      <th style="text-align:left;">点数</th><th style="text-align:left;">評価</th>
      <th style="text-align:left;">意味</th></tr></thead>
      <tbody>{grade_rows}</tbody></table>
    <div class="callout">
      建設業は商談期間が数ヶ月〜1年に及びます。本レポートの改善提案は、
      実施から効果が数字に表れるまで通常3〜6ヶ月を要します。
      短期での判断は避け、四半期単位で評価してください。
    </div>
    <h3>本レポートの制約</h3>
    <ul>
      <li>スコアは公開情報にもとづく評価であり、実際の受注データとは異なります</li>
      <li>会員限定エリアなど非公開部分は評価対象外です</li>
      <li>収益試算に用いた単価・粗利率は、記載がない場合は業界標準値を使用しています</li>
    </ul>"""

    css = f"""
  :root {{
{chr(10).join(f'    --hiro-{k}: {v};' for k, v in PALETTE.items())}
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin:0; background:var(--hiro-bg); color:var(--hiro-text);
    font-family:'Noto Sans JP','Hiragino Sans','Yu Gothic',sans-serif;
    line-height:1.8; font-size:15px; -webkit-print-color-adjust:exact; print-color-adjust:exact;
  }}
  .wrap {{ max-width:900px; margin:0 auto; padding:0 32px; }}
  h1 {{ font-family:'Noto Serif JP','Hiragino Mincho ProN',serif; font-size:30px;
       font-weight:600; color:var(--hiro-brand); margin:14px 0 6px; line-height:1.5; }}
  h2 {{ font-family:'Noto Serif JP','Hiragino Mincho ProN',serif; font-size:22px;
       font-weight:600; color:var(--hiro-brand); border-left:4px solid var(--hiro-accent);
       padding-left:14px; margin:0 0 22px; }}
  h3 {{ font-size:17px; font-weight:700; color:var(--hiro-brand);
       border-bottom:1px solid var(--hiro-border); padding-bottom:8px; margin:28px 0 14px; }}
  .hint {{ font-size:12px; font-weight:400; color:var(--hiro-gray); margin-left:10px; }}
  .badge {{ display:inline-block; background:var(--hiro-accent); color:#fff; font-size:11px;
           font-weight:700; padding:3px 10px; border-radius:3px; letter-spacing:.08em;
           font-family:'Outfit',sans-serif; }}
  .lead-brand {{ font-family:'Noto Serif JP',serif; font-size:19px; color:var(--hiro-brand);
                margin:0 0 4px; }}
  .meta {{ color:var(--hiro-gray); font-size:13px; margin:0; }}
  table {{ width:100%; border-collapse:collapse; font-size:13.5px; margin:6px 0 4px;
          background:var(--hiro-paper); }}
  thead tr {{ border-bottom:2px solid var(--hiro-brand); }}
  th {{ padding:10px 16px; color:var(--hiro-gray); font-weight:500; font-size:12.5px;
       white-space:nowrap; }}
  ol.plan {{ padding-left:22px; margin:0 0 4px; }}
  ol.plan li {{ margin-bottom:9px; }}
  ul {{ padding-left:20px; }}
  .note {{ font-size:12.5px; color:var(--hiro-gray); margin-top:10px; }}
  .callout {{ background:var(--hiro-highlight); border-left:3px solid var(--hiro-accent);
             padding:14px 18px; font-size:13px; border-radius:0 6px 6px 0; margin:20px 0; }}
  code {{ background:var(--hiro-blueLight); color:var(--hiro-brand); padding:1px 6px;
         border-radius:3px; font-size:12.5px; }}
  footer {{ padding:26px 0 34px; text-align:center; color:var(--hiro-gray); font-size:12px; }}
  @page {{ size:A4; margin:14mm; }}
  @media print {{
    section {{ padding:26px 0 !important; }}
    .wrap {{ padding:0 !important; }}
    table, ol.plan {{ page-break-inside:avoid; }}
    h2, h3 {{ page-break-after:avoid; }}
  }}"""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>マーケティング監査レポート{' — ' + e(brand_name) if brand_name else ''}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&family=Noto+Serif+JP:wght@600&family=Outfit:wght@400;700&display=swap" rel="stylesheet">
<style>{css}</style>
</head>
<body>
{cover}
{section('スコア内訳', breakdown, 'bg')}
{section('主要課題', issues, 'paper', page_break=True)}
{section('優先度別アクションプラン', plan, 'bg')}
{section('競合比較', competitors, 'paper', page_break=True)}
{section('採点方法と制約', method, 'bg')}
<footer>AI Marketing Suite — <code>/market report-pdf</code> により生成</footer>
</body>
</html>"""


CHROME_PATHS = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]


def find_chrome():
    for p in CHROME_PATHS:
        if Path(p).exists():
            return p
    for name in ("google-chrome", "chromium", "chromium-browser", "microsoft-edge"):
        found = shutil.which(name)
        if found:
            return found
    return None


def to_pdf(html_path, pdf_path):
    chrome = find_chrome()
    if not chrome:
        print("Chrome が見つかりません。HTMLをブラウザで開き、"
              "「印刷 → PDFとして保存」で変換してください。", file=sys.stderr)
        return False
    cmd = [chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
           "--no-pdf-header-footer", "--virtual-time-budget=8000",
           f"--print-to-pdf={Path(pdf_path).resolve()}",
           Path(html_path).resolve().as_uri()]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0 or not Path(pdf_path).exists():
        print(f"PDF変換に失敗しました。\n{r.stderr[:400]}", file=sys.stderr)
        return False
    return True


def main():
    ap = argparse.ArgumentParser(description="HTMLマーケティングレポートを生成する")
    ap.add_argument("json_path", help="レポートデータのJSON")
    ap.add_argument("html_path", help="出力するHTMLのパス")
    ap.add_argument("--pdf", help="PDFにも変換する場合の出力先")
    args = ap.parse_args()

    with open(args.json_path, encoding="utf-8") as f:
        data = json.load(f)

    Path(args.html_path).write_text(build_html(data), encoding="utf-8")
    print(f"HTMLを出力しました: {args.html_path}")

    if args.pdf:
        if to_pdf(args.html_path, args.pdf):
            size = Path(args.pdf).stat().st_size
            print(f"PDFを出力しました: {args.pdf}（{size:,} バイト）")
        else:
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
